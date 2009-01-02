"""
GiftCertificate processor
"""
from django.utils.translation import ugettext as _
from models import GiftCertificate
from l10n.utils import moneyfmt

class PaymentProcessor(object):

    def __init__(self, settings):
        self.settings = settings

    def prepareData(self, order):
        self.order = order

    def process(self):
        """
        Process the transaction and return a tuple:
            (success/failure, reason code, response text)
        """
        if self.order.paid_in_full:
            success = True
            reason_code = "0"
            response_text = _("No balance to pay")

        else:    
            try:
                gc = GiftCertificate.objects.from_order(self.order)
            
            except GiftCertificate.DoesNotExist:
                success = False
                reason_code="1"
                response_text = _("No such Gift Certificate")
            
            if not gc.valid:
                success = False
                reason_code="2"
                response_text = _("Bad Gift Certificate")
        
            else:
                gc.apply_to_order(self.order)
                reason_code = "0"
                response_text = _("Success")
                success = True
                
                if not self.order.paid_in_full:
                    response_text = _("%s balance remains after gift certificate was applied") % moneyfmt(self.order.balance)
                
        return (success, reason_code, response_text)

