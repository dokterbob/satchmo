from django.utils.translation import ugettext_lazy as _
from payment.modules.base import BasePaymentProcessor, ProcessorResult, NOTSET

class PaymentProcessor(BasePaymentProcessor):
    """
    Autosuccess Payment Module
    """
    def __init__(self, settings):
        super(PaymentProcessor, self).__init__('autosuccess', settings)

    def capture_payment(self, testing=False, order=None, amount=NOTSET):
        if not order:
            order = self.order

        if amount == NOTSET:
            amount = order.balance

        payment = self.record_payment(order=order, amount=amount, 
            transaction_id="AUTO", reason_code='0')

        return ProcessorResult(self.key, True, _('Success'), payment)
