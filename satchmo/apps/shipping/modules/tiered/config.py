from django.utils.translation import ugettext_lazy as _
from livesettings import *
import logging
log = logging.getLogger('tiered.config')
from shipping.config import SHIPPING_ACTIVE

SHIPPING_ACTIVE.add_choice(('shipping.modules.tiered', _('Tiered Shipping')))

log.debug('loaded')
