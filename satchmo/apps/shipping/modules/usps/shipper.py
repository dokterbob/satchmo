"""
USPS Shipping Module
You must have a USPS account to use this module.
You may register at usps.com

This module uses the XML online tools for maximum flexibility.  It is
primarily created for use in the US but reconfiguring for international
shipping or more advanced uses should be straightforward.

It is recommended that you refer to the USPS shipper developer documents
(available when you register at USPS) in order to tailor this to your
unique needs.
"""

# Note, make sure you use decimal math everywhere!
from decimal import Decimal
from django.core.cache import cache
from django.template import Context, loader
from django.utils.translation import ugettext as _
from l10n.models import Country
from livesettings import config_get_group, config_value
from shipping.modules.base import BaseShipper
import logging
import urllib2
try:
    from xml.etree.ElementTree import fromstring, tostring
except ImportError:
    from elementtree.ElementTree import fromstring, tostring

"""
The different class codes for each type of mail.  Some types of mail have
several sub-options.
"""
CODES = {'0': 'FIRST CLASS',
         '1': 'PRIORITY',
         '16': 'PRIORITY',
         '17': 'PRIORITY',
         '22': 'PRIORITY',
         '3': 'EXPRESS',
         '13': 'EXPRESS',
         '4': 'PARCEL',
         '5': 'BPM',
         '6': 'MEDIA',
         '7': 'LIBRARY',
         
         # these are here to avoid KeyErrors
         '2': 'INTL',
         '8': 'INTL',
         '9': 'INTL',
         '10': 'INTL',
         '11': 'INTL',
         '12': 'INTL',
         '14': 'INTL',
         '15': 'INTL',
        }
        
"""
International service codes

        (('14', 'First Class Mail International Large Envelope')),
        (('15', 'First Class Mail International Package')),
        (('1', 'Express Mail International (EMS)')),
        (('4', 'Global Express Guaranteed')),
        (('6', 'Global Express Guaranteed Non-Document Rectangular')),
        (('7', 'Global Express Guaranteed Non-Document Non-Rectangular')),
        (('10', 'Express Mail International (EMS) Flat-Rate Envelope')),
        (('2', 'Priority Mail International')),
        (('8', 'Priority Mail International Flat-Rate Envelope')),
        (('9', 'Priority Mail International Flat-Rate Box')),
        (('11', 'Priority Mail International Large Flat-Rate Box')),
        (('12', 'USPS GXG Envelopes')),
"""

"""
These are the deliver estimates from the website at
http://www.usps.com/webtools/htm/DomMailServStandv1-0.htm#_Toc82841084
"""
ESTIMATES = {'FIRST CLASS': '3 - 5',
             'PRIORITY': '1 - 3',
             'EXPRESS': '1 - 2',
             'PARCEL': '2 - 9',
             'BPM': '2 - 9',
             'MEDIA': '2 - 9',
             'LIBRARY': '2 - 9',
             'INTL': '',
            }

"""
A list of API's for each type of mail service
"""
APIS = {'PRIORITY': 'PriorityMail',
        'EXPRESS': 'ExpressMailCommitment',
        'PARCEL': 'StandardB',
        'BPM': 'StandardB',
        'MEDIA': 'StandardB',
        'LIBRARY': 'StandardB',
        'INTL': '',
       }

log = logging.getLogger('usps.shipper')
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
        self.id = u"USPS-%s-%s" % (self.service_type_code, self.service_type_text)
        self.raw = "NO DATA"
        self.exact_date = False
        #if cart or contact:
        #    self.calculate(cart, contact)

    def __str__(self):
        """
        This is mainly helpful for debugging purposes
        """
        return "U.S. Postal Service"

    def description(self):
        """
        A basic description that will be displayed to the user when selecting their shipping options
        """
        return _("USPS - %s" % self.service_type_text.replace('Int`l: ', ''))

    def cost(self):
        """
        Complex calculations can be done here as long as the return value is a decimal figure
        """
        assert(self._calculated)
        settings =  config_get_group('shipping.modules.usps')
        if settings.HANDLING_FEE and float(str(settings.HANDLING_FEE)) > 0.0:
            self.charges = Decimal(self.charges) + Decimal(str(settings.HANDLING_FEE))
        return Decimal(str(self.charges))

    def method(self):
        """
        Describes the actual delivery service (Mail, FedEx, DHL, UPS, etc)
        """
        return _("USPS")

    def expectedDelivery(self):
        """
        Can be a plain string or complex calcuation returning an actual date
        """
        if self.exact_date:
            if self.is_intl:
                return _('in %s' % self.delivery_days.lower())
            return _("by %s" % self.delivery_days.replace('-', ' '))
        elif self.delivery_days != "1":
            return _("in %s business days" % self.delivery_days)
        else:
            return _("in %s business day" % self.delivery_days)

    def valid(self, order=None):
        """
        Can do complex validation about whether or not this option is valid.
        For example, may check to see if the recipient is in an allowed country
        or location.
        """
        return self.is_valid

    def _process_request(self, connection, request, api=None):
        """
        Post the data and return the XML response
        """
        # determine which API to use
        if api == None:
            if self.is_intl:
                api = 'IntlRate'
            else:
                api = 'RateV3'

        data = 'API=%s&XML=%s' % (api, request.encode('utf-8'))

        conn = urllib2.Request(url=connection, data=data)
        f = urllib2.urlopen(conn)
        all_results = f.read()

        log.error(all_results)

        return (fromstring(all_results))

    def render_template(self, template, cart=None, contact=None):
        from satchmo_store.shop.models import Config
        shop_details = Config.objects.get_current()
        settings =  config_get_group('shipping.modules.usps')

        if not self.is_intl:
            mail_type = CODES[self.service_type_code]
            if mail_type == 'INTL': return ''
        
            if mail_type == 'FIRST CLASS':
                self.api = None
            else:
                self.api = APIS[mail_type]
        else:
            mail_type = None
            self.api = None
        
        # calculate the weight of the entire order
        weight = Decimal('0.0')
        for item in cart.cartitem_set.all():
            if item.product.smart_attr('weight'):
                weight += item.product.smart_attr('weight') * item.quantity
        self.verbose_log('WEIGHT: %s' % weight)

        # I don't know why USPS made this one API different this way...
        if self.api == 'ExpressMailCommitment':
            zip_ending = 'ZIP'
        else:
            zip_ending = 'zip'

        # get the shipping country (for the international orders)
        ship_country = contact.shipping_address.country.printable_name

        configuration = {
            'userid': settings.USER_ID.value,
            'password': settings.USER_PASSWORD.value,
            'container': settings.SHIPPING_CONTAINER.value,
            'ship_type': mail_type,
            'shop_details': shop_details
        }
        c = Context({
                'config': configuration,
                'cart': cart,
                'contact': contact,
                'is_international': self.is_intl,
                'api': self.api,
                'weight': weight,
                'zip': zip_ending,
                'country': ship_country,
                'first_class_types': ['LETTER', 'FLAT', 'PARCEL']
        })
        t = loader.get_template(template)
        return t.render(c)

    def calculate(self, cart, contact):
        """
        Based on the chosen USPS method, we will do our call to USPS and see how
        much it will cost. We will also need to store the results for further 
        parsing and return via the methods above
        """
        from satchmo_store.shop.models import Config
        settings =  config_get_group('shipping.modules.usps')
        shop_details = Config.objects.get_current()
        self.is_intl = contact.shipping_address.country.iso2_code != shop_details.country.iso2_code
        self.delivery_days = ESTIMATES[CODES[self.service_type_code]]

        if not self.is_intl:
            template = 'shipping/usps/request.xml'
        else:
            template = 'shipping/usps/request_intl.xml'
        request = self.render_template(template, cart, contact)
        self.is_valid = False

        if settings.LIVE.value:
            connection = settings.CONNECTION.value
        else:
            connection = settings.CONNECTION_TEST.value

        cache_key_response = "usps-cart-%s-response" % int(cart.id)
        cache_key_request = "usps-cart-%s-request" % int(cart.id)
        last_request = cache.get(cache_key_request)

        tree = cache.get(cache_key_response)

        if (last_request != request) or tree is None:
            self.verbose_log("Requesting from USPS [%s]\n%s", cache_key_request, request)
            cache.set(cache_key_request, request, 60)
            tree = self._process_request(connection, request)
            self.verbose_log("Got from USPS [%s]:\n%s", cache_key_response, self.raw)
            needs_cache = True
        else:
            needs_cache = False

        errors = tree.getiterator('Error')

        # if USPS returned no error, return the prices
        if errors == None or len(errors) == 0:
            # check for domestic results first
            all_packages = tree.getiterator('RateV3Response')

            # if there are none, revert to international results
            if len(all_packages) == 0:
                all_packages = tree.getiterator('IntlRateResponse')
                for package in all_packages:
                    for service in package.getiterator('Service'):
                        #self.verbose_log('%s vs %s' % (service.attrib['ID'], self.service_type_code))
                        if service.attrib['ID'] == self.service_type_code and \
                            self.service_type_text.startswith('Int`l: '):
                            
                            self.charges = service.find('.//Postage/').text
                            self.delivery_days = service.find('.//SvcCommitments/').text
                            #self.verbose_log('%s %s' % (self.charges, self.delivery_days))
                            self.is_valid = True
                            self._calculated = True
                            self.exact_date = True

                            #if needs_cache:
                            #    cache.set(cache_key_response, tree, 60)
            else:
                for package in all_packages:
                    for postage in package.getiterator('Postage'):
                        if postage.attrib['CLASSID'] == self.service_type_code and \
                            not self.service_type_text.startswith('Int`l: '):
                            self.charges = postage.find('.//Rate/').text

                            # Now try to figure out how long it would take for this delivery
                            if self.api:
                                delivery = self.render_template('shipping/usps/delivery.xml', cart, contact)
                                del_tree = self._process_request(connection, delivery, self.api)
                                parent = '%sResponse' % self.api
                                del_iter = del_tree.getiterator(parent)

                                if len(del_iter):
                                    i = del_iter[0]

                                    # express mail usually has a date commitment
                                    if self.api == 'ExpressMailCommitment':
                                        key = './/Date/'
                                        self.exact_date = True
                                    else:
                                        key = './/Days/'
                                    if i.find(key) != None:
                                        self.delivery_days = i.find(key).text

                            self.is_valid = True
                            self._calculated = True

                            #if needs_cache:
                            #    cache.set(cache_key_response, tree, 60)
        else:
            error = errors[0]
            err_num = error.find('.//Number').text
            source = error.find('.//Source').text
            description = error.find('.//Description').text
            log.info("USPS Error: Code %s: %s" % (err_num, description))

    def verbose_log(self, *args, **kwargs):
        if config_value('shipping.modules.usps', 'VERBOSE_LOG'):
            log.debug(*args, **kwargs)
