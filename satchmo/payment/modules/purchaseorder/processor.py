"""
Handle a Purchase Order payments.
"""
from django.utils.translation import ugettext as _
from satchmo.payment.utils import record_payment
from satchmo.payment.modules.base import BasePaymentProcessor

class PaymentProcessor(BasePaymentProcessor):

    def __init__(self, settings):
        super(PaymentProcessor, self).__init__('purchaseorder', settings)

    def can_refund(self):
        return True

    def prepareData(self, order):
        super(PaymentProcessor, self).prepareData(order)

    def process(self):
        """
        Purchase Orders are always successful.
        """

        reason_code = "0"
        response_text = _("Success")
        
        record_payment(self.order, self.settings, amount=self.order.balance)
        
        return (True, reason_code, response_text)

