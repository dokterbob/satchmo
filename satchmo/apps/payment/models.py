"""
Stores details about the available payment options.
Also stores credit card info in an encrypted format.
"""

from Crypto.Cipher import Blowfish
from datetime import datetime
from decimal import Decimal
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from livesettings import config_value, config_choice_values, SettingNotSet
from payment.fields import PaymentChoiceCharField, CreditChoiceCharField
from satchmo_store.contact.models import Contact
from satchmo_store.shop.models import OrderPayment
import base64
import config
import keyedcache
import logging
import satchmo_utils.sslurllib

log = logging.getLogger('payment.models')
        
class PaymentOption(models.Model):
    """
    If there are multiple options - CC, Cash, COD, etc this class allows
    configuration.
    """
    description = models.CharField(_("Description"), max_length=20)
    active = models.BooleanField(_("Active"), 
        help_text=_("Should this be displayed as an option for the user?"))
    optionName = PaymentChoiceCharField(_("Option Name"), max_length=20, 
        unique=True, 
        help_text=_("The class name as defined in payment.py"))
    sortOrder = models.IntegerField(_("Sort Order"))
    
    class Meta:
        verbose_name = _("Payment Option")
        verbose_name_plural = _("Payment Options")

class CreditCardDetail(models.Model):
    """
    Stores an encrypted CC number, its information, and its
    displayable number.
    """
    orderpayment = models.ForeignKey(OrderPayment, unique=True, 
        related_name="creditcards")
    credit_type = CreditChoiceCharField(_("Credit Card Type"), max_length=16)
    display_cc = models.CharField(_("CC Number (Last 4 digits)"),
        max_length=4, )
    encrypted_cc = models.CharField(_("Encrypted Credit Card"),
        max_length=40, blank=True, null=True, editable=False)
    expire_month = models.IntegerField(_("Expiration Month"))
    expire_year = models.IntegerField(_("Expiration Year"))
    card_holder = models.CharField(_("card_holder Name"), max_length=60, blank=True)
    start_month = models.IntegerField(_("Start Month"), blank=True, null=True)
    start_year = models.IntegerField(_("Start Year"), blank=True, null=True)
    issue_num = models.CharField(blank=True, null=True, max_length=2)
    
    def storeCC(self, ccnum):
        """Take as input a valid cc, encrypt it and store the last 4 digits in a visible form"""
        self.display_cc = ccnum[-4:]
        encrypted_cc = _encrypt_code(ccnum)
        if config_value('PAYMENT', 'STORE_CREDIT_NUMBERS'):
            self.encrypted_cc = encrypted_cc
        else:
            standin = "%s%i%i%i" % (self.display_cc, self.expire_month, self.expire_year, self.orderpayment.id)
            self.encrypted_cc = _encrypt_code(standin)
            key = _encrypt_code(standin + '-card')
            keyedcache.cache_set(key, skiplog=True, length=60*60, value=encrypted_cc)
    
    def setCCV(self, ccv):
        """Put the CCV in the cache, don't save it for security/legal reasons."""
        if not self.encrypted_cc:
            raise ValueError('CreditCardDetail expecting a credit card number to be stored before storing CCV')
            
        keyedcache.cache_set(self.encrypted_cc, skiplog=True, length=60*60, value=ccv)
    
    def getCCV(self):
        try:
            ccv = keyedcache.cache_get(self.encrypted_cc)
        except keyedcache.NotCachedError:
            ccv = ""

        return ccv
    
    ccv = property(fget=getCCV, fset=setCCV)
    
    def _decryptCC(self):
        ccnum = _decrypt_code(self.encrypted_cc)
        if not config_value('PAYMENT', 'STORE_CREDIT_NUMBERS'):
            try:
                key = _encrypt_code(ccnum + '-card')
                encrypted_ccnum = keyedcache.cache_get(key)
                ccnum = _decrypt_code(encrypted_ccnum)
            except keyedcache.NotCachedError:
                ccnum = ""
        return ccnum
                
    decryptedCC = property(_decryptCC) 

    def _expireDate(self):
        return(str(self.expire_month) + "/" + str(self.expire_year))
    expirationDate = property(_expireDate)
    
    class Meta:
        verbose_name = _("Credit Card")
        verbose_name_plural = _("Credit Cards")

def _decrypt_code(code):
    """Decrypt code encrypted by _encrypt_code"""
    secret_key = settings.SECRET_KEY
    encryption_object = Blowfish.new(secret_key)
    # strip padding from decrypted credit card number
    return encryption_object.decrypt(base64.b64decode(code)).rstrip('X')

def _encrypt_code(code):
    """Quick encrypter for CC codes or code fragments"""
    secret_key = settings.SECRET_KEY
    encryption_object = Blowfish.new(secret_key)
    # block cipher length must be a multiple of 8
    padding = ''
    if (len(code) % 8) <> 0:
        padding = 'X' * (8 - (len(code) % 8))
    return base64.b64encode(encryption_object.encrypt(code + padding))
