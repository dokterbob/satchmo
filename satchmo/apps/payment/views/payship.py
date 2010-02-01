####################################################################
# Second step in the order process: Capture the billing method and shipping type
#####################################################################

from django import http
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _

from livesettings import config_value
from satchmo_store.contact.models import Contact
from payment.config import gateway_live
from payment.forms import CreditPayShipForm, SimplePayShipForm
from product.utils import find_best_auto_discount
from satchmo_store.shop.models import Cart
from satchmo_store.shop.models import Order, OrderPayment
from satchmo_utils.dynamic import lookup_url, lookup_template

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
        log.debug('No contact, returning to step 1 of checkout')
        url = lookup_url(payment_module, 'satchmo_checkout-step1')
        return (False, http.HttpResponseRedirect(url))

    # Verify that we still have items in the cart.
    tempCart = Cart.objects.from_request(request)
    if tempCart.numItems == 0:
        template = lookup_template(payment_module, 'shop/checkout/empty_cart.html')
        return (False, render_to_response(template,
                                          context_instance=RequestContext(request)))

    return (True, contact, tempCart)

def credit_pay_ship_process_form(request, contact, working_cart, payment_module, allow_skip=True, *args, **kwargs):
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
            data = form.cleaned_data
            form.save(request, working_cart, contact, payment_module, data=data)
            url = lookup_url(payment_module, 'satchmo_checkout-step3')
            return (True, http.HttpResponseRedirect(url))
        else:
            log.debug('Form errors: %s', form.errors)
    else:
        order_data = {}
        try:
            order = Order.objects.from_request(request)
            if order.shipping_model:
                order_data['shipping'] = order.shipping_model
            if order.credit_card:
                cc = order.credit_card
                val = cc.decryptedCC
                if val:
                    order_data['credit_number'] = val
                val = cc.ccv
                if val:
                    order_data['ccv'] = val
                val = cc.expire_month
                if val:
                    order_data['month_expires'] = val
                val = cc.expire_year
                if val:
                    order_data['year_expires'] = val
                val = cc.credit_type
                if val:
                    order_data['credit_type'] = val
            
            kwargs['initial'] = order_data
            ordershippable = order.is_shippable
        except Order.DoesNotExist:
            pass
        
        form = _get_form(request, payment_module, *args, **kwargs)
        if not form.is_needed():
            log.debug('Skipping pay ship because form is not needed, nothing to pay')
            form.save(request, working_cart, contact, None, 
                data={'shipping' : form.shipping_dict.keys()[0]})

            url = lookup_url(payment_module, 'satchmo_checkout-step3')
            return (True, http.HttpResponseRedirect(url))
        
    return (False, form)

def simple_pay_ship_process_form(request, contact, working_cart, payment_module, allow_skip=True):
    if request.method == "POST":
        new_data = request.POST.copy()
        form = SimplePayShipForm(request, payment_module, new_data)
        if form.is_valid():
            form.save(request, working_cart, contact, payment_module)
            url = lookup_url(payment_module, 'satchmo_checkout-step3')
            return (True, http.HttpResponseRedirect(url))
        else:
            return (False, form)
    else:
        order_data = None
        try:
            order = Order.objects.from_request(request)
            if order.shipping_model:
                order_data = {}
                order_data['shipping'] = order.shipping_model
            ordershippable = order.is_shippable
        except Order.DoesNotExist:
            pass

        form = SimplePayShipForm(request, payment_module, order_data)
        if allow_skip:
            skipping = False
            skipstep = form.shipping_hidden or not ordershippable or (len(form.shipping_dict) == 1)
            if skipstep:               
                log.debug('Skipping pay ship, nothing to select for shipping')
                # no shipping choice = skip this step
                form.save(request, working_cart, contact, payment_module, 
                    data={'shipping' : form.fields['shipping'].initial})
                skipping = True
            elif not form.is_needed():
                log.debug('Skipping pay ship because form is not needed, nothing to pay')
                form.save(request, working_cart, contact, None, 
                    data={'shipping' : form.shipping_dict.keys()[0]})
                skipping = True
            
            if skipping:
                url = lookup_url(payment_module, 'satchmo_checkout-step3')
                return (True, http.HttpResponseRedirect(url))
                
        return (False, form)

def pay_ship_render_form(request, form, template, payment_module, cart):
    template = lookup_template(payment_module, template)
            
    ctx = RequestContext(request, {
        'form': form,
        'PAYMENT_LIVE': gateway_live(payment_module),
        })
    return render_to_response(template, context_instance=ctx)

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

def credit_pay_ship_info(request, payment_module, template='shop/checkout/pay_ship.html'):
    """A pay_ship view which uses a credit card."""
    return base_pay_ship_info(request, payment_module, credit_pay_ship_process_form, template)

def simple_pay_ship_info(request, payment_module, template):
    """A pay_ship view which doesn't require a credit card."""
    return base_pay_ship_info(request, payment_module, simple_pay_ship_process_form, template)
