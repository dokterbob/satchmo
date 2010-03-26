"""Protx checkout custom views"""

from django import http
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _
from livesettings import config_get_group
from payment.views import payship, confirm
import logging
from satchmo_utils.dynamic import lookup_template

log = logging.getLogger('protx.views')
    
def pay_ship_info(request):
    return payship.credit_pay_ship_info(request, 
            config_get_group('PAYMENT_PROTX'),
            template="shop/checkout/protx/pay_ship.html")
    
def confirm_info(request, template='shop/checkout/protx/confirm.html', extra_context={}):
    payment_module = config_get_group('PAYMENT_PROTX')
    controller = confirm.ConfirmController(request, payment_module)
    controller.templates['CONFIRM'] = template
    controller.extra_context = extra_context
    controller.onForm = secure3d_form_handler
    controller.confirm()
    return controller.response
            
def confirm_secure3d(request, secure3d_template='shop/checkout/secure3d_form.html', 
    confirm_template='shop/checkout/confirm.html', extra_context={}):
    """Handles confirming an order and processing the charges when secured by secure3d.
 
    """
    payment_module = config_get_group('PAYMENT_PROTX')
    controller = confirm.ConfirmController(request, payment_module, extra_context=extra_context)
    controller.template['CONFIRM'] = confirm_template
    if not controller.sanity_check():
        return controller.response
    
    auth3d = request.session.get('3D', None)
    if not auth3d:
        controller.processorMessage = _('3D Secure transaction expired. Please try again.')

    else:
        if request.method == "POST":
            returnMD = request.POST.get('MD', None)
            if not returnMD:
                template = lookup_template(payment_module, secure3d_template)
                ctx = RequestContext(request, {'order': controller.order, 'auth': auth3d })
                return render_to_response(template, context_instance=ctx)

            elif returnMD == auth3d['MD']:
                pares = request.POST.get('PaRes', None)
                controller.processor.prepare_data(controller.order)
                controller.processor.prepare_data3d(returnMD, pares)
                if controller.process():
                    return controller.onSuccess(controller)
                else:
                    controller.processorMessage = _('3D Secure transaction was not approved by payment gateway. Please contact us.')
        else:
            template = lookup_template(payment_module, secure3d_template)
            ctx =RequestContext(request, {
                'order': controller.order, 'auth': auth3d 
                })
            return render_to_response(template, context_instance=ctx)

    return secure3d_form_handler(controller)

def secure3d_form_handler(controller):
    """At the confirmation step, protx may ask for a secure3d authentication.  This method
    catches that, and if so, sends to that step, otherwise the form as normal"""
    
    if controller.processorReasonCode == '3DAUTH':
        log.debug('caught secure 3D request for order #%i, putting 3D into session as %s', 
            controller.order.id, controller.processorReasonCode)
            
        redirectUrl = controller.lookup_url('satchmo_checkout-secure3d')
        controller.processor.response['TermUrl'] = redirectUrl
        controller.request.session['3D'] = controller.processorReasonCode
        return http.HttpResponseRedirect(redirectUrl)
    
    return controller.onForm(controller)
