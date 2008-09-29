"""
Handle a cash-on-delivery payment.
"""
from django.utils.translation import ugettext as _
from satchmo.payment.utils import record_payment

class PaymentProcessor(object):

    def __init__(self, settings):
        self.settings = settings

    def prepareData(self, order):
        self.order = order

    def process(self):
        """
        COD is always successful.
        """

        reason_code = "0"
        response_text = _("Success")
        
        record_payment(self.order, self.settings, amount=self.order.balance)
        
        return (True, reason_code, response_text)

