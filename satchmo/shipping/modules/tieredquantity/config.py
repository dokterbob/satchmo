from django.utils.translation import ugettext_lazy as _
from satchmo.configuration import *

SHIP_MODULES = config_get('SHIPPING', 'MODULES')
SHIP_MODULES.add_choice(('satchmo.shipping.modules.tieredquantity', _('Tiered Quantity')))
#SHIPPING_GROUP = config_get_group('SHIPPING')
