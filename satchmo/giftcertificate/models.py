from datetime import datetime
try:
    from decimal import Decimal
except:
    from django.utils._decimal import Decimal

from django.contrib.sites.models import Site
from django.db import models
from django.utils.translation import ugettext_lazy as _
from satchmo.configuration import config_value, config_get_group
from satchmo.contact.models import Contact, OrderPayment, Order
from satchmo.l10n.utils import moneyfmt
from satchmo.payment.common.utils import record_payment
from satchmo.product.models import Product
from utils import generate_certificate_code
import logging

GIFTCODE_KEY = 'GIFTCODE'
log = logging.getLogger('giftcertificate.models')

class GiftCertificateManager(models.Manager):
    
    def from_order(self, order):
        code = order.get_variable(GIFTCODE_KEY, "")
        log.debug("GiftCert.from_order code=%s", code)
        if code:
            return GiftCertificate.objects.get(code__exact=code.value, valid__exact=True, site=Site.objects.get_current())
        raise GiftCertificate.DoesNotExist()
    
class GiftCertificate(models.Model):
    """A Gift Cert which holds value."""
    site = models.ForeignKey(Site, null=True, blank=True, verbose_name=_('Site'))
    order = models.ForeignKey(Order, null=True, blank=True, related_name="giftcertificates", verbose_name=_('Order'))
    code = models.CharField(_('Certificate Code'), max_length=100, 
        blank=True, null=True)
    purchased_by =  models.ForeignKey(Contact, verbose_name=_('Purchased by'), 
        blank=True, null=True, related_name='giftcertificates_purchased')
    date_added = models.DateField(_("Date added"), null=True, blank=True)
    valid = models.BooleanField(_('Valid'), default=True)
    message = models.TextField(_('Message'), blank=True)
    recipient_email = models.EmailField(_("Email"), blank=True)
    start_balance = models.DecimalField(_("Starting Balance"), decimal_places=2,
        max_digits=8)    
        
    objects = GiftCertificateManager()

    def balance(self):
        b = Decimal(self.start_balance)
        for usage in self.usages.all():
            log.info('usage: %s' % usage)
            b = b - Decimal(usage.balance_used)

        return b

    balance = property(balance)

    def apply_to_order(self, order):
        """Apply up to the full amount of the balance of this cert to the order.

        Returns new balance.
        """
        amount = min(order.balance, self.balance)
        config = config_get_group('PAYMENT_GIFTCERTIFICATE')
        orderpayment = record_payment(order, config, amount)
        return self.use(amount, orderpayment=orderpayment)

    def use(self, amount, notes="", orderpayment=None):
        """Use some amount of the gift cert, returning the current balance."""
        u = GiftCertificateUsage(notes=notes, balance_used = amount, 
            orderpayment=orderpayment, giftcertificate=self)
        u.save()
        return self.balance

    def save(self):
        if not self.id:
            self.date_added = datetime.now()
        if not self.code:
            self.code = generate_certificate_code()        
        if not self.site:
            self.site = Site.objects.get_current()
        super(GiftCertificate, self).save()
        
    def __str__(self):
        sb = moneyfmt(self.start_balance)
        b = moneyfmt(self.balance)
        return "Gift Cert: %s/%s" % (sb, b)

    class Admin:
        list_display = ['code','balance']
        ordering = ['date_added']
        
    class Admin:
        pass

    class Meta:
        verbose_name = _("Gift Certificate")
        verbose_name_plural = _("Gift Certificates")    
            
class GiftCertificateUsage(models.Model):
    """Any usage of a Gift Cert is logged with one of these objects."""
    usage_date = models.DateField(_("Date of usage"), null=True, blank=True)
    notes = models.TextField(_('Notes'), blank=True)
    balance_used = models.DecimalField(_("Amount Used"), decimal_places=2,
        max_digits=8, core=True)
    orderpayment = models.ForeignKey(OrderPayment, null=True, verbose_name=_('Order Payment'))
    used_by = models.ForeignKey(Contact, verbose_name=_('Used by'), 
        blank=True, null=True, related_name='giftcertificates_used')
    giftcertificate = models.ForeignKey(GiftCertificate, related_name='usages', 
        edit_inline=models.STACKED, num_in_admin=1)
    
    def __unicode__(self):
        return u"GiftCertificateUsage: %s" % self.balance_used
    
    def save(self):
        if not self.id:
            self.usage_date = datetime.now()
        super(GiftCertificateUsage, self).save()


class GiftCertificateProduct(models.Model):
    """
    The product model for a Gift Certificate
    """
    product = models.OneToOneField(Product, verbose_name=_('Product'))
    is_shippable = False

    def __unicode__(self):
        return u"GiftCertificateProduct: %s" % self.product.name

    def order_success(self, order, order_item):
        log.debug("Order success called, creating gift certs on order: %s", order)
        message = ""
        email = ""
        for detl in order_item.orderitemdetail_set.all():
            if detl.name == "email":
                email = detl.value
            elif detl.name == "message":
                message = detl.value
                
        price=order_item.line_item_price
        log.debug("Creating gc for %s", price)
        gc = GiftCertificate(
            order = order,
            start_balance= price, 
            purchased_by = order.contact, 
            valid=True,
            message=message,
            recipient_email=email
            )
        gc.save()

    class Admin:
        pass

    class Meta:
        verbose_name = _("Gift certificate product")
        verbose_name_plural = _("Gift certificate products")
