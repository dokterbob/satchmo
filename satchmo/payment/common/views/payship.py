####################################################################
# Second step in the order process: Capture the billing method and shipping type
#####################################################################

from django import http
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _

from satchmo.contact.models import Contact
from satchmo.contact.models import Order, OrderPayment
from satchmo.payment.common.forms import CreditPayShipForm, SimplePayShipForm
from satchmo.payment.common.pay_ship import pay_ship_save
from satchmo.payment.config import payment_live
from satchmo.payment.models import CreditCardDetail
from satchmo.shop.utils.dynamic import lookup_url, lookup_template
from satchmo.shop.models import Cart

selection = _("Please Select")

def pay_ship_info_verify(request, payment_module):
    """Verify customer and cart.
    Returns:
    True, contact, cart on success
    False, destination of failure
    """
    # Verify that the customer exists.
    contact = Contact.from_request(request, create=False)
    if contact is None:
        url = lookup_url(payment_module, 'satchmo_checkout-step1')
        return (False, http.HttpResponseRedirect(url))

    # Verify that we still have items in the cart.
    if request.session.get('cart', False):
        tempCart = Cart.objects.get(id=request.session['cart'])
        if tempCart.numItems == 0:
            template = lookup_template(payment_module, 'checkout/empty_cart.html')
            return (False, render_to_response(template, RequestContext(request)))
    else:
        return (False, render_to_response('checkout/empty_cart.html', RequestContext(request)))

    return (True, contact, tempCart)

def credit_pay_ship_process_form(request, contact, working_cart, payment_module):
    """Handle the form information.
    Returns:
        (True, destination) on success
        (False, form) on failure
    """
    if request.POST:
        new_data = request.POST.copy()
        form = CreditPayShipForm(request, payment_module, new_data)
        if form.is_valid():
            data = form.cleaned_data

            # Create a new order.
            newOrder = Order(contact=contact)
            pay_ship_save(newOrder, working_cart, contact,
                shipping=data['shipping'], discount=data['discount'])
            request.session['orderID'] = newOrder.id

            orderpayment = OrderPayment(order=newOrder, amount=newOrder.balance,
                payment=unicode(payment_module.KEY.value))
            orderpayment.save()
            # Save the credit card information.
            cc = CreditCardDetail(orderpayment=orderpayment, ccv=data['ccv'],
                expireMonth=data['month_expires'],
                expireYear=data['year_expires'],
                creditType=data['credit_type'])
            cc.storeCC(data['credit_number'])
            cc.save()

            url = lookup_url(payment_module, 'satchmo_checkout-step3')
            return (True, http.HttpResponseRedirect(url))
    else:
        form = CreditPayShipForm(request, payment_module)

    return (False, form)

def simple_pay_ship_process_form(request, contact, working_cart, payment_module, create_payment=True):
    if request.POST:
        new_data = request.POST.copy()
        form = SimplePayShipForm(request, payment_module, new_data)
        if form.is_valid():
            data = form.cleaned_data

            # Create a new order.
            newOrder = Order(contact=contact)
            pay_ship_save(newOrder, working_cart, contact,
                shipping=data['shipping'], discount=data['discount'])
            request.session['orderID'] = newOrder.id

            if create_payment:
                orderpayment = OrderPayment(order=newOrder, amount=newOrder.balance, payment=payment_module.KEY.value)
                orderpayment.save()

            url = lookup_url(payment_module, 'satchmo_checkout-step3')
            return (True, http.HttpResponseRedirect(url))
    else:
        form = SimplePayShipForm(request, payment_module)

    return (False, form)

def pay_ship_render_form(request, form, template, payment_module):
    template = lookup_template(payment_module, template)
    ctx = RequestContext(request, {
        'form': form,
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
    return pay_ship_render_form(request, form, template, payment_module)

def credit_pay_ship_info(request, payment_module, template='checkout/pay_ship.html'):
    """A pay_ship view which uses a credit card."""
    return base_pay_ship_info(request, payment_module, credit_pay_ship_process_form, template)

def simple_pay_ship_info(request, payment_module, template):
    """A pay_ship view which doesn't require a credit card."""
    return base_pay_ship_info(request, payment_module, simple_pay_ship_process_form, template)
