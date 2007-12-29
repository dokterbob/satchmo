####################################################################
# Last step in the order process - confirm the info and process it
#####################################################################

from django.core import urlresolvers
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _
from satchmo.contact.models import Order
from satchmo.payment.common.pay_ship import send_order_confirmation
from satchmo.shop.utils.dynamic import lookup_url, lookup_template
from satchmo.shop.models import Cart
import logging

log = logging.getLogger('satchmo.payment.common.views')

def base_confirm_info(request, payment_module, confirm_template, success_handler, extra_context={}):
    try:
        orderToProcess = Order.objects.from_request(request)
    except Order.DoesNotExist:
        url = urlresolvers.reverse('satchmo_checkout-step1')
        return HttpResponseRedirect(url)

    try:
        tempCart = Cart.objects.from_request(request)
        if tempCart.numItems == 0:
            template = lookup_template(payment_module, 'checkout/empty_cart.html')
            return render_to_response(template, RequestContext(request))
    except Cart.DoesNotExist:
        template = lookup_template(payment_module, 'checkout/empty_cart.html')
        return render_to_response(template, RequestContext(request))

    # Check if the order is still valid
    if not orderToProcess.validate(request):
        context = RequestContext(request,
            {'message': _('Your order is no longer valid.')})
        return render_to_response('shop_404.html', context)

    if request.POST:
        #Do the credit card processing here & if successful, execute the success_handler
        credit_processor = payment_module.MODULE.load_module('processor')
        processor = credit_processor.PaymentProcessor(payment_module)
        processor.prepareData(orderToProcess)
        results, reason_code, msg = processor.process()
        
        log.info("""Processing %s transaction with %s
Order #%i
Results=%s
Response=%s
Reason=%s""", payment_module.LABEL.value, payment_module.KEY.value, orderToProcess.id, results, reason_code, msg)

        if results:
            if orderToProcess.paid_in_full:
                return success_handler(tempCart, orderToProcess, payment_module)
            else:
                log.debug('Not paid in full, sending to pay rest of balance')
                url = orderToProcess.get_balance_remaining_url()
                return HttpResponseRedirect(url)
            
        #Since we're not successful, let the user know via the confirmation page
        else:
            errors = msg
    else:
        errors = ''

    template = lookup_template(payment_module, confirm_template)
    base_env = {
        'order': orderToProcess,
        'errors': errors,
        'checkout_step2': lookup_url(payment_module, 'satchmo_checkout-step2')}
    if extra_context:
        base_env.update(extra_context)
    context = RequestContext(request, base_env)
    return render_to_response(template, context)

def credit_success_handler(working_cart, order, payment_module):
    working_cart.empty()    
    order.add_status(status='Pending', notes = "Order successfully submitted")
    send_order_confirmation(order)
    
    #Redirect to the success page
    url = lookup_url(payment_module, 'satchmo_checkout-success')
    return HttpResponseRedirect(url)    

def credit_confirm_info(request, payment_module, confirm_template='checkout/confirm.html', extra_context={}):
    """A view which shows and requires credit card selection"""
    return base_confirm_info(request, payment_module, confirm_template, credit_success_handler, extra_context=extra_context)
