####################################################################
# Second step in the order process: Capture the billing method and shipping type
#####################################################################

from django import http
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _

from satchmo.contact.models import Contact
from satchmo.shop.models import Order, OrderPayment
from satchmo.discount.utils import find_best_auto_discount
from satchmo.payment.forms import CreditPayShipForm, SimplePayShipForm
from satchmo.payment.config import payment_live
from satchmo.shop.models import Cart
from satchmo.utils.dynamic import lookup_url, lookup_template
import logging

log = logging.getLogger('payship')
selection = _("Please Select")

def pay_ship_info_verify(request, payment_module):
    """Verify customer and cart.
    Returns:
    True, contact, cart on success
    False, destination of failure
    """
    # Verify that the customer exists.
    try:
        contact = Contact.objects.from_request(request, create=False)
    except Contact.DoesNotExist:
        url = lookup_url(payment_module, 'satchmo_checkout-step1')
        return (False, http.HttpResponseRedirect(url))

    # Verify that we still have items in the cart.
    tempCart = Cart.objects.from_request(request)
    if tempCart.numItems == 0:
        template = lookup_template(payment_module, 'checkout/empty_cart.html')
        return (False, render_to_response(template, RequestContext(request)))
            
    return (True, contact, tempCart)

def credit_pay_ship_process_form(request, contact, working_cart, payment_module, *args, **kwargs):
    """Handle the form information.
    Returns:
        (True, destination) on success
        (False, form) on failure
    """
    
    def _get_form(request, payment_module, *args, **kwargs):
        processor = payment_module.MODULE.load_module('processor')
        log.debug('processor=%s', processor)
        if hasattr(processor, 'FORM'):
            log.debug('getting form from module')
            formclass = processor.FORM
        else:
            log.debug('using default form')
            formclass = CreditPayShipForm
        
        form = formclass(request, payment_module, *args, **kwargs)
        return form

    if request.method == "POST":
        new_data = request.POST.copy()
        
        form = _get_form(request, payment_module, new_data, *args, **kwargs)
        if form.is_valid():
            form.save(request, working_cart, contact, payment_module)
            url = lookup_url(payment_module, 'satchmo_checkout-step3')
            return (True, http.HttpResponseRedirect(url))
        else:
            log.debug('Form errors: %s', form.errors)
    else:
        form = _get_form(request, payment_module, *args, **kwargs)

    return (False, form)

def simple_pay_ship_process_form(request, contact, working_cart, payment_module):
    if request.method == "POST":
        new_data = request.POST.copy()
        form = SimplePayShipForm(request, payment_module, new_data)
        if form.is_valid():
            form.save(request, working_cart, contact, payment_module)
            url = lookup_url(payment_module, 'satchmo_checkout-step3')
            return (True, http.HttpResponseRedirect(url))
    else:
        form = SimplePayShipForm(request, payment_module)

    return (False, form)

def pay_ship_render_form(request, form, template, payment_module, cart):
    template = lookup_template(payment_module, template)
    
    if cart.numItems > 0:    
        products = [item.product for item in cart.cartitem_set.all()]
        sale = find_best_auto_discount(products)
    else:
        sale = None
        
    ctx = RequestContext(request, {
        'form': form,
        'sale' : sale,
        'PAYMENT_LIVE': payment_live(payment_module)})
    return render_to_response(template, ctx)

def base_pay_ship_info(request, payment_module, form_handler, template):
    results = pay_ship_info_verify(request, payment_module)
    if not results[0]:
        return results[1]

    contact = results[1]
    working_cart = results[2]

    results = form_handler(request, contact, working_cart, payment_module)
    if results[0]:
        return results[1]

    form = results[1]
    return pay_ship_render_form(request, form, template, payment_module, working_cart)

def credit_pay_ship_info(request, payment_module, template='checkout/pay_ship.html'):
    """A pay_ship view which uses a credit card."""
    return base_pay_ship_info(request, payment_module, credit_pay_ship_process_form, template)

def simple_pay_ship_info(request, payment_module, template):
    """A pay_ship view which doesn't require a credit card."""
    return base_pay_ship_info(request, payment_module, simple_pay_ship_process_form, template)
