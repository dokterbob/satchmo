from django.utils.translation import ugettext_lazy as _
from livesettings import *
import logging
log = logging.getLogger('shipping.modules.productshipping')
from shipping.config import SHIPPING_ACTIVE

SHIPPING_ACTIVE.add_choice(('shipping.modules.productshipping', _('Shipping By Product')))

log.debug('loaded')
