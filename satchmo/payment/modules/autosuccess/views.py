from django.conf import settings
from django.core import urlresolvers
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import loader, RequestContext, Context
from django.utils.translation import ugettext as _
from satchmo.configuration import config_value, config_get_group
from satchmo.contact.models import Order, Contact, OrderPayment
from satchmo.payment.common.pay_ship import pay_ship_save
from satchmo.payment.common.views import payship
from satchmo.payment.config import payment_live
from satchmo.payment.urls import lookup_url, lookup_template
from satchmo.shop.models import Cart, Config
from socket import error as SocketError

import logging

log = logging.getLogger('autosuccess.views')

def one_step(request):
    payment_module = config_get_group('PAYMENT_AUTOSUCCESS')

    #First verify that the customer exists
    contact = Contact.from_request(request, create=False)
    if contact is None:
        url = lookup_url(payment_module, 'satchmo_checkout-step1')
        return http.HttpResponseRedirect(url)
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
        shop_config = Config.get_shop_config()
        shop_email = shop_config.store_email
        shop_name = shop_config.store_name
        t = loader.get_template('email/order_complete.txt')
        c = Context({'order': newOrder,
                      'shop_name': shop_name})
        subject = "Thank you for your order from %s" % shop_name
             
        try:
            email = newOrder.contact.email
            body = t.render(c)
            send_mail(subject, body, shop_email,
                      [email], fail_silently=False)
        except SocketError, e:
            if settings.DEBUG:
                log.error('Error sending mail: %s' % e)
                log.warn('Ignoring email error, since you are running in DEBUG mode.  Email was:\nTo:%s\nSubject: %s\n---\n%s', email, subject, body)
            else:
                log.fatal('Error sending mail: %s' % e)
                raise IOError('Could not send email, please check to make sure your email settings are correct, and that you are not being blocked by your ISP.')    
    
    
    tempCart.empty()
    success = lookup_url(payment_module, 'satchmo_checkout-success')
    return HttpResponseRedirect(success)

