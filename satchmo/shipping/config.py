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
    choices=[('satchmo.shipping.modules.per', _('Per piece'))]
    ))
    
# --- Load default shipping modules.  Ignore import errors, user may have deleted them. ---
_default_modules = ('dummy', 'flat', 'per')

for module in _default_modules:
    try:
        load_module("satchmo.shipping.modules.%s.config" % module)
    except ImportError:
        log.debug('Could not load default shipping module configuration: %s', module)

# --- Load any extra shipping modules. ---
extra_shipping = getattr(settings, 'CUSTOM_SHIPPING_MODULES', ())

for extra in extra_shipping:
    try:
        load_module("%s.config" % extra)
    except ImportError:
        log.warn('Could not load shipping module configuration: %s' % extra)

class ShippingModuleNotFound(Exception):
    def __init__(key):
        self.key = key

def shipping_methods():
    methods = []
    for m in config_value('SHIPPING', 'MODULES'):
        module = load_module(m)
        methods.extend(module.get_methods())
    return methods
    
def shipping_method_by_key(key):
    if key:
        for method in shipping_methods():
            if method.id == key:
                return method
    else:
        import satchmo.shipping.modules.no.shipper as noship
        method = noship.Shipper()
        
    if method:
        return method
    else:
        raise ShippingModuleNotFound(key)
        

def shipping_choices():
    choices = []
    keys = []
    for method in shipping_methods():
        key = method.id
        label = method.description()
        choices.append((key, label))
    return choices