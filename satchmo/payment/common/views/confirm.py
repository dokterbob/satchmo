####################################################################
# Last step in the order process - confirm the info and process it
#####################################################################

from django.core import urlresolvers
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _
from satchmo.configuration import config_value
from satchmo.shop.models import Order
from satchmo.payment.config import payment_live
from satchmo.utils.dynamic import lookup_url, lookup_template
from satchmo.shop.models import Cart
import logging

log = logging.getLogger('satchmo.payment.common.views')

NOTSET = object()

def base_confirm_form_handler(request,
    workingCart, 
    orderToProcess, 
    payment_module, 
    confirm_template, 
    msg, 
    processor,
    default_view_tax=NOTSET,
    extra_context={}):
    """Show the confirmation page for the order.  Looks up the proper template for the
    payment_module.
    """
    template = lookup_template(payment_module, confirm_template)
    if default_view_tax == NOTSET:
        default_view_tax = config_value('TAX', 'DEFAULT_VIEW_TAX')
    
    log.info("default_view_tax: %s", default_view_tax)
    orderToProcess.recalculate_total()
    base_env = {
        'PAYMENT_LIVE' : payment_live(payment_module),
        'default_view_tax' : default_view_tax,
        'order': orderToProcess,
        'errors': msg,
        'checkout_step2': lookup_url(payment_module, 'satchmo_checkout-step2')}
    if extra_context:
        base_env.update(extra_context)
    context = RequestContext(request, base_env)
    return render_to_response(template, context)

def credit_success_handler(workingCart, order, payment_module):
    """Handles a success in payment.  If the order is paid-off, sends success, else return page to pay remaining."""
    if order.paid_in_full:
        workingCart.empty()
        for item in order.orderitem_set.all():
            if item.product.is_subscription:
                item.completed = True
                item.save()
        if not order.status:
            order.add_status(status='Pending', notes = "Order successfully submitted")

        #Redirect to the success page
        url = lookup_url(payment_module, 'satchmo_checkout-success')
        return HttpResponseRedirect(url)    

    else:
        log.debug('Not paid in full, sending to pay rest of balance')
        url = order.get_balance_remaining_url()
        return HttpResponseRedirect(url)

def base_confirm_info(request, 
    payment_module, 
    form_handler=base_confirm_form_handler,
    success_handler=credit_success_handler,
    confirm_template='checkout/confirm.html',
    default_view_tax=NOTSET,
    extra_context={}):
    """Handles confirming an order and processing the charges.
    
    If this is a POST, then tries to charge the order using the `payment_module`.`processor`
    On success, returns the result of the `success_handler`
    On failure, or if not a POST, returns the result of the `form_handler`
    """
    msg = ""
    failure, orderToProcess, workingCart = sanity_check_confirm_order(request, payment_module)
    if failure:
        return failure

    #sanity checks done, try to charge the customer if this is a POST
    if request.method == "POST":
        #Do the credit card processing here & if successful, execute the success_handler
        credit_processor = payment_module.MODULE.load_module('processor')
        processor = credit_processor.PaymentProcessor(payment_module)
        processor.prepareData(orderToProcess)
        results, reason_code, msg = processor.process()
        
        log.info("""Processing %s transaction with %s
Order %i
Results=%s
Response=%s
Reason=%s""", payment_module.LABEL.value, payment_module.KEY.value, 
              orderToProcess.id, results, reason_code, msg)

        if results:
            return success_handler(workingCart, orderToProcess, payment_module)
        else:
            # store this in processor for handler to use if needed
            processor.last_results = results
            processor.last_reason_code = reason_code
            processor.last_msg = msg
    else:
        processor = None
        
    return form_handler(request, workingCart, orderToProcess, payment_module, 
        confirm_template, msg, processor, default_view_tax=default_view_tax, extra_context=extra_context)

def credit_confirm_info(request, payment_module, confirm_template='checkout/confirm.html', extra_context={}):
    """A view which shows and requires credit card selection"""
        
    return base_confirm_info(request, 
        payment_module, 
        form_handler=base_confirm_form_handler,
        success_handler=credit_success_handler, 
        confirm_template=confirm_template, 
        extra_context=extra_context)

def sanity_check_confirm_order(request, payment_module):
    """Perform sanity checks on confirmation request.
    
    Returns:
    - Redirect, None if OK, some response if not OK
    - order
    - cart
    """
    try:
        orderToProcess = Order.objects.from_request(request)
    except Order.DoesNotExist:
        url = urlresolvers.reverse('satchmo_checkout-step1')
        return (HttpResponseRedirect(url), None, None)

    try:
        workingCart = Cart.objects.from_request(request)
        if workingCart.numItems == 0 and not orderToProcess.is_partially_paid:
            template = lookup_template(payment_module, 'checkout/empty_cart.html')
            return (render_to_response(template, RequestContext(request)), None, None)
    except Cart.DoesNotExist:
        template = lookup_template(payment_module, 'checkout/empty_cart.html')
        return (render_to_response(template, RequestContext(request)), None, None)

    # Check if the order is still valid
    if not orderToProcess.validate(request):
        context = RequestContext(request,
            {'message': _('Your order is no longer valid.')})
        return (render_to_response('shop_404.html', context), None, None)
        
    return None, orderToProcess, workingCart
