from decimal import Decimal
from django.utils.translation import ugettext_lazy as _
from livesettings import *

SHIP_MODULES = config_get('SHIPPING', 'MODULES')
SHIP_MODULES.add_choice(('shipping.modules.usps', 'USPS'))

SHIPPING_GROUP = ConfigurationGroup('shipping.modules.usps',
    _('U.S.P.S. Shipping Settings'),
    requires = SHIP_MODULES,
    ordering = 101)

config_register_list(

StringValue(SHIPPING_GROUP,
    'USER_ID',
    description=_("USPS  Username"),
    help_text=_("User ID provided by USPS site."),
    default=u""),

StringValue(SHIPPING_GROUP,
    'USER_PASSWORD',
    description=_("USPS Password"),
    help_text=_("User password provided by USPS site."),
    default=u""),

DecimalValue(SHIPPING_GROUP,
    'HANDLING_FEE',
    description=_("Handling Fee"),
    help_text=_("The cost of packaging and taking order to post office"),
    default=Decimal('0.00')),

MultipleStringValue(SHIPPING_GROUP,
    'USPS_SHIPPING_CHOICES',
    description=_("USPS Shipping Choices Available to customers."),
    choices = (
        (('0', 'First Class')),
        (('1', 'Priority Mail')),
        (('16', 'Priority Mail Flat-Rate Envelope')),
        (('17', 'Priority Mail Flat-Rate Box')),
        (('22', 'Priority Mail Large Flat-Rate Box')),
        (('3', 'Express Mail')),
        (('13', 'Express Mail Flat-Rate Envelope')),
        (('4', 'Parcel Post')),
        (('5', 'Bound Printed Matter')),
        (('6', 'Media Mail')),
        (('7', 'Library Mail')),
        
        # INTERNATIONAL CODES
        
        (('14', 'Int`l: First Class Mail International Large Envelope')),
        (('15', 'Int`l: First Class Mail International Package')),
        (('1', 'Int`l: Express Mail International (EMS)')),
        (('4', 'Int`l: Global Express Guaranteed')),
        (('6', 'Int`l: Global Express Guaranteed Non-Document Rectangular')),
        (('7', 'Int`l: Global Express Guaranteed Non-Document Non-Rectangular')),
        (('10', 'Int`l: Express Mail International (EMS) Flat-Rate Envelope')),
        (('2', 'Int`l: Priority Mail International')),
        (('8', 'Int`l: Priority Mail International Flat-Rate Envelope')),
        (('9', 'Int`l: Priority Mail International Flat-Rate Box')),
        (('11', 'Int`l: Priority Mail International Large Flat-Rate Box')),
        (('12', 'Int`l: USPS GXG Envelopes')),
    ),
    default = ('3',)),

StringValue(SHIPPING_GROUP,
    'SHIPPING_CONTAINER',
    description=_("Type of container used to ship product."),
    choices = (
        (('00', 'Unknown')),
        (('01', 'Variable')),
        (('02', 'Flat rate box')),
        (('03', 'Flat rate envelope')),
        (('04', 'Rectangular')),
        (('05', 'Non-rectangular')),
    ),
    default = u"01"),

BooleanValue(SHIPPING_GROUP,
    'LIVE',
    description=_("Access production USPS server"),
    help_text=_("Use this when your store is in production."),
    default=False),

StringValue(SHIPPING_GROUP,
    'CONNECTION',
    description=_("Submit to URL"),
    help_text=_("Address to submit live transactions."),
    default="http://production.shippingapis.com/ShippingAPI.dll"),

StringValue(SHIPPING_GROUP,
    'CONNECTION_TEST',
    description=_("Submit to Test URL"),
    help_text=_("Address to submit test transactions."),
    default="http://testing.shippingapis.com/ShippingAPITest.dll"),

BooleanValue(SHIPPING_GROUP,
    'VERBOSE_LOG',
    description=_("Verbose logs"),
    help_text=_("Send the entire request and response to the log - for debugging help when setting up USPS."),
    default=False),

#ModuleValue(SHIPPING_GROUP,
#    'MODULE',
#    description=_('Implementation module'),
#    hidden=True,
#    default = 'shipping.modules.ups'),

)
