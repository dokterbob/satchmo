"""Protx checkout custom views"""

from django.utils.translation import ugettext as _
from satchmo.payment.common.views import payship, confirm

import logging
log = logging.getLogger('protx.views')
    
def pay_ship_info(request):
    return payship.credit_pay_ship_info(request, config_get_group('PAYMENT_PROTX'))
    
def confirm_info(request, confirm_template='checkout/confirm.html', extra_context={}):
    return base_confirm_info(request, 
        config_get_group('PAYMENT_PROTX'), 
        form_handler=secure3d_form_handler,
        success_handler=confirm.credit_success_handler, 
        confirm_template=confirm_template, 
        extra_context=extra_context)
        
def confirm_secure3d(request, secure3d_template='checkout/secure3d_form.html', 
    confirm_template='checkout/confirm.html', extra_context={}):
    """Handles confirming an order and processing the charges when secured by secure3d.
 
    """
    payment_module = config_get_group('PAYMENT_PROTX')
    failure, orderToProcess, workingCart = confirm.sanity_check_confirm_order(request, payment_module)
    if failure:
        return failure
    
    processor = None
    auth3d = request.session.get('3D', None)
    if not auth3d:
        msg = '3D Secure transaction expired. Please try again.'

    else:
        if request.method == "POST":
            returnMD = request.POST.get('MD', None)
            if not returnMD:
                template = payment_module.lookup_template(secure3d_template)
                ctx ={'order': orderToProcess, 'auth': auth3d }
                return render_to_response(template, ctx, RequestContext(request))
            
            elif returnMD == auth3d['MD']:
                pares = request.POST.get('PaRes', None)
                credit_processor = payment_module.MODULE.load_module('processor')
                processor = credit_processor.PaymentProcessor(payment_module)
                processor.prepareData(orderToProcess)
                processor.prepareData3d(returnMD, pares)
                results, reason_code, msg = processor.process()
                processor.last_results = results
                processor.last_reason_code = reason_code
                processor.last_msg = msg
                if results:
                    return confirm.credit_success_handler(workingCart, orderToProcess, payment_module, 
                        confirm_template, results, reason_code, msg)
                else:
                    msg = _('3D Secure transaction was not approved by payment gateway. Please contact us.')
        else:
            template = payment_module.lookup_template(secure3d_template)
            ctx ={'order': orderToProcess, 'auth': auth3d }
            return render_to_response(template, ctx, RequestContext(request))                
                    
    return secure3d_form_handler(workingCart, orderToProcess, 
        payment_module, confirm_template, msg, processor)

def secure3d_form_handler(request, 
    workingCart, 
    orderToProcess, 
    payment_module, 
    confirm_template,
    msg,
    processor,
    default_view_tax=confirm.NOTSET,
    extra_context={}):
    """At the confirmation step, protx may ask for a secure3d authentication.  This method
    catches that, and if so, sends to that step, otherwise the form as normal"""
    
    if processor and processor.last_reason_code == '3DAUTH':
        log.debug('caught secure 3D request for order #%i, putting 3D into session as %s', 
            orderToProcess.id, processor.last_response)
        redirectUrl = payment_module.lookup_url('satchmo_checkout-secure3d')
        processor.response['TermUrl'] = redirectUrl
        request.session['3D'] = processor.last_response
        return http.HttpResponseRedirect(redirectUrl)
    
    return confirm.base_confirm_form_handler(request, workingCart, orderToProcess, payment_module, 
        confirm_template, msg, processor, default_view_tax=default_view_tax, extra_context=extra_context)
