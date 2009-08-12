"""
GiftCertificate processor
"""
from django.utils.translation import ugettext as _
from l10n.utils import moneyfmt
from models import GiftCertificate
from payment.modules.base import BasePaymentProcessor, ProcessorResult, NOTSET

class PaymentProcessor(BasePaymentProcessor):

    def __init__(self, settings):
        super(PaymentProcessor, self).__init__('giftcertificate', settings)

    def capture_payment(self, testing=False, order=None, amount=NOTSET):
        """
        Process the transaction and return a ProcessorResponse
        """
        if not order:
            order = self.order
            
        if amount==NOTSET:
            amount = order.balance

        payment = None

        valid_gc = False
        if self.order.paid_in_full:
            success = True
            reason_code = "0"
            response_text = _("No balance to pay")
            self.record_payment()

        else:
            try:
                gc = GiftCertificate.objects.from_order(self.order)
                valid_gc = gc.valid

            except GiftCertificate.DoesNotExist:
                success = False
                reason_code="1"
                response_text = _("No such Gift Certificate")

            if not valid_gc:
                success = False
                reason_code="2"
                response_text = _("Bad Gift Certificate")

            else:
                gc.apply_to_order(self.order)
                payment = gc.orderpayment
                reason_code = "0"
                response_text = _("Success")
                success = True

                if not self.order.paid_in_full:
                    response_text = _("%s balance remains after gift certificate was applied") % moneyfmt(self.order.balance)

        return ProcessorResult(self.key, success, response_text, payment=payment)
