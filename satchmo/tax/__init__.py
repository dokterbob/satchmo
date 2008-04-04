from satchmo.configuration import config_value
from satchmo.shop.utils import load_module

try:
    import decimal
except ImportError:
    from django.utils import _decimal as decimal    # for Python 2.3

TWOPLACES = decimal.Decimal('0.01')

def get_processor(order=None, user=None):
    modulename = config_value('TAX','MODULE')
    mod = load_module(modulename + u'.tax')
    return mod.Processor(order=order,user=user)
    
def round_cents(x):
    return x.quantize(TWOPLACES, decimal.ROUND_FLOOR)
