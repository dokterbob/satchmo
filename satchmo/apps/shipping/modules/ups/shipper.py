"""
UPS Shipping Module
You must have a UPS account to use this module.
You may register at ups.com

This module uses the XML online tools for maximum flexibility.  It is
primarily created for use in the US but reconfiguring for international
shipping or more advanced uses should be straightforward.

It is recommended that you refer to the UPS shipper developer documents
(available when you register at UPS) in order to tailor this to your
unique needs.
"""

from decimal import Decimal
from django.core.cache import cache
from django.template import Context, loader
from django.utils.translation import ugettext as _
from livesettings import config_get_group, config_value
from shipping import signals
from shipping.modules.base import BaseShipper
import logging
import urllib2

try:
    from xml.etree.ElementTree import fromstring, tostring
except ImportError:
    from elementtree.ElementTree import fromstring, tostring

log = logging.getLogger('ups.shipper')
class Shipper(BaseShipper):
    
    def __init__(self, cart=None, contact=None, service_type=None):
        self._calculated = False
        self.cart = cart
        self.contact = contact
        if service_type:        
            self.service_type_code = service_type[0]
            self.service_type_text = service_type[1]
        else:
            self.service_type_code = "99"
            self.service_type_text = "Uninitialized"
        self.id = u"UPS-%s-%s" % (self.service_type_code, self.service_type_text)
        self.raw = "NO DATA"
        #if cart or contact:
        #    self.calculate(cart, contact)
    
    def __str__(self):
        """
        This is mainly helpful for debugging purposes
        """
        return "UPS"
        
    def description(self):
        """
        A basic description that will be displayed to the user when selecting their shipping options
        """
        return _("UPS - %s" % self.service_type_text)

    def cost(self):
        """
        Complex calculations can be done here as long as the return value is a decimal figure
        """
        assert(self._calculated)
        return(Decimal(self.charges))

    def method(self):
        """
        Describes the actual delivery service (Mail, FedEx, DHL, UPS, etc)
        """
        return _("UPS")

    def expectedDelivery(self):
        """
        Can be a plain string or complex calcuation returning an actual date
        """
        if self.delivery_days <> "1":
            return _("%s business days" % self.delivery_days)
        else:
            return _("%s business day" % self.delivery_days)
        
    def valid(self, order=None):
        """
        Can do complex validation about whether or not this option is valid.
        For example, may check to see if the recipient is in an allowed country
        or location.
        """
        return self.is_valid

    def _process_request(self, connection, request):
        """
        Post the data and return the XML response
        """
        conn = urllib2.Request(url=connection, data=request.encode("utf-8"))
        f = urllib2.urlopen(conn)
        all_results = f.read()
        self.raw = all_results
        return(fromstring(all_results))
        
    def calculate(self, cart, contact):
        """
        Based on the chosen UPS method, we will do our call to UPS and see how much it will
        cost.
        We will also need to store the results for further parsing and return via the
        methods above
        """
        from satchmo_store.shop.models import Config
        
        settings =  config_get_group('shipping.modules.ups')
        self.delivery_days = _("3 - 4") #Default setting for ground delivery
        shop_details = Config.objects.get_current()
        configuration = {
            'xml_key': settings.XML_KEY.value,
            'account': settings.ACCOUNT.value,
            'userid': settings.USER_ID.value,
            'password': settings.USER_PASSWORD.value,
            'container': settings.SHIPPING_CONTAINER.value,
            'pickup': settings.PICKUP_TYPE.value,
            'ship_type': self.service_type_code,
            'shop_details':shop_details,
        }
        shippingdata = {
                'config': configuration,
                'cart': cart,
                'contact': contact,
                'shipping_address' : shop_details,
                'shipping_phone' : shop_details.phone,
                'shipping_country_code' : shop_details.country.iso2_code
        }
        signals.shipping_data_query.send(Shipper, shipper=self, cart=cart, shippingdata=shippingdata)
        c = Context(shippingdata)
        t = loader.get_template('shipping/ups/request.xml')
        request = t.render(c)
        self.is_valid = False
        if settings.LIVE.value:
            connection = settings.CONNECTION.value
        else:
            connection = settings.CONNECTION_TEST.value
        cache_key_response = "ups-cart-%s-response" % int(cart.id)
        cache_key_request = "ups-cart-%s-request" % int(cart.id)
        last_request = cache.get(cache_key_request)
        tree = cache.get(cache_key_response)

        if (last_request != request) or tree is None:
            self.verbose_log("Requesting from UPS [%s]\n%s", cache_key_request, request)
            cache.set(cache_key_request, request, 60)
            tree = self._process_request(connection, request)
            self.verbose_log("Got from UPS [%s]:\n%s", cache_key_response, self.raw)
            needs_cache = True
        else:
            needs_cache = False

        try:
            status_code = tree.getiterator('ResponseStatusCode')
            status_val = status_code[0].text
            self.verbose_log("UPS Status Code for cart #%s = %s", int(cart.id), status_val)
        except AttributeError:
            status_val = "-1"
        
        if status_val == '1':
            self.is_valid = False
            self._calculated = False
            all_rates = tree.getiterator('RatedShipment')
            for response in all_rates:
                if self.service_type_code == response.find('.//Service/Code/').text:
                    self.charges = response.find('.//TotalCharges/MonetaryValue').text
                    if response.find('.//GuaranteedDaysToDelivery').text:
                        self.delivery_days = response.find('.//GuaranteedDaysToDelivery').text
                    self.is_valid = True
                    self._calculated = True
                    if needs_cache:
                        cache.set(cache_key_response, tree, 60)
                        
            if not self.is_valid:
                self.verbose_log("UPS Cannot find rate for code: %s [%s]", self.service_type_code, self.service_type_text)
        
        else:
            self.is_valid = False
            self._calculated = False

            try:
                errors = tree.find('.//Error')
                log.info("UPS %s Error: Code %s - %s" % (errors[0].text, errors[1].text, errors[2].text))
            except AttributeError:
                log.info("UPS error - cannot parse response:\n %s", self.raw)
            
    def verbose_log(self, *args, **kwargs):
        if config_value('shipping.modules.ups', 'VERBOSE_LOG'):
            log.debug(*args, **kwargs)
        
        
