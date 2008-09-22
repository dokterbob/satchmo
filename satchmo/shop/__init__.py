from satchmo_settings import get_satchmo_setting
from satchmo.shop import signals
from satchmo.shop.exceptions import *
from satchmo.shop.listeners import veto_out_of_stock
import logging
log = logging.getLogger('satchmo.shop')

if get_satchmo_setting('MULTISHOP'):
    log.debug('patching for multishop')
    from threaded_multihost import multihost_patch

signals.satchmo_cart_add_verify.connect(veto_out_of_stock)
