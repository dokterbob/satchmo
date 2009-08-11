"""
Tiered shipping models
"""
from decimal import Decimal
from django.conf import settings
from django.db import models
from django.utils.translation import get_language, ugettext_lazy as _
from shipping.modules.base import BaseShipper
import datetime
import logging
import operator

log = logging.getLogger('shipping.TieredQuantity')

class TieredPriceException(Exception):
    def __init__(self, reason):
        self.reason = reason

class Shipper(BaseShipper):

    def __init__(self, carrier):
        self.id = carrier.key
        self.carrier = carrier
        super(BaseShipper, self).__init__()

    def __str__(self):
        """
        This is mainly helpful for debugging purposes
        """
        return "Tiered_Shipper: %s" % self.id

    def description(self):
        """
        A basic description that will be displayed to the user when selecting their shipping options
        """
        return self.carrier.description

    def cost(self):
        """
        Complex calculations can be done here as long as the return value is a dollar figure
        """
        assert(self._calculated)
        qty = Decimal('0')
        for cartitem in self.cart.cartitem_set.all():
            if cartitem.product.is_shippable:
                qty += cartitem.quantity
        return self.carrier.price(qty)

    def method(self):
        """
        Describes the actual delivery service (Mail, FedEx, DHL, UPS, etc)
        """
        return self.carrier.method

    def expectedDelivery(self):
        """
        Can be a plain string or complex calcuation returning an actual date
        """
        return self.carrier.delivery

    def valid(self, order=None):
        """
        Check to see if this order can be shipped using this method
        """
        if order:
            quants = [item.quantity for item in order.orderitem_set.all() if item.product.is_shippable]
            if quants:
                qty = reduce(operator.add, quants)
            else:
                qty = Decimal('0')
                                                
        elif self.cart:
            qty = self.cart.numItems

        try:
            price = self.carrier.price(qty)
            
        except TieredPriceException:
            return False
                        
        return True


class Carrier(models.Model):
    key = models.SlugField(_('Key'))
    ordering = models.IntegerField(_('Ordering'), default=0)
    active = models.BooleanField(_('Active'), default=True)

    def _find_translation(self, language_code=None):
        if not language_code:
            language_code = get_language()
            
        c = self.translations.filter(languagecode__exact = language_code)
        ct = c.count()

        if not c or ct == 0:
            pos = language_code.find('-')
            if pos>-1:
                short_code = language_code[:pos]
                log.debug("%s: Trying to find root language content for: [%s]", self.id, short_code)
                c = self.translations.filter(languagecode__exact = short_code)
                ct = c.count()
                if ct>0:
                    log.debug("%s: Found root language content for: [%s]", self.id, short_code)

        if not c or ct == 0:
            #log.debug("Trying to find default language content for: %s", self)
            c = self.translations.filter(languagecode__istartswith = settings.LANGUAGE_CODE)
            ct = c.count()

        if not c or ct == 0:
            #log.debug("Trying to find *any* language content for: %s", self)
            c = self.translations.all()
            ct = c.count()

        if ct > 0:
            trans = c[0]
        else:
            trans = None

        return trans

    def delivery(self):
        """Get the delivery, looking up by language code, falling back intelligently.
        """
        trans = self._find_translation()

        if trans:
            return trans.delivery
        else:
            return ""

    delivery = property(delivery)
 
    def description(self):
        """Get the description, looking up by language code, falling back intelligently.
        """
        trans = self._find_translation()

        if trans:
            return trans.description
        else:
            return ""

    description = property(description)
    
    def method(self):
        """Get the description, looking up by language code, falling back intelligently.
        """
        trans = self._find_translation()

        if trans:
            return trans.method
        else:
            return ""

    method = property(method)    
 
    def name(self):
        """Get the name, looking up by language code, falling back intelligently.
        """
        trans = self._find_translation()

        if trans:
            return trans.name
        else:
            return self.key

    name = property(name)
    
    def price(self, qty):
        """Get a price for this qty."""
        # first check for special discounts
        prices = self.tiers.filter(expires__isnull=False, quantity__lte=qty).exclude(expires__lt=datetime.date.today())
        
        if not prices.count() > 0:
            prices = self.tiers.filter(expires__isnull=True, quantity__lte=qty)

        if prices.count() > 0:
            # Get the price with the quantity closest to the one specified without going over
            return Decimal(prices.order_by('-quantity')[0].calculate_price(qty))

        else:
            log.debug("No quantity tier found for %s: qty=%d", self.id, qty)
            raise TieredPriceException('No price available')
            
            
    def __unicode__(self):
        return u"Carrier: %s" % self.name
        
    class Admin:
        ordering = ('key',)

    class Meta:
        pass
        
class CarrierTranslation(models.Model):
    carrier = models.ForeignKey('Carrier', related_name='translations')
    languagecode = models.CharField(_('language'), max_length=10, choices=settings.LANGUAGES, )
    name = models.CharField(_('Carrier'), max_length=50, )
    description = models.CharField(_('Description'), max_length=200)
    method = models.CharField(_('Method'), help_text=_("i.e. US Mail"), max_length=200)
    delivery = models.CharField(_('Delivery Days'), max_length=200)

class QuantityTier(models.Model):
    carrier = models.ForeignKey('Carrier', related_name='tiers')
    quantity = models.DecimalField(_("Min Quantity"), max_digits=18,  decimal_places=6,
        help_text=_('Minimum qty in order for this to apply?'), )
    handling = models.DecimalField(_("Handling Price"), max_digits=10, 
        decimal_places=2, )
    price = models.DecimalField(_("Shipping Per Item"), max_digits=10, 
        decimal_places=2, )
    expires = models.DateField(_("Expires"), null=True, blank=True)
    
    def calculate_price(self, qty):
        return self.handling + self.price * qty
    
    def __unicode__(self):
        return u"QuantityTier: %s @ %s" % (self.price, self.quantity)
    
    class Admin:
        ordering = ('min_total', 'expires')
    
    class Meta:
        pass

import config
