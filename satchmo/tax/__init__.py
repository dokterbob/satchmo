from satchmo.configuration import config_value
from satchmo.shop.utils import load_module

def get_processor(order=None, user=None):
    modulename = config_value('TAX','MODULE')
    mod = load_module(modulename + u'.tax')
    return mod.Processor(order=order,user=user)
    