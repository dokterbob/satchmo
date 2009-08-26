from django.utils.translation import ugettext_lazy as _
from livesettings import *

TAX_MODULE = config_get('TAX', 'MODULE')
TAX_MODULE.add_choice(('tax.modules.us_sst', _('USA: Streamlined Sales Tax')))
TAX_GROUP = config_get_group('TAX')

# varies state-to-state, so we need to support this being variable.
config_register(
     BooleanValue(TAX_GROUP,
         'TAX_SHIPPING',
         description=_("Tax Shipping in ANY jurisdiction?"),
         requires=TAX_MODULE,
         requiresvalue='tax.modules.us_sst',
         default=True)
)

config_register(
     StringValue(TAX_GROUP,
         'TAX_CLASS',
         description=_("TaxClass for shipping"),
         help_text=_("Select a TaxClass that should be applied for shipments."),
         #TODO: [BJK] make this dynamic - doesn't work to have it be preloaded.
         default='Shipping'
     )
)
