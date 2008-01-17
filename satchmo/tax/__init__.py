from satchmo.configuration import config_value
from satchmo.shop.utils import load_module
import decimal

TWOPLACES = decimal.Decimal('0.01')

def get_processor(order=None, user=None):
    modulename = config_value('TAX','MODULE')
    mod = load_module(modulename + u'.tax')
    return mod.Processor(order=order,user=user)
    
def round_cents(x):
    return x.quantize(TWOPLACES, decimal.ROUND_FLOOR)
