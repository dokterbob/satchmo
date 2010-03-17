"""
TieredWeight shipping models
"""
import logging

from datetime import date
from django.db import models
from django.conf import settings
from django.utils.translation import get_language, ugettext_lazy as _
from l10n.models import Country
from shipping.modules.base import BaseShipper

try:
    from decimal import Decimal
except:
    from django.utils._decimal import Decimal


log = logging.getLogger('shipping.TieredWeight')


class TieredWeightException(Exception):
    pass


def _get_cart_weight(cart):
    weight = Decimal('0.0')
    for item in cart.cartitem_set.all():
        if item.is_shippable and item.product.weight:
            weight = weight + (item.product.weight * item.quantity)
    return weight


class Shipper(BaseShipper):
    def __init__(self, carrier):
        self.id = 'tieredweight_%i' % carrier.pk
        self._carrier = carrier
        super(BaseShipper, self).__init__()


    def calculate(self, cart, contact):
        """
        Perform shipping calculations
        """
        self._cost, self._weight = None, None
        self._zone = self._carrier.get_zone(contact._shipping_address().country)

        if self._zone:
            try:
                self._weight = _get_cart_weight(cart)
                self._cost = self._zone.cost(self._weight)
            except TieredWeightException:
                pass

        super(Shipper, self).calculate(cart, contact)


    def __str__(self):
        """
        This is mainly helpful for debugging purposes
        """
        return "TieredWeight_Shipper: %s" % self.id


    def cost(self):
        """
        Calulates the shipping for the order
        """
        assert(self._calculated)
        return self._cost


    def description(self):
        """
        A basic description that will be displayed to the user when selecting their shipping options
        """
        assert(self._calculated)
        return self._zone.description


    def method(self):
        """
        Describes the actual delivery service (Mail, FedEx, DHL, UPS, etc)
        """
        assert(self._calculated)
        return self._zone.method


    def expectedDelivery(self):
        """
        Can be a plain string or complex calculation returning an actual date
        """
        assert(self._calculated)
        return self._zone.delivery


    def valid(self, order=None):
        """
        Check if shipping is valid for country and set zone accordingly. Fallback 
        to default zone if set
        """
        assert(self._calculated)
        # I think its reasonable to assume this shipping method should
        # not be used on an order that doesn't weigh anything.
        if not self._weight or self._weight == Decimal('0.0'):
            return False

        if self._zone and self._cost:
            return True


class Carrier(models.Model):
    name = models.CharField(_('carrier'), max_length=50)
    ordering = models.IntegerField(_('Ordering'), default=0)
    active = models.BooleanField(_('Active'), default=True)
    default_zone = models.ForeignKey('Zone', verbose_name=_('default_zone'), 
        related_name='default', null=True, blank=True)


    def __unicode__(self):
        return u'%s' % self.name


    class Meta:
        ordering = ['ordering',]
        verbose_name = _('carrier')
        verbose_name_plural = _('carriers')


    def get_zone(self, country):
        try:
            return self.zones.filter(countries=country).get()
        except Zone.DoesNotExist:
            if self.default_zone:
                return self.default_zone


class Zone(models.Model):
    carrier = models.ForeignKey(Carrier, verbose_name=_('carrier'), related_name='zones')
    name = models.CharField(_('name'), max_length=50)
    countries = models.ManyToManyField(Country, verbose_name=_('countries'), blank=True)
    handling = models.DecimalField(_('handling'), max_digits=10, decimal_places=2,
        null=True, blank=True)


    def __unicode__(self):
        return u'%s' % self.name


    class Meta:
        unique_together = ('carrier', 'name')
        ordering = ['carrier', 'name',]
        verbose_name = _('zone')
        verbose_name_plural = _('zones')


    def _find_translation(self, language_code=None):
        if not language_code:
            language_code = get_language()
    
        c = self.translations.filter(lang_code__exact=language_code)
        ct = c.count()
    
        if not c or ct == 0:
            pos = language_code.find('-')
            if pos > -1:
                short_code = language_code[:pos]
                log.debug("%s: Trying to find root language content for: [%s]", self, short_code)
                c = self.translations.filter(lang_code__exact=short_code)
                ct = c.count()
                if ct > 0:
                    log.debug("%s: Found root language content for: [%s]", self, short_code)
    
        if not c or ct == 0:
            #log.debug("Trying to find default language content for: %s", self)
            c = self.translations.filter(lang_code__istartswith=settings.LANGUAGE_CODE)
            ct = c.count()
    
        if not c or ct == 0:
            #log.debug("Trying to find *any* language content for: %s", self)
            c = self.translations.all()
            ct = c.count()
    
        if ct > 0:
            return c[0]
        else:
            return None


    def delivery(self):
        """
        Get the delivery, looking up by language code, falling back gracefully
        """
        trans = self._find_translation()
        if trans:
            return trans.delivery
        else:
            return u''
    delivery = property(delivery)


    def description(self):
        """
        Get the description, looking up by language code, falling back gracefully
        """
        trans = self._find_translation()
        if trans:
            return trans.description
        else:
            return u''
    description = property(description)


    def method(self):
        """
        Get the description, looking up by language code, falling back gracefully
        """
        trans = self._find_translation()
        if trans:
            return trans.method
        else:
            return u''
    method = property(method)


    def cost(self, weight):
        """
        Get a price for this weight
        """
        tiers_tmp = self.tiers.filter(min_weight__gte=weight).order_by('min_weight')
        tiers = tiers_tmp.filter(expires__gte=date.today())[:1]

        if tiers.count() is 0:
            tiers = tiers_tmp.filter(expires__isnull=True)[:1]

        if tiers.count() is not 0:
            return tiers[0].cost
        else:
            log.debug("No tiered price found for %s: weight=%s", self, weight)
            raise TieredWeightException


class ZoneTranslation(models.Model):
    zone = models.ForeignKey(Zone, verbose_name=_('zone'), related_name='translations')
    lang_code = models.CharField(_('language'), max_length=10, choices=settings.LANGUAGES)
    description = models.CharField(_('description'), max_length=200)
    method = models.CharField(_('method'), help_text=_('i.e. Air, Land, Sea'), max_length=200)
    delivery = models.CharField(_('delivery'), max_length=200)


    def __unicode__(self):
        return u'%s' % self.lang_code


    class Meta:
        ordering = ['lang_code',]
        verbose_name = _('zone translation')
        verbose_name_plural = _('zone translations')


class WeightTier(models.Model):
    zone = models.ForeignKey(Zone, verbose_name=_('zone'), related_name='tiers')
    min_weight = models.DecimalField(_('min weight'), max_digits=10, decimal_places=2)
    handling = models.DecimalField(_('handling ajustment'), max_digits=10, decimal_places=2,
        null=True, blank=True)
    price = models.DecimalField(_('shipping price'), max_digits=10, decimal_places=2)
    expires = models.DateField(_('expires'), null=True, blank=True)
    

    def __unicode__(self):
        return u'Weight: %s (Total cost: %s)' % (self.min_weight, self.cost)


    class Meta:
        unique_together = ('zone', 'min_weight', 'expires')
        ordering = ['min_weight',]
        verbose_name = _('weight tier')
        verbose_name_plural = _('weight tiers')


    def cost(self):
        handling = Decimal('0.0')

        if self.zone.handling:
            handling = handling + self.zone.handling

        if self.handling:
            handling = handling + self.handling

        return Decimal(handling + self.price)
    cost = property(cost)


import config
