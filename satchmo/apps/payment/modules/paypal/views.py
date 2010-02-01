from decimal import Decimal
from django.core import urlresolvers
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.http import urlencode
from django.utils.translation import ugettext as _
from django.views.decorators.cache import never_cache
from livesettings import config_get_group, config_value 
from payment.config import gateway_live
from payment.utils import get_processor_by_key
from payment.views import payship
from satchmo_store.shop.models import Cart
from satchmo_store.shop.models import Order, OrderPayment
from satchmo_utils.dynamic import lookup_url, lookup_template
from sys import exc_info
from traceback import format_exception
import logging
import urllib2

log = logging.getLogger()

def pay_ship_info(request):
    return payship.base_pay_ship_info(request,
        config_get_group('PAYMENT_PAYPAL'), payship.simple_pay_ship_process_form,
        'shop/checkout/paypal/pay_ship.html')
pay_ship_info = never_cache(pay_ship_info)


def confirm_info(request):
    payment_module = config_get_group('PAYMENT_PAYPAL')

    try:
        order = Order.objects.from_request(request)
    except Order.DoesNotExist:
        url = lookup_url(payment_module, 'satchmo_checkout-step1')
        return HttpResponseRedirect(url)

    tempCart = Cart.objects.from_request(request)
    if tempCart.numItems == 0 and not order.is_partially_paid:
        template = lookup_template(payment_module, 'shop/checkout/empty_cart.html')
        return render_to_response(template,
                                  context_instance=RequestContext(request))

    # Check if the order is still valid
    if not order.validate(request):
        context = RequestContext(request,
                                 {'message': _('Your order is no longer valid.')})
        return render_to_response('shop/404.html', context_instance=context)

    template = lookup_template(payment_module, 'shop/checkout/paypal/confirm.html')
    if payment_module.LIVE.value:
        log.debug("live order on %s", payment_module.KEY.value)
        url = payment_module.POST_URL.value
        account = payment_module.BUSINESS.value
    else:
        url = payment_module.POST_TEST_URL.value
        account = payment_module.BUSINESS_TEST.value

    try:
        address = lookup_url(payment_module,
            payment_module.RETURN_ADDRESS.value, include_server=True)
    except urlresolvers.NoReverseMatch:
        address = payment_module.RETURN_ADDRESS.value
    
    processor_module = payment_module.MODULE.load_module('processor')
    processor = processor_module.PaymentProcessor(payment_module)
    processor.create_pending_payment(order=order)
    default_view_tax = config_value('TAX', 'DEFAULT_VIEW_TAX') 
  
    recurring = None
    order_items = order.orderitem_set.all()
    for item in order_items:
        if item.product.is_subscription:
            recurring = {'product':item.product, 'price':item.product.price_set.all()[0].price.quantize(Decimal('.01')),}
            trial0 = recurring['product'].subscriptionproduct.get_trial_terms(0)
            if len(order_items) > 1 or trial0 is not None or recurring['price'] < order.balance:
                recurring['trial1'] = {'price': order.balance,}
                if trial0 is not None:
                    recurring['trial1']['expire_length'] = trial0.expire_length
                    recurring['trial1']['expire_unit'] = trial0.expire_unit[0]
                # else:
                #     recurring['trial1']['expire_length'] = recurring['product'].subscriptionproduct.get_trial_terms(0).expire_length
                trial1 = recurring['product'].subscriptionproduct.get_trial_terms(1)
                if trial1 is not None:
                    recurring['trial2']['expire_length'] = trial1.expire_length
                    recurring['trial2']['expire_unit'] = trial1.expire_unit[0]
                    recurring['trial2']['price'] = trial1.price
 
    ctx = RequestContext(request, {'order': order,
     'post_url': url,
     'default_view_tax': default_view_tax, 
     'business': account,
     'currency_code': payment_module.CURRENCY_CODE.value,
     'return_address': address,
     'invoice': order.id,
     'subscription': recurring,
     'PAYMENT_LIVE' : gateway_live(payment_module)
    })

    return render_to_response(template, context_instance=ctx)
confirm_info = never_cache(confirm_info)

def ipn(request):
    """PayPal IPN (Instant Payment Notification)
    Cornfirms that payment has been completed and marks invoice as paid.
    Adapted from IPN cgi script provided at http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/456361"""
    payment_module = config_get_group('PAYMENT_PAYPAL')
    if payment_module.LIVE.value:
        log.debug("Live IPN on %s", payment_module.KEY.value)
        url = payment_module.POST_URL.value
        account = payment_module.BUSINESS.value
    else:
        log.debug("Test IPN on %s", payment_module.KEY.value)
        url = payment_module.POST_TEST_URL.value
        account = payment_module.BUSINESS_TEST.value
    PP_URL = url

    try:
        data = request.POST
        log.debug("PayPal IPN data: " + repr(data))
        if not confirm_ipn_data(data, PP_URL):
            return HttpResponse()

        if not 'payment_status' in data or not data['payment_status'] == "Completed":
            # We want to respond to anything that isn't a payment - but we won't insert into our database.
             log.info("Ignoring IPN data for non-completed payment.")
             return HttpResponse()

        try:
            invoice = data['invoice']
        except:
            invoice = data['item_number']

        gross = data['mc_gross']
        txn_id = data['txn_id']

        if not OrderPayment.objects.filter(transaction_id=txn_id).count():
            # If the payment hasn't already been processed:
            order = Order.objects.get(pk=invoice)
            
            order.add_status(status='New', notes=_("Paid through PayPal."))
            processor = get_processor_by_key('PAYMENT_PAYPAL')
            payment = processor.record_payment(order=order, amount=gross, transaction_id=txn_id)
            
            if 'memo' in data:
                if order.notes:
                    notes = order.notes + "\n"
                else:
                    notes = ""
                
                order.notes = notes + _('---Comment via Paypal IPN---') + u'\n' + data['memo']
                order.save()
                log.debug("Saved order notes from Paypal")
            
            for item in order.orderitem_set.filter(product__subscriptionproduct__recurring=True, completed=False):
                item.completed = True
                item.save()
            for cart in Cart.objects.filter(customer=order.contact):
                cart.empty()
                
    except:
        log.exception(''.join(format_exception(*exc_info())))

    return HttpResponse()

def confirm_ipn_data(data, PP_URL):
    # data is the form data that was submitted to the IPN URL.

    newparams = {}
    for key in data.keys():
        newparams[key] = data[key]

    newparams['cmd'] = "_notify-validate"
    params = urlencode(newparams)

    req = urllib2.Request(PP_URL)
    req.add_header("Content-type", "application/x-www-form-urlencoded")
    fo = urllib2.urlopen(req, params)

    ret = fo.read()
    if ret == "VERIFIED":
        log.info("PayPal IPN data verification was successful.")
    else:
        log.info("PayPal IPN data verification failed.")
        log.debug("HTTP code %s, response text: '%s'" % (fo.code, ret))
        return False

    return True
