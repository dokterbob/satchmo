"""
This is a stub and used as the default processor.
It doesn't do anything but it can be used to build out another
interface.

See the authorizenet module for the reference implementation
"""
from django.utils.translation import ugettext as _
from payment.modules.base import BasePaymentProcessor, ProcessorResult, NOTSET

class PaymentProcessor(BasePaymentProcessor):

    def __init__(self, settings):
        super(PaymentProcessor, self).__init__('dummy', settings)

    def authorize_payment(self, testing=False, amount=NOTSET):
        """
        Make an authorization for an order.  This payment will then be captured when the order
        is set marked 'shipped'.
        """
        orderauth = self.record_authorization(amount=amount, reason_code="0")
        return ProcessorResult(self.key, True, _('Success'), orderauth)

    def can_authorize(self):
        return True

    def capture_payment(self, testing=False, amount=NOTSET):
        """
        Process the transaction and return a ProcessorResult:

        Example:
        >>> from django.conf import settings
        >>> from payment.modules.dummy.processor import PaymentProcessor
        >>> processor = PaymentProcessor(settings)
        # If using a normal payment module, data should be an Order object.
        >>> data = {}
        >>> processor.prepare_data(data)
        >>> processor.process()
        ProcessorResult: DUMMY [Success] Success
        """
        
        orderpayment = self.record_payment(amount=amount, reason_code="0")
        return ProcessorResult(self.key, True, _('Success'), orderpayment)

    def capture_authorized_payment(self, authorization, amount=NOTSET):
        """
        Given a prior authorization, capture remaining amount not yet captured.
        """
        if amount == NOTSET:
            amount = authorization.remaining()

        orderpayment = self.record_payment(amount=amount, reason_code="0", 
            transaction_id="dummy", authorization=authorization)
        
        return ProcessorResult(self.key, True, _('Success'), orderpayment)
