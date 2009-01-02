"""Simple wrapper for standard checkout as implemented in payment.views"""

from django import http
from forms import PurchaseorderPayShipForm
from livesettings import config_get_group
from payment.views import confirm, payship
from satchmo_utils.dynamic import lookup_url
import logging

log = logging.getLogger('purchaseorder.views')

settings = config_get_group('PAYMENT_PURCHASEORDER')
    
def pay_ship_info(request):
    return payship.base_pay_ship_info(
        request, 
        settings, 
        purchaseorder_process_form, 
        'shop/checkout/purchaseorder/pay_ship.html')
        
def confirm_info(request):
    return confirm.credit_confirm_info(
        request, 
        settings, 
        template='shop/checkout/purchaseorder/confirm.html')

def purchaseorder_process_form(request, contact, working_cart, payment_module):
    log.debug('purchaseorder_process_form')
    if request.method == "POST":
        log.debug('handling POST')
        new_data = request.POST.copy()
        form = PurchaseorderPayShipForm(request, payment_module, new_data)
        if form.is_valid():
            form.save(request, working_cart, contact, payment_module)
            url = lookup_url(payment_module, 'satchmo_checkout-step3')
            return (True, http.HttpResponseRedirect(url))
    else:
        log.debug('new form')
        form = PurchaseorderPayShipForm(request, payment_module)

    return (False, form)
