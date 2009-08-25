import logging

from django.utils.translation import ugettext_lazy as _
from livesettings import *

log = logging.getLogger('tieredweight.config')

from shipping.config import SHIPPING_ACTIVE

SHIPPING_ACTIVE.add_choice(('shipping.modules.tieredweight', _('Tiered Weight Shipping')))

log.debug('loaded')