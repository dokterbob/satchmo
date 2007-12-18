from django.utils.translation import ugettext_lazy as _
from satchmo.configuration import *

TAX_MODULE = config_get('TAX', 'MODULE')
TAX_MODULE.add_choice(('satchmo.tax.modules.area', _('By Country/Area')))
TAX_GROUP = config_get_group('TAX')

# config_register([
#     DecimalValue(TAX_GROUP,
#     'PERCENT',
#     description=_("Percent tax"),
#     requires=TAX_MODULE,
#     requiresvalue='satchmo.tax.modules.area'),
#     
#     BooleanValue(TAX_GROUP,
#     'TAX_SHIPPING',
#     description=_("Tax Shipping?"),
#     requires=TAX_MODULE,
#     requiresvalue='satchmo.tax.modules.area'
#     default=False)    
# ])
