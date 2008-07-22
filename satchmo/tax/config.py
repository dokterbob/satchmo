from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from satchmo.configuration import *
from satchmo.utils import is_string_like, load_module

TAX_GROUP = ConfigurationGroup('TAX', _('Tax Settings'))

config_register([

StringValue(TAX_GROUP,
    'MODULE',
    description=_("Active tax module"),
    help_text=_("Select a module, save and reload to set any module-specific settings."),
    default="satchmo.tax.modules.no",
    choices=[('satchmo.tax.modules.no', _('No Tax')),
    ]
),

BooleanValue(TAX_GROUP,
    'DEFAULT_VIEW_TAX',
    description=_("Show with tax included"),
    help_text=_("If yes, then all products and the cart will display with tax included."),
    default=False
),

])

# --- Load default tax modules.  Ignore import errors, user may have deleted them. ---
_default_modules = ('percent','area')

for module in _default_modules:
    try:
        load_module("satchmo.tax.modules.%s.config" % module)
    except ImportError:
        log.debug('Could not load default tax module configuration: %s', module)


    
# --- Load any extra tax modules. ---
extra_tax = getattr(settings, 'CUSTOM_TAX_MODULES', ())

for extra in extra_tax:
    try:
        load_module("%s.config" % extra)
    except ImportError:
        log.warn('Could not load tax module configuration: %s' % extra)
