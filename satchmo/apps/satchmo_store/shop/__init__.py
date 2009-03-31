from satchmo_settings import get_satchmo_setting
import logging

log = logging.getLogger('satchmo_store.shop')

if get_satchmo_setting('MULTISHOP'):
    log.debug('patching for multishop')
    from threaded_multihost import multihost_patch
