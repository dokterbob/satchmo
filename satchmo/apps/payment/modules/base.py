from datetime import datetime
from decimal import Decimal
from django.utils.translation import ugettext_lazy as _
from livesettings import config_get_group
from satchmo_store.shop.models import Order, OrderAuthorization, OrderPayment, OrderPaymentFailure, OrderPendingPayment, OrderStatus
import logging

log = logging.getLogger('payment.modules.base')

NOTSET = object()

class BasePaymentProcessor(object):

    def __init__(self, label, payment_module):
        self.key = payment_module.KEY.value
        self.settings = payment_module
        self.label = label
        self.log = logging.getLogger('payment.' + label)
        self.order = None

    def allowed(self, user, amount):
        """Allows different payment processors to be allowed for certain situations."""
        return True
        
    def authorize_and_release(self, order=None, amount=NOTSET, testing=False):
        if not order:
            order = self.order
        else:
            self.order = order
        if amount == NOTSET:
            amount = Decimal('0.01')
        self.log_extra('authorize_and_release for order #%i, %s', order.id, amount)
        result = self.authorize_payment(testing=testing, order=order, amount=amount)
        if result.success:
            auths = order.authorizations.filter(complete=False).order_by('-id')
            if auths.count() > 0:
                auth = auths[0]
            self.log_extra('releasing successful authorize_and_release for order #%i [%s], %s.  AUTH', 
                order.id,  amount, auth.transaction_id)
            return self.release_authorized_payment(order=order, auth=auth, testing=testing)
        else:
            self.log_extra('early authorization was not successful for: %s', order)
            return result

    def authorize_payment(self, testing=False, order=None, amount=NOTSET):
        """Authorize a single payment, must be overridden to function"""
        self.log.warn('Module does not implement authorize_payment: %s', self.key)
        return ProcessorResult(False, _("Not Implemented"))

    def can_authorize(self):
        return False

    def can_process(self):
        return True

    def can_refund(self):
        return False

    def can_recur_bill(self):
        return False

    def capture_authorized_payments(self, order=None):
        """Capture all outstanding payments for this processor.  This is usually called by a 
        listener which watches for a 'shipped' status change on the Order."""
        results = []
        if self.can_authorize():
            if not order:
                order = self.order
            auths = order.authorizations.filter(payment__exact=self.key, complete=False)
            self.log_extra('Capturing %i %s authorizations for order #%i', auths.count(), self.key, order.id)
            self.prepare_data(order)
            for auth in auths:
                results.append(self.capture_authorized_payment(auth))
                
        return results

    def capture_authorized_payment(self, authorization, testing=False, order=None, amount=NOTSET):
        """Capture a single payment, must be overridden to function"""
        self.log.warn('Module does not implement capture_payment: %s', self.key)
        return ProcessorResult(False, _("Not Implemented"))

    def capture_payment(self, testing=False, order=None, amount=NOTSET):
        """Capture payment without an authorization step.  Override this one."""
        self.log.warn('Module does not implement authorize_and_capture: %s', self.key)
        return ProcessorResult(False, _("Not Implemented"))
        
    def create_pending_payment(self, order=None, amount=NOTSET):
        if not order:
            order = self.order
        recorder = PaymentRecorder(order, self.settings)
        return recorder.create_pending(amount=amount)

    def get_recurring_orderitems(self):
        """Iterate through the order and get all recurring billing items"""
        subscriptions = []
        for orderitem in self.order.orderitem_set.all():
            product = orderitem.product
            if product.is_subscription:
                self.log_extra('Found subscription product: %s', product.slug)
                if product.subscriptionproduct.recurring:
                    self.log_extra('Subscription is recurring: %s', product.slug)
                    subscriptions.append(orderitem)
                elif product.subscriptionproduct.trial_set.count() > 0:
                    self.log_extra('Not recurring, but it has a trial: %s', product.slug)
                    subscriptions.append(orderitem)
                else:
                    self.log_extra('Not a recurring product: %s ', product.slug)
            else:
                self.log_extra('Not a subscription product: %s', product.slug)
        return subscriptions

    def is_live(self):
        return self.settings.LIVE.value

    def log_extra(self, msg, *args):
        """Send a log message if EXTRA_LOGGING is set in settings."""
        if self.settings.EXTRA_LOGGING.value:
            self.log.info("(Extra logging) " + msg, *args)

    def prepare_data(self, order):
        self.order = order

    def process(self, testing=False):
        """This will process the payment."""
        if self.can_authorize() and not self.settings.CAPTURE.value:
            self.log_extra('Authorizing payment on order #%i', self.order.id)
            return self.authorize_payment(testing=testing)
        else:
            self.log_extra('Capturing payment on order #%i', self.order.id)
            return self.capture_payment(testing=testing)
            
    def record_authorization(self, amount=NOTSET, transaction_id="", reason_code="", order=None):
        """
        Convert a pending payment into a real authorization.
        """
        if not order:
            order = self.order

        recorder = PaymentRecorder(order, self.settings)
        recorder.transaction_id = transaction_id
        recorder.reason_code = reason_code
        return recorder.authorize_payment(amount=amount)

    def record_failure(self, amount=NOTSET, transaction_id="", reason_code="", 
        authorization=None, order=None, details=""):
        """
        Add an OrderPaymentFailure record
        """
        log.debug('record_failure for %s', order)
        if not order:
            order = self.order

        recorder = PaymentRecorder(order, self.settings)
        recorder.transaction_id = transaction_id
        recorder.reason_code = reason_code
        recorder.record_failure(amount, details=details, authorization=authorization)

    def record_payment(self, amount=NOTSET, transaction_id="", reason_code="", authorization=None, order=None):
        """
        Convert a pending payment or an authorization.
        """
        if not order:
            order = self.order
        recorder = PaymentRecorder(order, self.settings)
        recorder.transaction_id = transaction_id
        recorder.reason_code = reason_code

        if authorization:
            payment = recorder.capture_authorized_payment(authorization, amount=amount)
            authorization.complete=True
            authorization.save()

        else:
            payment = recorder.capture_payment(amount=amount)

        return payment

    def release_authorized_payment(self, order=None, auth=None, testing=False):
        """Release a previously authorized payment."""
        self.log.warn('Module does not implement released_authorized_payment: %s', self.key)
        return ProcessorResult(False, _("Not Implemented"))

class HeadlessPaymentProcessor(BasePaymentProcessor):
    """A payment processor which doesn't actually do any processing directly.
    
    This is used for payment providers such as PayPal and Google, which are entirely
    view/form based.
    """
    
    def can_process(self):
        return False

class PaymentRecorder(object):
    """Manages proper recording of pending payments, payments, and authorizations."""
    
    def __init__(self, order, config):
        self.order = order
        self.key = unicode(config.KEY.value)
        self.config = config
        self._amount = NOTSET
        self.transaction_id = ""
        self.reason_code = ""
        self.orderpayment = None
        self.pending = None
        
    def _set_amount(self, amount):
        if amount != NOTSET:
            self._amount = amount

    def _get_amount(self):
        if self._amount == NOTSET:
            return self.order.balance
        else:
            return self._amount

    amount = property(fset=_set_amount, fget=_get_amount)

    def _get_pending(self):
        self.pendingpayments = self.order.pendingpayments.filter(payment__exact=self.key)
        if self.pendingpayments.count() > 0:
            self.pending = self.pendingpayments[0]
            log.debug("Found pending payment: %s", self.pending)
            
    def authorize_payment(self, amount=NOTSET):
        """Make an authorization, using the existing pending payment if found"""
        self.amount = amount
        log.debug("Recording %s authorization of %s for %s", self.key, self.amount, self.order)
        
        self._get_pending()

        if self.pending:
            self.orderpayment = OrderAuthorization()
            self.orderpayment.capture = self.pending.capture
            
            if amount == NOTSET:
                self.set_amount_from_pending()
            
        else:
            log.debug("No pending %s authorizations for %s", self.key, self.order)
            self.orderpayment = OrderAuthorization(
                order=self.order, 
                payment=self.key)

        self.cleanup()
        return self.orderpayment

    def capture_authorized_payment(self, authorization, amount=NOTSET):
        """Convert an authorization into a payment."""
        self.amount = amount
        log.debug("Recording %s capture of authorization #%i for %s", self.key, authorization.id, self.order)

        self.orderpayment = authorization.capture
        self.cleanup()
        return self.orderpayment

    def capture_payment(self, amount=NOTSET):
        """Make a direct payment without a prior authorization, using the existing pending payment if found."""
        self.amount = amount

        self._get_pending()
        
        if self.pending:
            self.orderpayment = self.pending.capture
            log.debug("Using linked payment: %s", self.orderpayment)

            if amount == NOTSET:
                self.set_amount_from_pending()

        else:
            log.debug("No pending %s payments for %s", self.key, self.order)
        
            self.orderpayment = OrderPayment(
                order=self.order, 
                payment=self.key)
                
        log.debug("Recorded %s payment of %s for %s", self.key, self.amount, self.order)
        self.cleanup()
        return self.orderpayment
        
    def record_failure(self, amount=NOTSET, details="", authorization=None):
        log.info('Recording a payment failure: order #%i, code %s\nmessage=%s', self.order.id, self.reason_code, details)
        self.amount = amount
            
        failure = OrderPaymentFailure.objects.create(order=self.order, 
            details=details, 
            transaction_id=self.transaction_id,
            amount = self.amount,
            payment = self.key,
            reason_code = self.reason_code
        )
        return failure
    
    def cleanup(self):
        if self.pending:
            pending = self.pending
            self.orderpayment.capture = pending.capture
            self.orderpayment.order = pending.order
            self.orderpayment.payment = pending.payment
            self.orderpayment.details = pending.details

            # delete any extra pending orderpayments
            for p in self.pendingpayments:
                if p != pending and p.capture.transaction_id=='LINKED':
                    p.capture.delete()
                p.delete()

        self.orderpayment.reason_code=self.reason_code
        self.orderpayment.transaction_id=self.transaction_id
        self.orderpayment.amount=self.amount

        self.orderpayment.time_stamp = datetime.now()
        self.orderpayment.save()

        order = self.orderpayment.order

        if order.paid_in_full:
            def _latest_status(order):
                    try:
                        curr_status = order.orderstatus_set.latest()
                        return curr_status.status
                    except OrderStatus.DoesNotExist:
                        return ''

            if _latest_status(order) in ('', 'New'):
                order.order_success()
                # order_success listeners or product methods could have modified the status. reload it.
                if _latest_status(order) == '':
                    order.add_status('New')
                
    def create_pending(self, amount=NOTSET):
        """Create a placeholder payment entry for the order.  
        This is done by step 2 of the payment process."""
        if amount == NOTSET:
            amount = Decimal("0.00")
            
        self.amount = amount

        self._get_pending()
        ct = self.pendingpayments.count()
        if ct > 0:
            log.debug("Deleting %i expired pending payment entries for order #%i", ct, self.order.id)

            for pending in self.pendingpayments:
                if pending.capture.transaction_id=='LINKED':
                    pending.capture.delete()
                pending.delete()
        
        log.debug("Creating pending %s payment of %s for %s", self.key, amount, self.order)

        self.pending = OrderPendingPayment.objects.create(order=self.order, amount=amount, payment=self.key)
        return self.pending

    def set_amount_from_pending(self):
        """Try to figure out how much to charge. If it is set on the "pending" charge use that
        otherwise use the order balance."""
        amount = self.pending.amount
                
        # otherwise use the order balance.
        if amount == Decimal('0.00'):
            amount = self.order.balance
                    
        self.amount = amount

class ProcessorResult(object):
    """The result from a processor.process call"""

    def __init__(self, processor, success, message, payment=None):
        """Initialize with:

        processor - the key of the processor setting the result
        success - boolean
        message - a lazy string label, such as _('OK)
        payment - an OrderPayment or OrderAuthorization
        """
        self.success = success
        self.processor = processor
        self.message = message
        self.payment = payment

    def __unicode__(self):
        if self.success:
            yn = _('Success')
        else:
            yn = _('Failure')

        return u"ProcessorResult: %s [%s] %s" % (self.processor, yn, self.message)
