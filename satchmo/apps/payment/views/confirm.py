####################################################################
# Last step in the order process - confirm the info and process it
#####################################################################

from django.core import urlresolvers
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.views.decorators.cache import never_cache
from livesettings import config_value
from satchmo_store.shop.models import Order, OrderStatus
from payment.config import gateway_live
from satchmo_utils.dynamic import lookup_url, lookup_template
from satchmo_store.shop.models import Cart
from payment import signals
from payment.modules.base import ProcessorResult
import logging

log = logging.getLogger('payment.views')

class ConfirmController(object):
    """Centralizes and manages data used by the confirm views.
    Generally, this is used by initializing, then calling
    `confirm`.  If defaults need to be overridden, such as
    by setting different templates, or by overriding `viewTax`,
    then do that before calling `confirm`.
    """

    def __init__(self, request, payment_module, extra_context={}):
        self.request = request
        self.paymentModule = payment_module
        if payment_module:
            processor_module = payment_module.MODULE.load_module('processor')
            self.processor = processor_module.PaymentProcessor(self.paymentModule)
        else:
            self.processor = None
        self.viewTax = config_value('TAX', 'DEFAULT_VIEW_TAX')
        self.order = None
        self.cart = None
        self.extra_context = extra_context
                
        #to override the form_handler, set this
        #otherwise it will use the built-in `_onForm`
        self.onForm = self._onForm
        
        #to override the success method, set this
        #othewise it will use the built-in `_onSuccess`
        self.onSuccess = self._onSuccess
        
        #false on any "can not continue" error
        self.valid = False
        
        #the value to be returned from the view
        #an HttpResponse or a HttpRedirect
        self.response = None
        
        self.processorMessage = ""
        self.processorReasonCode = ""
        self.processorResults = None
        
        self.templates = {
            'CONFIRM' : 'shop/checkout/confirm.html',
            'EMPTY_CART': 'shop/checkout/empty_cart.html',
            '404': 'shop/404.html',
            }
            
                
    def confirm(self, force_post=False):
        """Handles confirming an order and processing the charges.

        If this is a POST, then tries to charge the order using the `payment_module`.`processor`
        On success, sets `response` to the result of the `success_handler`, returns True
        On failure, sets `response` to the result, the result of the `form_handler`, returns False
        
        If not a POST, sets `response` to the result, the result of the `form_handler`, returns True
        """
        if not self.sanity_check():
            return False

        status = False

        if force_post or self.request.method == "POST":
            self.processor.prepare_data(self.order)
            # This copy command is used to handle an error that can occur
            # with mod_wsgi. See #951 for more info
            tmp = self.request.POST.copy()
            if self.process():
                self.response = self.onSuccess(self)
                return True
                
        else:
            # not a post, so still a success
            status = True

        self.response = self.onForm(self)
        return status
        
        
    def invalidate(self, dest):
        """Mark the confirmation invalid, and set the response"""
        self.valid = False
        self.response = dest


    def lookup_template(self, key):
        """Shortcut method to the the proper template from the `paymentModule`"""
        return lookup_template(self.paymentModule, self.templates[key])


    def lookup_url(self, view):
        """Shortcut method to the the proper url from the `paymentModule`"""
        return lookup_url(self.paymentModule, view)

        
    def _onForm(self, controller):
        """Show the confirmation page for the order.  Looks up the proper template for the
        payment_module.
        """
        template = controller.lookup_template('CONFIRM')
        controller.order.recalculate_total()
        
        base_env = {
            'PAYMENT_LIVE' : gateway_live(controller.paymentModule),
            'default_view_tax' : controller.viewTax,
            'order': controller.order,
            'errors': controller.processorMessage,
            'checkout_step2': controller.lookup_url('satchmo_checkout-step2')}
        if controller.extra_context:
            base_env.update(controller.extra_context)
            
        context = RequestContext(self.request, base_env)
        return render_to_response(template, context_instance=context)

    def _onSuccess(self, controller):
        """Handles a success in payment.  If the order is paid-off, sends success, else return page to pay remaining."""
        if controller.order.paid_in_full:
            controller.cart.empty()
            for item in controller.order.orderitem_set.all():
                if item.product.is_subscription:
                    item.completed = True
                    item.save()
            try:
                curr_status = controller.order.orderstatus_set.latest()  
            except OrderStatus.DoesNotExist:
                curr_status = None
                
            if (curr_status is None) or (curr_status.notes and curr_status.status == "New"):
                controller.order.add_status(status='New', notes = "Order successfully submitted")
            else:
                # otherwise just update and save
                if not curr_status.notes:
                    curr_status.notes = _("Order successfully submitted")
                curr_status.save()                

            #Redirect to the success page
            url = controller.lookup_url('satchmo_checkout-success')
            return HttpResponseRedirect(url)    

        else:
            log.debug('Order #%i not paid in full, sending to pay rest of balance', controller.order.id)
            url = controller.order.get_balance_remaining_url()
            return HttpResponseRedirect(url)

    def process(self):
        """Process a prepared payment"""
        result = self.processor.process()
        self.processorResults = result.success
        if result.payment:
            reason_code = result.payment.reason_code
        else:
            reason_code = ""
        self.processorReasonCode = reason_code
        self.processorMessage = result.message

        log.info("""Processing %s transaction with %s
        Order %i
        Results=%s
        Response=%s
        Reason=%s""", self.paymentModule.LABEL.value, self.paymentModule.KEY.value, 
                      self.order.id, self.processorResults, self.processorReasonCode, self.processorMessage)
        return self.processorResults

    def sanity_check(self):
        """Ensure we have a valid cart and order."""
        try:
            self.order = Order.objects.from_request(self.request)
            
        except Order.DoesNotExist:
            url = urlresolvers.reverse('satchmo_checkout-step1')
            self.invalidate(HttpResponseRedirect(url))
            return False

        try:
            self.cart = Cart.objects.from_request(self.request)
            if self.cart.numItems == 0 and not self.order.is_partially_paid:
                template = self.lookup_template('EMPTY_CART')
                self.invalidate(render_to_response(template,
                                                   context_instance=RequestContext(self.request)))
                return False
                
        except Cart.DoesNotExist:
            template = self.lookup_template('EMPTY_CART')
            self.invalidate(render_to_response(template,
                                               context_instance=RequestContext(self.request)))
            return False

        # Check if the order is still valid
        if not self.order.validate(self.request):
            context = RequestContext(self.request, 
                {'message': _('Your order is no longer valid.')})
            self.invalidate(render_to_response(self.templates['404'],
                                               context_instance=context))

        self.valid = True
        signals.confirm_sanity_check.send(self, controller=self)
        return True

def credit_confirm_info(request, payment_module, template=None):
    """A view which shows and requires credit card selection.  
    This is the simplest confirmation flow, with no overrides."""

    controller = ConfirmController(request, payment_module)
    if template:
        controller.templates['CONFIRM'] = template
    controller.confirm()
    return controller.response
credit_confirm_info = never_cache(credit_confirm_info)

class FakeValue(object):
    def __init__(self, val):
        self.value = val

class FreeProcessor(object):

    def __init__(self, key):
        self.KEY = FakeValue(key)
        self.LABEL = FakeValue('Free Processor')

    def has_key(*args):
        return False

        
class FreeProcessorModule(object):
    def __init__(self, key):
        self.KEY = FakeValue(key)
        self.LABEL = FakeValue('Free Processor Module')

    def prepare_data(self, order, *args, **kwargs):
        self.order = order

    def process(self, *args, **kwargs):
        if self.order.paid_in_full:
            return ProcessorResult('FREE', True, _('Success'))
        else:
            return ProcessorResult('FREE', False, _('This order does not have a zero balance'))
    

def confirm_free_order(request, key="FREE", template=None):
    controller = ConfirmController(request, None)
    freeproc = FreeProcessor(key)
    freemod = FreeProcessorModule(key)
    controller.paymentModule = freeproc
    controller.processor = freemod
    if template:
        controller.templates['CONFIRM'] = template
    controller.confirm(force_post=True)
    return controller.response
