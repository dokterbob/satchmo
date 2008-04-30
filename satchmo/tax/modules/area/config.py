from django.utils.translation import ugettext_lazy as _
from satchmo.configuration import * 
from satchmo.tax.models import TaxClass

TAX_MODULE = config_get('TAX', 'MODULE')
TAX_MODULE.add_choice(('satchmo.tax.modules.area', _('By Country/Area')))
TAX_GROUP = config_get_group('TAX')

_tax_classes = []
ship_default = ""
for tax in TaxClass.objects.all():
     _tax_classes.append( (tax.title, tax.title) )
     if "ship" in tax.title.lower():
         ship_default = tax.title
         
if ship_default == "" and len(_tax_classes) > 0:
    ship_default = _tax_classes[0].title

config_register([
#     DecimalValue(TAX_GROUP,
#     'PERCENT',
#     description=_("Percent tax"),
#     requires=TAX_MODULE,
#     requiresvalue='satchmo.tax.modules.area'),
#     
     BooleanValue(TAX_GROUP,
     'TAX_SHIPPING',
     description=_("Tax Shipping?"),
     requires=TAX_MODULE,
     requiresvalue='satchmo.tax.modules.area',
     default=False) ,
     
     StringValue(TAX_GROUP,
         'TAX_CLASS',
         description=_("TaxClass for shipping"),
         help_text=_("Select a TaxClass that should be applied for shipments."),
         default=ship_default,
         choices=_tax_classes
     ),    
 ])
