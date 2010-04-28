from django.template import Library
from l10n.utils import moneyfmt

register = Library()

def option_price(option_item):
    """
    Returns the price as (+$1.00)
    or (-$1.00) depending on the sign of the price change
    The currency symbol is set in the settings.py file
    """
    output = ""
    if option_item.price_change != 0:
        amount = moneyfmt(abs(option_item.price_change))
    if option_item.price_change < 0:
        output = "(- %s)" % amount
    if option_item.price_change > 0:
        output = "(+ %s)" % amount
    return output

register.simple_tag(option_price)

def option_total_price(product, option_item):
    """
    Returns the price as (+$1.00)
    or (-$1.00) depending on the sign of the price change
    The currency symbol is set in the settings.py file
    """
    if option_item.price_change:
        val = product.unit_price + option_item.price_change
    else:
        val = product.unit_price
    return moneyfmt(val)

register.simple_tag(option_total_price)
