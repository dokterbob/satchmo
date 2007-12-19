from decimal import Decimal
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Q
from satchmo.configuration import config_value
from satchmo.contact.models import Contact
from satchmo.l10n.models import AdminArea, Country
from satchmo.shop.models import Config
from satchmo.shop.utils import is_string_like
from satchmo.tax.models import TaxRate, TaxClass
import logging

log = logging.getLogger('tax.area')

class Processor(object):
    
    method = "area"
    
    def __init__(self, order=None, user=None):
        """
        Any preprocessing steps should go here
        For instance, copying the shipping and billing areas
        """
        self.order = order
        self.user = user
        
    def _get_location(self):

        area=country=None
        
        if self.order:
            country = self.order.ship_country
            area = self.order.ship_state
        
        elif self.user and self.user.is_authenticated():
            try:
                contact = Contact.objects.get(user=self.user)
                try:
                    area = contact.state
                except AttributeError:
                    pass
                try:
                    country = contact.country
                except AttributeError:
                    pass

            except Contact.DoesNotExist:
                pass
        
        if area:
            try:
                area = AdminArea.objects.get(name__iexact=area)
            except AdminArea.DoesNotExist:
                try:
                    area = AdminArea.objects.get(abbrev__iexact=area)
                except AdminArea.DoesNotExist:
                    log.info("Couldn't find AdminArea from string: %s", area)
                    area = None
        if country:
            try:
                country = Country.objects.get(iso2_code__exact=country)
            except Country.DoesNotExist:
                log.info("Couldn't find Country from string: %s", country)
                country = None

        if not country:
            country = Config.get_shop_config().sales_country
            
        return area, country
        
    def _get_rate(self, taxclass, area, country):
        rate = None
        if not taxclass:
            taxclass="Default"
            
        if is_string_like(taxclass):
            try:
                taxclass = TaxClass.objects.get(title__exact=taxclass)
            
            except TaxClass.DoesNotExist:
                try:
                    taxclass = TaxRate.objects.get(title__exact="Default")
                except TaxClass.DoesNotExist:
                    raise ImproperlyConfigured("You must have a 'default' Tax Class")            
            
        if area:
            try:
                rate = TaxRate.objects.get(taxClass=taxclass, taxZone=area)
                
            except TaxRate.DoesNotExist:
                rate = None
                
        if not rate:
            try:
                rate = TaxRate.objects.get(taxClass=taxclass, taxCountry=country)
                
            except TaxRate.DoesNotExist:
                rate = None
                
        return rate

    def by_price(self, taxclass, price):
        area, country = self._get_location()
        rate = self._get_rate(taxclass, area, country)

        if not rate:
            t = Decimal("0.00")
        else:
            t = rate.percentage * price

        return round_cents(t)

    def by_product(self, product, quantity=1):
        """Get the tax for a given product"""
        price = product.get_qty_price(quantity)
        tc = product.taxClass
        return self.by_price(tc, price)
        
    def by_orderitem(self, orderitem):
        price = orderitem.sub_total
        taxclass = orderitem.product.taxClass
        return self.by_price(taxclass, price)

    def shipping(self):
        if self.order:
            s = self.order.shipping_sub_total
            area, country = self._get_location()
            tc = TaxClass.objects.get(title='Shipping')
            rate = self._get_rate(tc, area, country)

            if rate:
                t = rate.percentage * s
            else:
                t = Decimal("0.00")
            
        else:
            t = Decimal("0.00")
        
        return t

    def process(self, order=None):
        """
        Calculate the tax and return it.
        
        Ignoring discounts for now.
        
        Probably need to make a breakout.
        """
        if order:
            self.order = order
        else:
            order = self.order
        
        sub_total = Decimal('0.00')
        taxes = {}
        
        rates = {}
        for item in order.orderitem_set.all():
            tc = item.product.taxClass
            if tc:
                tc_key = tc.title
            else:
                tc_key = "Default"
                
            if rates.has_key(tc_key):
                rate = rates[tc_key]
            else:
                area, country = self._get_location()
                rate = self._get_rate(tc, area, country)
                rates[tc_key] = rate
                taxes[tc_key] = Decimal("0.00")
                
            price = item.sub_total
            if rate:
                t = price*rate.percentage
            else:
                t = Decimal("0.00")
            sub_total += t
            taxes[tc_key] += t
        
        ship = self.shipping()
        sub_total += ship
        taxes['Shipping'] = ship
        
        sub_total = round_cents(sub_total)
        for k in taxes:
            taxes[k] = round_cents(taxes[k])
        
        return sub_total, taxes
        
def round_cents(x):
    return x.quantize(Decimal('0.01'))