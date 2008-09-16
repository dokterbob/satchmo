import logging
from django import forms
from django.core import urlresolvers
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from satchmo.configuration import config_get_group, config_value
from satchmo.shop.models import Order, OrderItem, OrderPayment
from satchmo.payment.decorators import cart_has_minimum_order
from satchmo.payment.common.forms import PaymentMethodForm
from satchmo.payment.common.views import common_contact
from satchmo.shop.views.utils import bad_or_missing
from satchmo.utils.dynamic import lookup_url

try:
    from decimal import Decimal
except:
    from django.utils._decimal import Decimal

log = logging.getLogger('payment.views')

class CustomChargeForm(forms.Form):
    orderitem = forms.IntegerField(required=True, widget=forms.HiddenInput())
    amount = forms.DecimalField(label=_('New price'), required=False)
    shipping = forms.DecimalField(label=_('Shipping adjustment'), required=False)
    notes = forms.CharField(_("Notes"), required=False, initial="Your custom item is ready.")

# Create your views here.
from datetime import datetime, timedelta

def cron_rebill(request=None):
    """Rebill customers with expiring recurring subscription products
    This can either be run via a url with GET key authentication or
    directly from a shell script.
    """
    #TODO: support re-try billing for failed transactions

    if request is not None:
        if not config_value('PAYMENT', 'ALLOW_URL_REBILL'):
            return bad_or_missing(request, _("Feature is not enabled."))
        if 'key' not in request.GET or request.GET['key'] != config_value('PAYMENT','CRON_KEY'):
            return HttpResponse("Authentication Key Required")

    expiring_subscriptions = OrderItem.objects.filter(expire_date__gte=datetime.now()).order_by('order', 'id', 'expire_date')
    for item in expiring_subscriptions:
        if item.product.is_subscription:#TODO - need to add support for products with trial but non-recurring
            if item.product.subscriptionproduct.recurring_times and item.product.subscriptionproduct.recurring_times + item.product.subscriptionproduct.get_trial_terms().count() == OrderItem.objects.filter(order=item.order, product=item.product).count():
                continue
            if item.expire_date == datetime.date(datetime.now()) and item.completed:
                if item.id == OrderItem.objects.filter(product=item.product, order=item.order).order_by('-id')[0].id:
                    #bill => add orderitem, recalculate total, porocess card
                    new_order_item = OrderItem(order=item.order, product=item.product, quantity=item.quantity, unit_price=item.unit_price, line_item_price=item.line_item_price)
                    #if product is recuring, set subscription end
                    if item.product.subscriptionproduct.recurring:
                        new_order_item.expire_date = datetime.now() + timedelta(days=item.product.subscriptionproduct.expire_days)
                    #check if product has 2 or more trial periods and if the last one paid was a trial or a regular payment.
                    ordercount = item.order.orderitem_set.all().count()
                    if item.product.subscriptionproduct.get_trial_terms().count() > 1 and item.unit_price == item.product.subscriptionproduct.get_trial_terms(ordercount - 1).price:
                        new_order_item.unit_price = item.product.subscriptionproduct.get_trial.terms(ordercount).price
                        new_order_item.line_item_price = new_order_item.quantity * new_order_item.unit_price
                        new_order_item.expire_date = datetime.datetime.now() + datetime.timedelta(days=item.product.subscriptionproduct.get_trial_terms(ordercount).expire_days)
                    new_order_item.save()
                    item.order.recalculate_total()
#                    if new_order_item.product.subscriptionproduct.is_shippable == 3:
#                        item.order.total = item.order.total - item.order.shipping_cost
#                        item.order.save()
                    payments = item.order.payments.all()[0]
                    #list of ipn based payment modules.  Include processors that use 3rd party recurring billing.
                    ipn_based = ['PAYPAL']
                    if not payments.payment in ipn_based and item.order.balance > 0:
                        #run card
                        #Do the credit card processing here & if successful, execute the success_handler
                        from satchmo.configuration import config_get_group
                        payment_module = config_get_group('PAYMENT_%s' % payments.payment)
                        credit_processor = payment_module.MODULE.load_module('processor')
                        processor = credit_processor.PaymentProcessor(payment_module)
                        processor.prepareData(item.order)
                        results, reason_code, msg = processor.process()
        
                        log.info("""Processing %s recurring transaction with %s
                            Order #%i
                            Results=%s
                            Response=%s
                            Reason=%s""", payment_module.LABEL.value, payment_module.KEY.value, item.order.id, results, reason_code, msg)

                        if results:
                            #success handler
                            item.order.add_status(status='Pending', notes = "Subscription Renewal Order successfully submitted")
                            new_order_item.completed = True
                            new_order_item.save()
                            orderpayment = OrderPayment(order=item.order, amount=item.order.balance, payment=unicode(payment_module.KEY.value))
                            orderpayment.save()
    return HttpResponse()


def balance_remaining_order(request, order_id=None):
    """Load the order into the session, so we can charge the remaining amount"""
    # this will create an "OrderCart" - a fake cart to allow us to check out
    request.session['cart'] = 'order'
    request.session['orderID'] = order_id
    return balance_remaining(request)

def balance_remaining(request):
    """Allow the user to pay the remaining balance."""
    order = None
    orderid = request.session.get('orderID')
    if orderid:
        try:
            order = Order.objects.get(pk=orderid)
        except Order.DoesNotExist:
            # TODO: verify user against current user
            pass
            
    if not order:
        url = urlresolvers.reverse('satchmo_checkout-step1')
        return HttpResponseRedirect(url)

    if request.method == "POST":
        new_data = request.POST.copy()
        form = PaymentMethodForm(new_data)
        if form.is_valid():
            data = form.cleaned_data
            modulename = data['paymentmethod']
            if not modulename.startswith('PAYMENT_'):
                modulename = 'PAYMENT_' + modulename
            
            paymentmodule = config_get_group(modulename)
            url = lookup_url(paymentmodule, 'satchmo_checkout-step2')
            return HttpResponseRedirect(url)
        
    else:
        form = PaymentMethodForm()
        
    ctx = RequestContext(request, {'form' : form, 
        'order' : order,
        'paymentmethod_ct': len(config_value('PAYMENT', 'MODULES'))
    })
    return render_to_response('checkout/balance_remaining.html', ctx)
    
    
def _contact_info(request):
    return common_contact.contact_info(request)

contact_info = cart_has_minimum_order()(_contact_info)

def charge_remaining(request, orderitem_id):
    """Given an orderitem_id, this returns a confirmation form."""
    
    try:
        orderitem = OrderItem.objects.get(pk = orderitem_id)
    except OrderItem.DoesNotExist:
        return bad_or_missing(request, _("The orderitem you have requested doesn't exist, or you don't have access to it."))
        
    amount = orderitem.product.customproduct.full_price
        
    data = {
        'orderitem' : orderitem_id,
        'amount' : amount,
        }
    form = CustomChargeForm(data)
    ctx = RequestContext(request, {'form' : form})
    return render_to_response('admin/charge_remaining_confirm.html', ctx)
    
def charge_remaining_post(request):
    if not request.method == 'POST':
        return bad_or_missing(request, _("No form found in request."))
    
    data = request.POST.copy()
    
    form = CustomChargeForm(data)
    if form.is_valid():
        data = form.cleaned_data
        try:
            orderitem = OrderItem.objects.get(pk = data['orderitem'])
        except OrderItem.DoesNotExist:
            return bad_or_missing(request, _("The orderitem you have requested doesn't exist, or you don't have access to it."))
        
        price = data['amount']
        line_price = price*orderitem.quantity
        orderitem.unit_price = price
        orderitem.line_item_price = line_price
        orderitem.save()
        #print "Orderitem price now: %s" % orderitem.line_item_price
        
        order = orderitem.order
    
        if not order.shipping_cost:
            order.shipping_cost = Decimal("0.00")
    
        if data['shipping']:
            order.shipping_cost += data['shipping']
            
        order.recalculate_total()
        
        request.user.message_set.create(message='Charged for custom product and recalculated totals.')

        notes = data['notes']
        if not notes:
            notes = 'Updated total price'
            
        order.add_status(notes=notes)
        
        return HttpResponseRedirect('/admin/shop/order/%i' % order.id)
    else:
        ctx = RequestContext(request, {'form' : form})
        return render_to_response('admin/charge_remaining_confirm.html', ctx)

