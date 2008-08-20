from django.utils.translation import ugettext_lazy as _
from satchmo.configuration import *

SHIP_MODULES = config_get('SHIPPING', 'MODULES')
SHIP_MODULES.add_choice(('satchmo.shipping.modules.flat', _('Flat rate')))
SHIPPING_GROUP = config_get_group('SHIPPING')

config_register_list(

    DecimalValue(SHIPPING_GROUP,
        'FLAT_RATE',
        description=_("Flat shipping"),
        requires=SHIP_MODULES,
        requiresvalue='satchmo.shipping.modules.flat',
        default="4.00"),

    StringValue(SHIPPING_GROUP,
        'FLAT_SERVICE',
        description=_("Flat Shipping Service"),
        help_text=_("Shipping service used with Flat rate shipping"),
        requires=SHIP_MODULES,
        requiresvalue='satchmo.shipping.modules.flat',
        default=u"U.S. Mail"),
    
    StringValue(SHIPPING_GROUP,
        'FLAT_DAYS',
        description=_("Flat Delivery Days"),
        requires=SHIP_MODULES,
        requiresvalue='satchmo.shipping.modules.flat',
        default="3 - 4 business days")
)
