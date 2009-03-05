'''
FedEx Shipping Module
v0.4
By Neum Schmickrath - www.pageworthy.com

You must have a Fedex account to use this module.
You may register at fedex.com
'''

from decimal import Decimal
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe 
from django.template import loader, Context
from django.core.cache import cache

from shipping.modules.base import BaseShipper
from shipping import signals
from livesettings import config_get_group

import urllib2
from xml.dom import minidom
import logging

log = logging.getLogger('fedex.shipper')

class Shipper(BaseShipper):
    
    def __init__(self, cart=None, contact=None, service_type=None):

        self._calculated = False
        self.cart = cart
        self.contact = contact
        self.raw_results = '(not processed)'

        if service_type:    
            self.service_type_code = service_type[0]
            self.service_type_text = service_type[1]

        else:
            self.service_type_code = '99'
            self.service_type_text = 'Uninitialized'
# Had to edit this so the shipping name did not error out for being more than 30 characters. Old code is commented out.
        #self.id = u'FedEx-%s-%s' % (self.service_type_code, self.service_type_text)
        self.id = u'%s' % (self.service_type_text)

        #if cart or contact:
        #  self.calculate(cart, contact)
  
    def __str__(self):
        '''
          This is mainly helpful for debugging purposes
        '''

        return 'FedEx'


    def __unicode__(self):
        '''
          As is this.
        '''

        return 'FedEx'
    
    def description(self):
        '''
          A basic description that will be displayed to the user when 
          selecting their shipping options
        '''

        return _('FedEx - %s' % self.service_type_text)

    def cost(self):
        '''
          Complex calculations can be done here as long as the return 
          value is a decimal figure
        '''

        assert(self._calculated)
        return(Decimal(self.charges))

    def method(self):
        '''
          Describes the actual delivery service (Mail, FedEx, DHL, UPS, etc)
        '''

        return _('FedEx')

    def expectedDelivery(self):
        '''
          Can be a plain string or complex calcuation 
          returning an actual date
        '''

        if self.delivery_days <> '1':
            return _('%s business days' % self.delivery_days)
        else:
            return _('%s business day' % self.delivery_days)
    
    def valid(self, order=None):
        '''
        Can do complex validation about whether or not this
        option is valid. For example, may check to see if the 
        recipient is in an allowed country or location.
        '''

        return self.is_valid

    def _check_for_error(self, response):
        '''
          Check XML response, see if it indicates an error.
          Expects 'response' to already have been run through
          minidom.parseString()
        '''
    
        if response.getElementsByTagName('Error'):
            # we have an error!
            error_code = response.getElementsByTagName('Error')[0].getElementsByTagName('Code')[0].firstChild.nodeValue
            error_mesg = response.getElementsByTagName('Error')[0].getElementsByTagName('Message')[0].firstChild.nodeValue
            log.info('Fedex Error: %s - Code: %s', error_mesg, error_code)
            return (error_mesg, error_code)

        else:
            # all clear.
            return False

    def _process_request(self, connection, request):
        '''
          Post the data and return the XML response
        '''

        conn = urllib2.Request(url=connection, data=request)
        f = urllib2.urlopen(conn)
        all_results = f.read()
        self.raw_response = all_results
        return(minidom.parseString(all_results))
    
    def calculate(self, cart, contact):
        '''
          Based on the chosen Fedex method, we will do our call(s) 
          to FedEx and see how much it will cost. We will also need 
          to store the results for further parsing and return via the
          methods above.
        '''
        log.debug("Starting fedex calculations")

        from satchmo_store.shop.models import Config
        settings =  config_get_group('shipping.modules.fedex')

        verbose = settings.VERBOSE_LOG.value
            
        self.delivery_days = _('3 - 4') #Default setting for ground delivery
        shop_details = Config.objects.get_current()
        self.packaging = ''


        # FedEx Ground Home Delivery Packaging must be YOURPACKAGING only.
        if self.service_type_code in ('FEDEXGROUND', 'GROUNDHOMEDELIVERY'):
            self.packaging = 'YOURPACKAGING'
        else:
            self.packaging = settings.SHIPPING_PACKAGE.value

        if verbose:
            log.debug('Calculating fedex with type=%s, packaging=%s', self.service_type_code, self.packaging)

        self.is_valid = False
        error = False

        if not settings.ACCOUNT.value:
            log.warn("No fedex account found in settings")
            return
        
        if not settings.METER_NUMBER.value:
            log.warn("No fedex meter number found in settings")
            return

        configuration = {
            'account': settings.ACCOUNT.value,
            'meter': settings.METER_NUMBER.value,
            'packaging': self.packaging,
            'ship_type': self.service_type_code,
            'shop_details':shop_details,
        }

        if settings.LIVE.value:
            connection = settings.CONNECTION.value
        else:
            connection = settings.CONNECTION_TEST.value
            

        self.charges = 0
        
        box_weight_units = "LB"

        # FedEx requires that the price be formatted to 2 decimal points.
        # e.g., 1.00, 10.40, 3.50

        # They also require that the weight be one decimal point. 
        # e.g., 1.0, 2.3, 10.4
        
        if settings.SINGLE_BOX.value:
            if verbose:
                log.debug("Using single-box method for fedex calculations.")
                
            box_price = Decimal("0.00")
            box_weight = Decimal("0.00")
            for product in cart.get_shipment_list():
                box_price += product.unit_price
                if product.weight is None:
                    log.warn("No weight on product (skipping for ship calculations): %s", product)
                else:
                    box_weight += product.weight
                if product.weight_units and product.weight_units != "":
                    box_weight_units = product.weight_units
            
            if box_weight < Decimal("0.1"):
                log.debug("Total box weight too small, defaulting to 0.1")
                box_weight = Decimal("0.1")
                
            shippingdata = {
                'config': configuration,
                'box_price': '%.2f' % box_price,
                'box_weight' : '%.1f' % box_weight,
                'box_weight_units' : box_weight_units.upper(),
                'contact': contact,
                'shipping_address' : shop_details,
                'shipping_phone' : shop_details.phone,
                'shipping_country_code' : shop_details.country.iso2_code
            }
            signals.shipping_data_query.send(Shipper, shipper=self, cart=cart, shippingdata=shippingdata)

            c = Context(shippingdata)
            t = loader.get_template('shipping/fedex/request.xml')
            request = t.render(c)

            try:
                response = self._process_request(connection, request)
                error = self._check_for_error(response)
            
                if verbose:
                    log.debug("Fedex request: %s", request)
                    log.debug("Fedex response: %s", self.raw_response)

                if not error:
                    this_charge = float(response.documentElement.getElementsByTagName('NetCharge')[0].firstChild.nodeValue)
                    this_discount = float(response.documentElement.getElementsByTagName('EffectiveNetDiscount')[0].firstChild.nodeValue)
                    self.delivery_days = response.documentElement.getElementsByTagName('TimeInTransit')[0].firstChild.nodeValue

                    total_cost = this_charge + this_discount
                    self.charges += total_cost
            except urllib2.URLError:
                log.warn("Error opening url: %s", connection)
                error = True
                
        else:
            # process each shippable separately

            # I'm not certain why FedEx implemented their 'Web Service' 
            # this way. However, you can't give FedEx a list of boxes 
            # and get back a list of prices (as you can with UPS). 
            # Each box has to be a completely new transaction - that 
            # is, a separate POST to their server.
            #
            # So, to simulate this functionality, and return a total 
            # price, we have to loop through all of our items, and 
            # pray the customer isn't ordering a thousand boxes of bagels.
            for product in cart.get_shipment_list():
                c = Context({
                  'config': configuration,
                  'box_weight' : '%.1f' % (product.weight or 0.0),
                  'box_weight_units' : product.weight_units and product.weight_units.upper() or 'LB',
                  'box_price' : '%.2f' % product.unit_price,
                  'contact': contact,
                })
    
                t = loader.get_template('shipping/fedex/request.xml')
                request = t.render(c)

                response = self._process_request(connection, request)
                error = self._check_for_error(response)
                
                if verbose:
                    log.debug("Fedex request: %s", request)
                    log.debug("Fedex response: %s", self.raw_response)

                if not error:
                    this_charge = float(response.documentElement.getElementsByTagName('NetCharge')[0].firstChild.nodeValue)
                    this_discount = float(response.documentElement.getElementsByTagName('EffectiveNetDiscount')[0].firstChild.nodeValue)
                    self.delivery_days = response.documentElement.getElementsByTagName('TimeInTransit')[0].firstChild.nodeValue

                    total_cost = this_charge + this_discount
                    self.charges += total_cost
                    
                else:
                    break

        if not error:
            self.charges = str(self.charges)
            self.is_valid = True
            self._calculated = True

