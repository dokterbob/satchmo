# By Neum Schmickrath 
# www.pageworthy.com
from django.utils.translation import ugettext_lazy as _
from livesettings import *

SHIP_MODULES = config_get('SHIPPING', 'MODULES')
SHIP_MODULES.add_choice(('shipping.modules.fedex', 'FEDEX'))

SHIPPING_GROUP = ConfigurationGroup('shipping.modules.fedex',
  _('FedEx Shipping Settings'),
  requires = SHIP_MODULES,
  requiresvalue='shipping.modules.fedex',
  ordering = 101
)

config_register_list(

    StringValue(SHIPPING_GROUP,
        'METER_NUMBER',
        description=_('FedEx Meter Number'),
        help_text=_('Meter Number provided by FedEx.'),
        default=u''),
    
    StringValue(SHIPPING_GROUP,
        'ACCOUNT',
        description=_('FedEx Account Number'),
        help_text=_('FedEx Account Number.'),
        default=u''),
    
    MultipleStringValue(SHIPPING_GROUP,
        'SHIPPING_CHOICES',
        description=_('FedEx Shipping Choices Available to customers.'),
        choices = (
                    (('PRIORITYOVERNIGHT','Priority Overnight')),
                    (('STANDARDOVERNIGHT','Standard Overnight')),
                    (('FIRSTOVERNIGHT', 'First Overnight')),
                    (('FEDEX2DAY','2 Day')),
                    (('FEDEXEXPRESSSAVER','Express Saver')),
                    (('INTERNATIONALPRIORITY','International Priority')),
                    (('INTERNATIONALECONOMY', 'International Economy')),
                    (('INTERNATIONALFIRST', 'International First')),
                    (('FEDEX1DAYFREIGHT', '1 Day Freight')),
                    (('FEDEX2DAYFREIGHT', '2 Day Freight')),
                    (('FEDEX3DAYFREIGHT', '3 Day Freight')),
                    (('FEDEXGROUND','Ground')),
                    (('GROUNDHOMEDELIVERY', 'Ground Home Delivery')),
                    (('INTERNATIONALPRIORITYFREIGHT', 'International Priority Freight')),
                    (('INTERNATIONALECONOMYFREIGHT','International Economy Freight')),
                    (('EUROPEFIRSTINTERNATIONALPRIORITY', 'Europe International Priority')),

        ),
        default = ('FEDEXGROUND',)),

    StringValue(SHIPPING_GROUP,
        'SHIPPING_PACKAGE',
        description = _('Type of container/package used to ship product.'),
        choices = (
                    (('FEDEXENVELOPE','FEDEXENVELOPE')),
                    (('FEDEXPAK','FEDEXPAK')),
                    (('FEDEXBOX','FEDEXBOX')),
                    (('FEDEXTUBE','FEDEXTUBE')),
                    (('FEDEX10KGBOX','FEDEX10KGBOX')),
                    (('FEDEX25KGBOX','FEDEX25KGBOX')),
                    (('YOURPACKAGING','YOURPACKAGING')),
        ),
        default = u'FEDEXENVELOPE'),

    BooleanValue(SHIPPING_GROUP,
        'LIVE',
        description=_('Access production FedEx server'),
        help_text=_('Use this when your store is in production.'),
        default=False),

    StringValue(SHIPPING_GROUP,
        'CONNECTION',
        description=_('Submit to URL'),
        help_text=_('Address to submit live transactions.'),
        default='https://gateway.fedex.com/GatewayDC'),

    StringValue(SHIPPING_GROUP,
        'CONNECTION_TEST',
        description=_('Submit to TestURL'),
        help_text=_('Address to submit test transactions.'),
        default='https://gatewaybeta.fedex.com/GatewayDC'),
    
    BooleanValue(SHIPPING_GROUP,
        'SINGLE_BOX',
        description=_("Single Box?"),
        help_text=_("Use just one box and ship by weight?  If no then every item will be sent in its own box."),
        default=True),

    BooleanValue(SHIPPING_GROUP,
        'VERBOSE_LOG',
        description=_("Verbose logs"),
        help_text=_("Send the entire request and response to the log - for debugging help when setting up FedEx."),
        default=False)
)
