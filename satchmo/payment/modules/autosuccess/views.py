from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from satchmo.configuration import config_get_group
from satchmo.contact.models import Order, Contact, OrderPayment
from satchmo.payment.common.pay_ship import pay_ship_save, send_order_confirmation
from satchmo.shop.utils.dynamic import lookup_url, lookup_template
from satchmo.shop.models import Cart

import logging

log = logging.getLogger('autosuccess.views')

def one_step(request):
    payment_module = config_get_group('PAYMENT_AUTOSUCCESS')

    #First verify that the customer exists
    contact = Contact.from_request(request, create=False)
    if contact is None:
        url = lookup_url(payment_module, 'satchmo_checkout-step1')
        return HttpResponseRedirect(url)
    #Verify we still have items in the cart
    if request.session.get('cart', False):
        tempCart = Cart.objects.get(id=request.session['cart'])
        if tempCart.numItems == 0:
            template = lookup_template(payment_module, 'checkout/empty_cart.html')
            return render_to_response(template, RequestContext(request))
    else:
        template = lookup_template(payment_module, 'checkout/empty_cart.html')
        return render_to_response(template, RequestContext(request))

    # Create a new order
    newOrder = Order(contact=contact)
    pay_ship_save(newOrder, tempCart, contact,
        shipping="", discount="")
        
    request.session['orderID'] = newOrder.id
        
    newOrder.add_status(status='Pending', notes = "Order successfully submitted")

    orderpayment = OrderPayment(order=newOrder, amount=newOrder.balance, payment=payment_module.KEY.value)
    orderpayment.save()        

    #Now, send a confirmation email
    if payment_module['EMAIL'].value:
        send_order_confirmation(newOrder)    

    tempCart.empty()
    success = lookup_url(payment_module, 'satchmo_checkout-success')
    return HttpResponseRedirect(success)

