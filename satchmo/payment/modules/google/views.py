from django import http
from django.shortcuts import render_to_response
from django.template import RequestContext, Context
from django.template.loader import get_template
from django.utils.translation import ugettext as _
from satchmo.configuration import config_get_group
from satchmo.contact.models import Order
from satchmo.payment.common.views import payship
from satchmo.payment.config import payment_live
from satchmo.shop.utils.dynamic import lookup_url, lookup_template
from satchmo.shop.models import Cart
import base64
import hmac
import logging
import sha

log = logging.getLogger("payment.modules.google.processor")

class GoogleCart(object):
    def __init__(self, order, payment_module, live):
        self.settings = payment_module
        self.cart_xml = self._cart_xml(order)
        self.signature = self._signature(live)

    def _cart_xml(self, order):
        template = get_template(self.settings["CART_XML_TEMPLATE"].value)

        shopping_url = lookup_url(self.settings, 'satchmo_checkout-success', True, self.settings.SSL.value)
        edit_url = lookup_url(self.settings, 'satchmo_cart', True, self.settings.SSL.value)
        ctx = Context({"order" : order,
                       "continue_shopping_url" : shopping_url,
                       "edit_cart_url" : edit_url,
                       "currency" : self.settings.CURRENCY_CODE.value,
                       })
        return template.render(ctx)

    def _signature(self, live):
        if live:
            merchkey = self.settings.MERCHANT_KEY.value
        else:
            merchkey = self.settings.MERCHANT_TEST_KEY.value

        s = hmac.new(merchkey, self.cart_xml, sha)
        rawsig = s.digest()
        return rawsig

    def encoded_cart(self):
        return base64.encodestring(self.cart_xml)[:-1]

    def encoded_signature(self):
        sig = base64.encodestring(self.signature)[:-1]
        log.debug("Sig is: %s", sig)
        return sig

def pay_ship_info(request):
    return payship.simple_pay_ship_info(request, config_get_group('PAYMENT_GOOGLE'), 'checkout/google/pay_ship.html')

def confirm_info(request):
    payment_module = config_get_group('PAYMENT_GOOGLE')

    if not 'orderID' in request.session:
        url = lookup_url(payment_module, 'satchmo_checkout-step1')
        return http.HttpResponseRedirect(url)

    tempCart = Cart.objects.from_request(request)
    if tempCart.numItems == 0:
        template = lookup_template(payment_module, 'checkout/empty_cart.html')
        return render_to_response(template, RequestContext(request))
            
    try:
        order = Order.objects.from_request(request)

    except Order.DoesNotExist:
        order = None

    if not (order and order.validate(request)):
        context = RequestContext(request,
            {'message': _('Your order is no longer valid.')})
        return render_to_response('shop_404.html', context)    

    live = payment_live(payment_module)
    gcart = GoogleCart(order, payment_module, live)
    log.debug("CART:\n%s", gcart.cart_xml)
    template = lookup_template(payment_module, 'checkout/google/confirm.html')

    if live:
        merchant_id = payment_module.MERCHANT_ID.value
        url_template = payment_module.POST_URL.value
    else:
        merchant_id = payment_module.MERCHANT_TEST_ID.value
        url_template = payment_module.POST_TEST_URL.value
        
    post_url =  url_template % {'MERCHANT_ID' : merchant_id}

    ctx = RequestContext(request, {
        'order': order,
        'post_url': post_url,
        'google_cart' : gcart.encoded_cart(),
        'google_signature' : gcart.encoded_signature(),
        'PAYMENT_LIVE' : live
    })

    return render_to_response(template, ctx)

