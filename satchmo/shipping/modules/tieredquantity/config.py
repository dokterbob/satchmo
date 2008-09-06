from django.utils.translation import ugettext_lazy as _
from satchmo.shipping.config import SHIPPING_ACTIVE

SHIPPING_ACTIVE.add_choice(('satchmo.shipping.modules.tieredquantity', _('Tiered Quantity')))

