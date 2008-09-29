"""
This is a stub and used as the default processor.
It doesn't do anything but it can be used to build out another
interface.

See the authorizenet module for the reference implementation
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
        Process the transaction and return a tuple:
            (success/failure, reason code, response text)

        Example:
        >>> from django.conf import settings
        >>> from satchmo.payment.modules.dummy.processor import PaymentProcessor
        >>> processor = PaymentProcessor(settings)
        # If using a normal payment module, data should be an Order object.
        >>> data = {}
        >>> processor.prepareData(data)
        >>> processor.process()
        (True, '0', u'Success')
        """
        
        orderpayment = record_payment(self.order, self.settings, amount=self.order.balance)

        reason_code = "0"
        response_text = _("Success")

        return (True, reason_code, response_text)

