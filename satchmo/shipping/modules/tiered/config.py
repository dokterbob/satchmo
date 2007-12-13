from django.utils.translation import ugettext_lazy as _
from satchmo.configuration import *

SHIP_MODULES = config_get('SHIPPING', 'MODULES')
SHIP_MODULES.add_choice(('satchmo.shipping.modules.tiered', _('Tiered Shipping')))
SHIPPING_GROUP = config_get_group('SHIPPING')
