from django import http
from django.contrib.sites.models import Site
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from forms import GiftCertCodeForm, GiftCertPayShipForm
from models import GiftCertificate, GIFTCODE_KEY
from satchmo.configuration import config_get_group
from satchmo.contact.models import Order
from satchmo.payment.common.pay_ship import pay_ship_save
from satchmo.payment.common.views import confirm, payship
from satchmo.shop.utils.dynamic import lookup_url, lookup_template
import logging

log = logging.getLogger("giftcertificate.views")

gc = config_get_group('PAYMENT_GIFTCERTIFICATE')
    
def giftcert_pay_ship_process_form(request, contact, working_cart, payment_module):
    if request.POST:
        new_data = request.POST.copy()
        form = GiftCertPayShipForm(request, payment_module, new_data)
        if form.is_valid():
            data = form.cleaned_data

            # Create a new order.
            newOrder = payship.get_or_create_order(request, working_cart, contact, data)            
            newOrder.add_variable(GIFTCODE_KEY, data['giftcode'])
            
            request.session['orderID'] = newOrder.id

            url = None
            if not url:
                url = lookup_url(payment_module, 'satchmo_checkout-step3')
                
            return (True, http.HttpResponseRedirect(url))
    else:
        form = GiftCertPayShipForm(request, payment_module)

    return (False, form)

    
def pay_ship_info(request):
    return payship.base_pay_ship_info(request, 
        gc, 
        giftcert_pay_ship_process_form,
        template="checkout/giftcertificate/pay_ship.html")
    
def confirm_info(request):
    try:
        order = Order.objects.get(id=request.session['orderID'])
        giftcert = GiftCertificate.objects.from_order(order)
    except (Order.DoesNotExist, GiftCertificate.DoesNotExist):
        giftcert = None
                
    return confirm.credit_confirm_info(request, 
        gc,
        confirm_template="checkout/giftcertificate/confirm.html", 
        extra_context={'giftcert' : giftcert})

def check_balance(request):
    if request.method == "GET":        
        code = request.GET.get('code', '')
        if code:
            try:
                gc = GiftCertificate.objects.get(code=code, 
                    value=True, 
                    site=Site.objects.get_current())
                success = True
                balance = gc.balance
            except GiftCertificate.DoesNotExist:
                success = False
        else:
            success = False
        
        ctx = RequestContext(request, {
            'code' : code,
            'success' : success,
            'balance' : balance,
            'giftcertificate' : gc
        })
    else:
        form = GiftCertCodeForm()
        ctx = RequestContext(request, {
            'code' : '',
            'form' : form
        })
    return render_to_response(ctx, 'giftcertificate/balance.html')
