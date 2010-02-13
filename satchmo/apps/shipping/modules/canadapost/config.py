'''
Canada Post Shipping Module
v0.1.1
'''
from django.utils.translation import ugettext_lazy as _
from livesettings import *

SHIP_MODULES = config_get('SHIPPING', 'MODULES')
SHIP_MODULES.add_choice(('shipping.modules.canadapost', 'Canada Post'))

SHIPPING_GROUP = ConfigurationGroup('shipping.modules.canadapost',
  _('Canada Post Shipping Settings'),
  requires = SHIP_MODULES,
  requiresvalue='shipping.modules.canadapost',
  ordering = 101
)

config_register_list(

    StringValue(SHIPPING_GROUP,
        'CPCID',
        description=_('Canada Post Merchant ID'),
        help_text=_('The merchant ID assigned by Canada Post'),
        default=u'CPC_DEMO_XML'),

    #http://sellonline.canadapost.ca/DevelopersResources/protocolV3/ProductID.html
    MultipleStringValue(SHIPPING_GROUP,
        'CANADAPOST_SHIPPING_CHOICES',
        description=_("Canada Post shipping choices available to customers."),
        choices = (
            (('1010', 'Domestic - Regular')),
            (('1020', 'Domestic - Expedited')),
            (('1030', 'Domestic - Xpresspost')),            
            (('1040', 'Domestic - Priority Courier')),
            (('2005', 'US - Small Packets Surface')),
            (('2015', 'US - Small Packets Air')),
            (('2020', 'US - Expedited US Business Contract')),
            (('2025', 'US - Expedited US Commercial')),
            (('2030', 'US - Xpress USA')),
            (('2040', 'US - Priority Worldwide USA')),
            (('2050', 'US - Priority Worldwide PAK USA')),
            (('3005', 'Int`l - Small Packets Surface')),
            (('3010', 'Int`l - Surface International')),
            (('3015', 'Int`l - Small Packets Air')),
            (('3020', 'Int`l - Air International')),
            (('3025', 'Int`l - Xpresspost International')),
            (('3040', 'Int`l - Priority Worldwide INTL')),
            (('3050', 'Int`l - Priority Worldwide PAK INTL')),
        ),
        default = ('1010','1020','1030','1040',)),

    StringValue(SHIPPING_GROUP,
        'SHIPPING_CONTAINER',
        description=_("Type of container used to ship product."),
        choices = (
            (('00', 'Unknown')),
            (('01', 'Variable')),
            (('02', 'Rectangular')),
        ),
        default = u"00"),

    BooleanValue(SHIPPING_GROUP,
        'LIVE',
        description=_('Access production Canada Post server'),
        help_text=_('Use this when your store is in production.'),
        default=False),

    StringValue(SHIPPING_GROUP,
        'CONNECTION',
        description=_('Submit to URL'),
        help_text=_('Canada Post Sell Online server to submit live transactions.'),
        default='http://sellonline.canadapost.ca:30000'),

    StringValue(SHIPPING_GROUP,
        'CONNECTION_TEST',
        description=_('Submit to TestURL'),
        help_text=_('Canada Post Sell Online server to submit test transactions.'),
        default='http://sellonline.canadapost.ca:30000'),

    StringValue(SHIPPING_GROUP,
        'TURN_AROUND_TIME',
        description=_('Turn around time'),
        help_text=_('Turn around time in hours. If declared here, this parameter \
                    will overwrite the one defined in the merchant\'s profile'),
        default='24'),

    BooleanValue(SHIPPING_GROUP,
        'VERBOSE_LOG',
        description=_("Verbose logs"),
        help_text=_("Send the entire request and response to the log - for debugging help when setting up Canada Post."),
        default=False)
)
