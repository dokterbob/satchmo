from django.utils.translation import ugettext_lazy as _
from satchmo.configuration import *
import logging
log = logging.getLogger('tiered.config')
from satchmo.shipping.config import SHIPPING_ACTIVE

SHIPPING_ACTIVE.add_choice(('satchmo.shipping.modules.tiered', _('Tiered Shipping')))

log.debug('loaded')
