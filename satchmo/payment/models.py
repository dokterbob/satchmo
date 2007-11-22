"""
Stores details about the available payment options.
Also stores credit card info in an encrypted format.
"""

from satchmo.configuration import config_value
from Crypto.Cipher import Blowfish
from datetime import datetime
from decimal import Decimal
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
#from modules.giftcertificate.utils import generate_certificate_code
from satchmo.contact.models import Contact, OrderPayment
from satchmo.payment.config import payment_choices, credit_choices
import base64
import logging

log = logging.getLogger('payment.models')
        
class PaymentOption(models.Model):
    """
    If there are multiple options - CC, Cash, COD, etc this class allows
    configuration.
    """
    description = models.CharField(_("Description"), max_length=20)
    active = models.BooleanField(_("Active"), 
        help_text=_("Should this be displayed as an option for the user?"))
    optionName = models.CharField(_("Option Name"), max_length=20, 
        choices = payment_choices(), unique=True, 
        help_text=_("The class name as defined in payment.py"))
    sortOrder = models.IntegerField(_("Sort Order"))
    
    class Admin:
        list_display = ['optionName','description','active']
        ordering = ['sortOrder']
    
    class Meta:
        verbose_name = "Payment Option"
        verbose_name_plural = "Payment Options"

class CreditCardDetail(models.Model):
    """
    Stores an encrypted CC number, its information, and its
    displayable number.
    """
    orderpayment = models.ForeignKey(OrderPayment, unique=True, edit_inline=True,
        num_in_admin=1, max_num_in_admin=1, related_name="creditcards")
    creditType = models.CharField(_("Credit Card Type"), max_length=16,
        choices=credit_choices())
    displayCC = models.CharField(_("CC Number (Last 4 digits)"),
        max_length=4, core=True)
    encryptedCC = models.CharField(_("Encrypted Credit Card"),
        max_length=40, blank=True, null=True, editable=False)
    expireMonth = models.IntegerField(_("Expiration Month"))
    expireYear = models.IntegerField(_("Expiration Year"))
    ccv = models.IntegerField(_("CCV"), blank=True, null=True)
    
    def storeCC(self, ccnum):
        # Take as input a valid cc, encrypt it and store the last 4 digits in a visible form
        # Must remember to save it after calling!
        secret_key = settings.SECRET_KEY
        encryption_object = Blowfish.new(secret_key)
        # block cipher length must be a multiple of 8
        padding = ''
        if (len(ccnum) % 8) <> 0:
            padding = 'X' * (8 - (len(ccnum) % 8))
        self.encryptedCC = base64.b64encode(encryption_object.encrypt(ccnum + padding))
        self.displayCC = ccnum[-4:]
    
    def _decryptCC(self):
        secret_key = settings.SECRET_KEY
        encryption_object = Blowfish.new(secret_key)
        # strip padding from decrypted credit card number
        ccnum = encryption_object.decrypt(base64.b64decode(self.encryptedCC)).rstrip('X')
        return (ccnum)
    decryptedCC = property(_decryptCC) 

    def _expireDate(self):
        return(str(self.expireMonth) + "/" + str(self.expireYear))
    expirationDate = property(_expireDate)
    
    class Meta:
        verbose_name = _("Credit Card")
        verbose_name_plural = _("Credit Cards")

# class GiftCertificateManager(models.Manager):
#     
#     def from_order(self, order):
#         code = order.get_variable('GIFTCODE', "")
#         if code:
#             return GiftCertificate.objects.get(code__exact=code.value, valid__exact=True)
#         raise GiftCertificate.DoesNotExist()
# 
# class GiftCertificate(models.Model):
#     """A Gift Cert which holds value."""
#     code = models.CharField(_('Certificate Code'), help_text=_("Automatically generated"), 
#         max_length=100, blank=True, null=True)
#     purchased_by =  models.ForeignKey(Contact, verbose_name=_('Purchased by'), 
#         blank=True, null=True, related_name='giftcertificates_purchased')
#     used_by = models.ForeignKey(Contact, verbose_name=_('Used by'), 
#         blank=True, null=True, related_name='giftcertificates_used')
#     date_added = models.DateField(_("Date added"), null=True, blank=True)
#     valid = models.BooleanField(_('Valid'), default=True)
#     message = models.TextField(_('Message'), blank=True)
#     recipient_email = models.EmailField(_("Email"), blank=True)
#     start_balance = models.DecimalField(_("Starting Balance"), decimal_places=2,
#         max_digits=8)    
#         
#     objects = GiftCertificateManager()
# 
#     @property
#     def balance(self):
#         b = Decimal(self.start_balance)
#         for usage in self.usages.all():
#             log.info('usage: %s' % usage)
#             b = b - Decimal(usage.balance_used)
# 
#         return b
# 
#     def apply_to_order(self, order):
#         """Apply up to the full amount of the balance of this cert to the order.
# 
#         Returns new balance.
#         """
#         amount = min(order.balance, self.balance)
#         orderpayment = OrderPayment(order=order, amount=amount,
#             payment=config_value('PAYMENT_GIFTCERTIFICATE', 'KEY'))
#         orderpayment.save()
#         return self.use(amount, orderpayment=orderpayment)
# 
#     def use(self, amount, notes="", orderpayment=None):
#         """Use some amount of the gift cert, returning the current balance."""
#         u = GiftCertificateUsage(notes=notes, balance_used = amount, 
#             orderpayment=orderpayment, giftcertificate=self)
#         u.save()
#         return self.balance
# 
#     def save(self):
#         if not self.id:
#             self.date_added = datetime.now()
#         if not self.code:
#             self.code = generate_certificate_code()
#         super(GiftCertificate, self).save()
# 
#     class Admin:
#         list_display = ['code','balance']
#         ordering = ['date_added']
# 
# class GiftCertificateUsage(models.Model):
#     """Any usage of a Gift Cert is logged with one of these objects."""
#     usage_date = models.DateField(_("Date of usage"), null=True, blank=True)
#     notes = models.TextField(_('Notes'), blank=True)
#     balance_used = models.DecimalField(_("Amount Used"), decimal_places=2,
#         max_digits=8, core=True)
#     orderpayment = models.ForeignKey(OrderPayment, null=True)
#     giftcertificate = models.ForeignKey(GiftCertificate, related_name='usages', 
#         edit_inline=models.STACKED, num_in_admin=1)
# 
#     def __unicode__(self):
#         return u"GiftCertificateUsage: %s" % self.balance_used
# 
#     def save(self):
#         if not self.id:
#             self.usage_date = datetime.now()
#         super(GiftCertificateUsage, self).save()

