try:
    from decimal import Decimal
except:
    from django.utils._decimal import Decimal

from django.core.exceptions import ImproperlyConfigured
from django.db.models import Q
from livesettings import config_value
from satchmo_store.contact.models import Contact
from l10n.models import AdminArea, Country
from satchmo_utils import is_string_like
from product.models import TaxClass
from models import TaxBoundry, TaxRate, Taxable
import logging
import re
import datetime

log = logging.getLogger('tax.us_sst')

class Processor(object):

    method = "us_sst"

    def __init__(self, order=None, user=None):
        """
        Any preprocessing steps should go here
        For instance, copying the shipping and billing areas
        """
        self.order = order
        self.user = user

    def _get_location(self):
        area=country=postal_code=None

        if self.order:
            street1 = self.order.ship_street1
            street2 = self.order.ship_street2
            city = self.order.ship_city
            state = self.order.ship_state
            postal_code = self.order.ship_postal_code
            country = self.order.ship_country
            log.debug('Using order country: %s' % country)
            if country == 'US':
                area = state

        elif self.user and self.user.is_authenticated():
            try:
                contact = Contact.objects.get(user=self.user)
                try:
                    area = contact.shipping_address.state
                    postal_code = contact.shipping_address.postal_code
                except AttributeError:
                    pass
                try:
                    country = contact.shipping_address.country.iso2code
                    log.debug('Using contact country: %s' % country)
                except AttributeError:
                    pass

            except Contact.DoesNotExist:
                log.debug('No contact entry found.')
                pass

        if country:
            try:
                country = Country.objects.get(iso2_code__exact=country)
                log.debug('Found country by ISO code: %s' % country)
            except Country.DoesNotExist:
                log.info("Couldn't find Country from string: %s", country)
                country = None

        if not country:
            from satchmo_store.shop.models import Config
            country = Config.objects.get_current().sales_country

        if area:
            try:
                area = AdminArea.objects.get(name__iexact=area,
                                             country=country)
            except AdminArea.DoesNotExist:
                try:
                    area = AdminArea.objects.get(abbrev__iexact=area,
                                                 country=country)
                except AdminArea.DoesNotExist:
                    log.info("Couldn't find AdminArea from string: %s", area)
                    area = None

        # We don't actually try and match 'A' records.
        street_name = None
        street_number = None
        street_prefix = None
        street_suffix = None
        odd_even = None
        zip_5 = None
        zip_4 = None

        if country.iso2_code == 'US':
            if '-' in postal_code:
                zip_5, zip_4 = postal_code.split('-')
                zip_5 = int(zip_5)
                zip_4 = int(zip_4)
            else:
                zip_5 = int(postal_code)
                zip_4 = None


        log.debug('Area: %s' % area)
        log.debug('Country: %s' % country)
        log.debug('Zip: %s-%s' % (zip_5, zip_4))
        return {
            'area':area,
            'country':country,
            #'street1': street1,
            #'street_number': street_number,
            #'street_name': street_name,
            #'street_prefix': street_prefix,
            #'street_suffix': street_suffix,
            'odd_even': odd_even,
            #'street2': street2,
            #'city':city,
            #'state': state,
            'postal_code': postal_code,
            'zip_4': zip_4,
            'zip_5': zip_5,
        }

    def get_percent(self, taxclass="Default", area=None, country=None):
        return 100*self.get_rate(taxclass=taxclass, area=area, country=country)

    def get_boundry(self, taxable_class, location, date=None):
        """
        Location is a dict of:
            'area', 'country': objects
            'street1', 'street2', 'city', 'state', 'postal_code': strings
        """
        boundry = TaxBoundry.lookup(location['zip_5'], location['zip_4'], date)
        log.debug('Boundry: %s' % boundry)
        return boundry

    def get_rate(self, taxclass=None, area=None, country=None, get_object=False, **kwargs):
        if not taxclass:
            taxclass = "Default"
        rate = None

        #if not (area or country):
        location = self._get_location()
        state = location['area']
        country = location['country']

        if is_string_like(taxclass):
            try:
                taxclass = TaxClass.objects.get(title__iexact=taxclass)

            except TaxClass.DoesNotExist:
                raise ImproperlyConfigured("Can't find a '%s' Tax Class", taxclass)

        # This module only works in the USA.
        if country.iso2_code != 'US':
            rate = None
        else:
            try:
                taxable = Taxable.objects.get(taxClass=taxclass, taxZone=state)
                if taxable.isTaxable is False:
                    rate = None
                else:
                    rate = self.get_boundry(taxable, location)
                    rate.useIntrastate = taxable.useIntrastate
                    rate.useFood = taxable.useFood

            except Taxable.DoesNotExist:
                rate = None

        log.debug("Got rate [%s] = %s", taxclass, rate)
        if get_object:
            return rate
        else:
            if rate:
                return rate.percentage
            else:
                return Decimal("0.00")

    def by_price(self, taxclass, price):
        rate = self.get_rate(taxclass)

        if not rate:
            t = Decimal("0.00")
        else:
            t = rate * price

        return t

    def by_product(self, product, quantity=Decimal('1')):
        """Get the tax for a given product"""
        price = product.get_qty_price(quantity)
        tc = product.taxClass
        return self.by_price(tc, price)

    def by_orderitem(self, orderitem):
        if orderitem.product.taxable:
            price = orderitem.sub_total
            taxclass = orderitem.product.taxClass
            return self.by_price(taxclass, price)
        else:
            return Decimal("0.00")

    #def shipping(self, subtotal=None):
    #    if subtotal is None and self.order:
    #        subtotal = self.order.shipping_sub_total
    #
    #    if subtotal:
    #        rate = None
    #        if config_value('TAX','TAX_SHIPPING'):
    #            try:
    #                tc = TaxClass.objects.get(title=config_value('TAX', 'TAX_CLASS'))
    #                rate = self.get_rate(taxclass=tc)
    #            except:
    #                log.error("'Shipping' TaxClass doesn't exist.")
    #
    #        if rate:
    #            t = rate * subtotal
    #        else:
    #            t = Decimal("0.00")
    #
    #    else:
    #        t = Decimal("0.00")
    #
    #    return t

    def process(self, order=None):
        """
        Calculate the tax and return it.

        Probably need to make a breakout.
        """
        if order:
            self.order = order
        else:
            order = self.order

        sub_total = Decimal('0.00')
        taxes = {}
        rates = {}

        items = [{'type':'item', 'item':x} for x in order.orderitem_set.filter(product__taxable=True)]
        items.append({'type':'shipping', 'price':self.order.shipping_sub_total})

        for i in items:
            if i['type'] == 'item':
                item = i['item']
                tc = item.product.taxClass
                price = item.sub_total
            else:
                if not config_value('TAX','TAX_SHIPPING'):
                    continue

                try:
                    tc = TaxClass.objects.get(title=config_value('TAX', 'TAX_CLASS'))
                    price = i['price']
                    #rate = self.get_rate(taxclass=tc)
                except:
                    log.error("'Shipping' TaxClass doesn't exist.")
                    continue

            if tc:
                tc_key = tc.title
            else:
                tc_key = "Default"

            if tc_key in rates:
                rate = rates[tc_key]
            else:
                rate = self.get_rate(tc, get_object=True)
                rates[tc_key] = rate

            for tax_rate in rate.rates():
                if rate.serCode:
                    tax_key = "%s (%s-SerCode-%s)" % (
                        tc_key, tax_rate.state, rate.serCode
                    )
                else:
                    tax_key = "%s (%s-%s-%s)" % (
                        tc_key, tax_rate.state, tax_rate.jurisdictionType,
                        tax_rate.jurisdictionFipsCode
                    )

                if not tax_key in taxes:
                    taxes[tax_key] = Decimal("0.00")


                if rate:
                    t = price*tax_rate.rate(intrastate=rate.useIntrastate, food=rate.useFood)
                else:
                    t = Decimal("0.00")
                sub_total += t
                taxes[tax_key] += t

        #ship = self.shipping()
        #sub_total += ship
        #taxes['Shipping'] = ship
        ## TODO: Fix this to do the same for shipping as items.

        for k in taxes:
            log.debug('Taxes: %s = %s' % (k, taxes[k]))
            taxes[k] = taxes[k]

        return sub_total, taxes
