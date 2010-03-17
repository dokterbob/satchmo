from django.db import transaction, DatabaseError
from django.utils.translation import ugettext_lazy as _
from livesettings import * 
from tax.config import TAX_MODULE

TAX_MODULE.add_choice(('tax.modules.area', _('By Country/Area')))
TAX_GROUP = config_get_group('TAX')
        
config_register(
     BooleanValue(TAX_GROUP,
         'TAX_SHIPPING',
         description=_("Tax Shipping?"),
         requires=TAX_MODULE,
         requiresvalue='tax.modules.area',
         default=False)
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

