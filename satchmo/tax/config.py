from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from satchmo.configuration import *
from satchmo.shop.utils import is_string_like, load_module

TAX_GROUP = ConfigurationGroup('TAX', _('Tax Settings'))

TAX_MODULE = config_register(StringValue(TAX_GROUP,
    'MODULE',
    description=_("Active tax module"),
    help_text=_("Select a module, save and reload to set any module-specific settings."),
    default="satchmo.tax.modules.no",
    choices=[('satchmo.tax.modules.percent', _('Percent Tax')),
            ('satchmo.tax.modules.no', _('No Tax'))]
    ))

config_register([

    DecimalValue(TAX_GROUP,
    'PERCENT',
    description=_("Percent tax"),
    requires=TAX_MODULE,
    requiresvalue='satchmo.tax.modules.percent'),
    
    BooleanValue(TAX_GROUP,
    'TAX_SHIPPING',
    description=_("Tax Shipping?"),
    default=False)    
])
    
# --- Load any extra tax modules. ---
extra_tax = getattr(settings, 'CUSTOM_TAX_MODULES', ())

for extra in extra_tax:
    try:
        load_module("%s.config" % extra)
    except ImportError:
        log.warn('Could not load tax module configuration: %s' % extra)
