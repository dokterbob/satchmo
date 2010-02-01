from datetime import datetime
from decimal import Decimal
from django.contrib.sites.models import Site
from django.contrib.sites.models import Site
from django.db import models
from django.utils.translation import ugettext_lazy as _
from l10n.utils import moneyfmt
from livesettings import config_value
from payment.modules.giftcertificate.utils import generate_certificate_code
from payment.utils import get_processor_by_key
from product.models import Product
from satchmo_store.contact.models import Contact
from satchmo_store.shop.models import OrderPayment, Order
import logging

GIFTCODE_KEY = 'GIFTCODE'
log = logging.getLogger('giftcertificate.models')

class GiftCertificateManager(models.Manager):

    def from_order(self, order):
        code = order.get_variable(GIFTCODE_KEY, "")
        log.debug("GiftCert.from_order code=%s", code)
        if code:
            site = order.site
            return GiftCertificate.objects.get(code__exact=code.value, valid__exact=True, site=site)
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
    message = models.CharField(_('Message'), blank=True, null=True, max_length=255)
    recipient_email = models.EmailField(_("Email"), blank=True, max_length=75)
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
        log.info('applying %s from giftcert #%i [%s] to order #%i [%s]', 
            moneyfmt(amount), 
            self.id, 
            moneyfmt(self.balance), 
            order.id, 
            moneyfmt(order.balance))
            
        processor = get_processor_by_key('PAYMENT_GIFTCERTIFICATE')
        orderpayment = processor.record_payment(order=order, amount=amount)
        self.orderpayment = orderpayment
        return self.use(amount, orderpayment=orderpayment)

    def use(self, amount, notes="", orderpayment=None):
        """Use some amount of the gift cert, returning the current balance."""
        u = GiftCertificateUsage(notes=notes, balance_used = amount,
            orderpayment=orderpayment, giftcertificate=self)
        u.save()
        return self.balance

    def save(self, **kwargs):
        if not self.pk:
            self.date_added = datetime.now()
        if not self.code:
            self.code = generate_certificate_code()
        if not self.site:
            self.site = Site.objects.get_current()
        super(GiftCertificate, self).save(**kwargs)

    def __unicode__(self):
        sb = moneyfmt(self.start_balance)
        b = moneyfmt(self.balance)
        return u"Gift Cert: %s/%s" % (sb, b)

    class Meta:
        verbose_name = _("Gift Certificate")
        verbose_name_plural = _("Gift Certificates")

class GiftCertificateUsage(models.Model):
    """Any usage of a Gift Cert is logged with one of these objects."""
    usage_date = models.DateField(_("Date of usage"), null=True, blank=True)
    notes = models.TextField(_('Notes'), blank=True, null=True)
    balance_used = models.DecimalField(_("Amount Used"), decimal_places=2,
        max_digits=8, )
    orderpayment = models.ForeignKey(OrderPayment, null=True, verbose_name=_('Order Payment'))
    used_by = models.ForeignKey(Contact, verbose_name=_('Used by'),
        blank=True, null=True, related_name='giftcertificates_used')
    giftcertificate = models.ForeignKey(GiftCertificate, related_name='usages')

    def __unicode__(self):
        return u"GiftCertificateUsage: %s" % self.balance_used

    def save(self, **kwargs):
        if not self.pk:
            self.usage_date = datetime.now()
        super(GiftCertificateUsage, self).save(**kwargs)


class GiftCertificateProduct(models.Model):
    """
    The product model for a Gift Certificate
    """
    product = models.OneToOneField(Product, verbose_name=_('Product'), primary_key=True)
    is_shippable = False
    discountable = False

    def __unicode__(self):
        return u"GiftCertificateProduct: %s" % self.product.name
        
    def _get_subtype(self):
        return 'GiftCertificateProduct'        

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
    
    def save(self, **kwargs):
        if hasattr(self.product,'_sub_types'):
            del self.product._sub_types
        super(GiftCertificateProduct, self).save(**kwargs)

    class Meta:
        verbose_name = _("Gift certificate product")
        verbose_name_plural = _("Gift certificate products")

import config
PAYMENT_PROCESSOR=True