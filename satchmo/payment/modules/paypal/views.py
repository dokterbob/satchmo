from django.core import urlresolvers
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _
from satchmo.configuration import config_value, config_get_group
from satchmo.contact.models import Order
from satchmo.payment.common.views import payship
from satchmo.payment.config import payment_live
from satchmo.payment.urls import lookup_url, lookup_template
from satchmo.shop.models import Cart

import logging

log = logging.getLogger('paypal.views')

def pay_ship_info(request):
    return payship.simple_pay_ship_info(request, config_get_group('PAYMENT_PAYPAL'), 'checkout/paypal/pay_ship.html')

def confirm_info(request):
    payment_module = config_get_group('PAYMENT_PAYPAL')

    if not request.session.get('orderID'):
        url = lookup_url(payment_module, 'satchmo_checkout-step1')
        return HttpResponseRedirect(url)

    if request.session.get('cart'):
        tempCart = Cart.objects.get(id=request.session['cart'])
        if tempCart.numItems == 0:
            template = lookup_template(payment_module, 'checkout/empty_cart.html')
            return render_to_response(template, RequestContext(request))
    else:
        template = lookup_template(payment_module, 'checkout/empty_cart.html')
        return render_to_response(template, RequestContext(request))

    order = Order.objects.get(id=request.session['orderID'])

    # Check if the order is still valid
    if not order.validate(request):
        context = RequestContext(request,
            {'message': _('Your order is no longer valid.')})
        return render_to_response('shop_404.html', context)

    template = lookup_template(payment_module, 'checkout/paypal/confirm.html')
    if payment_module.LIVE.value:
        log.debug("live order on %s", payment_module.KEY.value)
        url = payment_module.POST_URL.value
        account = payment_module.BUSINESS.value
    else:
        url = payment_module.POST_TEST_URL.value
        account = payment_module.BUSINESS_TEST.value
        
    try:
        address = lookup_url(payment_module, payment_module.RETURN_ADDRESS.value, include_server=True)
    except urlresolvers.NoReverseMatch:
        address = payment_module.RETURN_ADDRESS.value
        
    ctx = RequestContext(request, {'order': order,
     'post_url': url,
     'business': account,
     'currency_code': payment_module.CURRENCY_CODE.value,
     'return_address': address,
     'PAYMENT_LIVE' : payment_live(payment_module)
    })

    return render_to_response(template, ctx)

