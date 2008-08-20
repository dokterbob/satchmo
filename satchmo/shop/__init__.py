from satchmo_settings import get_satchmo_setting

if get_satchmo_setting('MULTISHOP'):
    from threaded_multihost import multihost_patch

class OutOfStockError(Exception):
    
    def __init__(self, product, have, need):
        self.product = product
        self.have = have
        self.need = need

