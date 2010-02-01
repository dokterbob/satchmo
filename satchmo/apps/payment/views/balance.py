from datetime import datetime, timedelta
from decimal import Decimal
from django.core import urlresolvers
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from livesettings import config_get_group, config_value
from payment import active_gateways
from payment.forms import PaymentMethodForm, CustomChargeForm
from payment.views import contact
from satchmo_store.shop.models import Order, OrderItem, OrderPayment
from satchmo_utils.dynamic import lookup_url
from satchmo_utils.views import bad_or_missing
import logging

log = logging.getLogger('payment.views.balance')

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
        form = PaymentMethodForm(data=new_data, order=order)
        if form.is_valid():
            data = form.cleaned_data
            modulename = data['paymentmethod']
            if not modulename.startswith('PAYMENT_'):
                modulename = 'PAYMENT_' + modulename
            
            paymentmodule = config_get_group(modulename)
            url = lookup_url(paymentmodule, 'satchmo_checkout-step2')
            return HttpResponseRedirect(url)
        
    else:
        form = PaymentMethodForm(order=order)
        
    ctx = RequestContext(request, {'form' : form, 
        'order' : order,
        'paymentmethod_ct': len(active_gateways())
    })
    return render_to_response('shop/checkout/balance_remaining.html',
                              context_instance=ctx)


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
    return render_to_response('payment/admin/charge_remaining_confirm.html',
                              context_instance=ctx)

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
        ctx = RequestContext(request, {'form': form})
        return render_to_response('admin/charge_remaining_confirm.html',
                                  context_instance=ctx)
