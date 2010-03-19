"""
Handle a cash-on-delivery payment.
"""
from django.utils.translation import ugettext as _
from payment.modules.base import BasePaymentProcessor, ProcessorResult

class PaymentProcessor(BasePaymentProcessor):
    """COD Payment Processor"""

    def __init__(self, settings):
        super(PaymentProcessor, self).__init__('cod', settings)

    def capture_payment(self, testing=False, order=None, amount=None):
        """
        COD is always successful.
        """
        if not order:
            order = self.order

        if amount is None:
            amount = order.balance

        payment = self.record_payment(order=order, amount=amount,
            transaction_id="COD", reason_code='0')

        return ProcessorResult(self.key, True, _('Success'), payment)

