from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from satchmo.configuration import *
from satchmo.shop.utils import is_string_like, load_module

SHIPPING_GROUP = ConfigurationGroup('SHIPPING', _('Shipping Settings'))

SHIPPING_ACTIVE = config_register(MultipleStringValue(SHIPPING_GROUP,
    'MODULES',
    description=_("Active shipping modules"),
    help_text=_("Select the active shipping modules, save and reload to set any module-specific shipping settings."),
    default=["satchmo.shipping.modules.per"],
    choices=[('satchmo.shipping.modules.flat', _('Flat rate')),
             ('satchmo.shipping.modules.per', _('Per piece'))]
    ))
    
config_register([

DecimalValue(SHIPPING_GROUP,
    'FLAT_RATE',
    description=_("Flat shipping"),
    requires=SHIPPING_ACTIVE,
    requiresvalue='satchmo.shipping.modules.flat',
    default="4.00"),

StringValue(SHIPPING_GROUP,
    'FLAT_SERVICE',
    description=_("Flat Shipping Service"),
    help_text=_("Shipping service used with Flat rate shipping"),
    requires=SHIPPING_ACTIVE,
    requiresvalue='satchmo.shipping.modules.flat',
    default=u"U.S. Mail"),
    
StringValue(SHIPPING_GROUP,
    'FLAT_DAYS',
    description=_("Flat Delivery Days"),
    requires=SHIPPING_ACTIVE,
    requiresvalue='satchmo.shipping.modules.flat',
    default="3 - 4 business days"),

DecimalValue(SHIPPING_GROUP,
    'PER_RATE',
    description=_("Per item price"),
    requires=SHIPPING_ACTIVE,
    requiresvalue='satchmo.shipping.modules.per',
    default="4.00"),

StringValue(SHIPPING_GROUP,
    'PER_SERVICE',
    description=_("Per Item Shipping Service"),
    help_text=_("Shipping service used with per item shipping"),
    requires=SHIPPING_ACTIVE,
    requiresvalue='satchmo.shipping.modules.per',
    default=u"U.S. Mail"),

StringValue(SHIPPING_GROUP,
    'PER_DAYS',
    description=_("Per Item Delivery Days"),
    requires=SHIPPING_ACTIVE,
    requiresvalue='satchmo.shipping.modules.per',
    default="3 - 4 business days")

])

# --- Load any extra payment modules. ---
extra_payment = getattr(settings, 'CUSTOM_SHIPPING_MODULES', ())

for extra in extra_payment:
    try:
        load_module("%s.config" % extra)
    except ImportError:
        log.warn('Could not load payment module configuration: %s' % extra)
