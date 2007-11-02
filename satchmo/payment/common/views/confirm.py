####################################################################
# Last step in the order process - confirm the info and process it
#####################################################################

from django.conf import settings
from django.core import urlresolvers
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import loader, RequestContext, Context
from django.utils.translation import ugettext as _
from satchmo.contact.models import Order, OrderStatus
from satchmo.payment.urls import lookup_url, lookup_template
from satchmo.shop.models import Cart, Config
from satchmo.shop.utils import load_module
from socket import error as SocketError
import datetime
import logging

log = logging.getLogger('satchmo.payment.common.views')

def credit_confirm_info(request, payment_module):
    """A view which shows and requires credit card selection"""
    if not request.session.get('orderID'):
        url = urlresolvers.reverse('satchmo_checkout-step1')
        return HttpResponseRedirect(url)

    if request.session.get('cart'):
        tempCart = Cart.objects.get(id=request.session['cart'])
        if tempCart.numItems == 0:
            template = lookup_template(payment_module, 'checkout/empty_cart.html')
            return render_to_response(template, RequestContext(request))
    else:
        template = lookup_template(payment_module, 'checkout/empty_cart.html')
        return render_to_response(template, RequestContext(request))

    orderToProcess = Order.objects.get(id=request.session['orderID'])

    # Check if the order is still valid
    if not orderToProcess.validate(request):
        context = RequestContext(request,
            {'message': _('Your order is no longer valid.')})
        return render_to_response('shop_404.html', context)

    if request.POST:
        #Do the credit card processing here & if successful, empty the cart and update the status
        credit_processor = payment_module.MODULE.load_module('processor')
        processor = credit_processor.PaymentProcessor(payment_module)
        processor.prepareData(orderToProcess)
        results, reason_code, msg = processor.process()
        
        log.info("""Processing credit card transaction with %s
Order #%i
Results=%s
Response=%s
Reason=%s""", payment_module.key, orderToProcess.id, results, reason_code, msg)

        if results:
            tempCart.empty()
            #Update status
            
            orderToProcess.add_status(status='Pending', notes = "Order successfully submitted")

            #Now, send a confirmation email
            shop_config = Config.get_shop_config()
            shop_email = shop_config.store_email
            shop_name = shop_config.store_name
            t = loader.get_template('email/order_complete.txt')
            c = Context({'order': orderToProcess,
                          'shop_name': shop_name})
            subject = "Thank you for your order from %s" % shop_name
                     
            try:
                email = orderToProcess.contact.email
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
            
            #Redirect to the success page
            url = lookup_url(payment_module, 'satchmo_checkout-success')
            return HttpResponseRedirect(url)
        #Since we're not successful, let the user know via the confirmation page
        else:
            errors = msg
    else:
        errors = ''

    template = lookup_template(payment_module, 'checkout/confirm.html')
    context = RequestContext(request, {
        'order': orderToProcess,
        'errors': errors,
        'checkout_step2': lookup_url(payment_module, 'satchmo_checkout-step2')})
    return render_to_response(template, context)


