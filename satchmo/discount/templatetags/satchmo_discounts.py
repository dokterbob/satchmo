try:
    from decimal import Decimal
except:
    from django.utils._decimal import Decimal
from django import template
from django.conf import settings
from django.core import urlresolvers
from django.template import Context, Template
from django.utils.translation import get_language, ugettext_lazy as _
from satchmo.discount.utils import calc_by_percentage, find_best_auto_discount
from satchmo.configuration import config_value
from satchmo.shop.templatetags import get_filter_args

register = template.Library()

def sale_price(product):
    """Returns the product unit price with the best auto discount applied."""
    disc = find_best_auto_discount(product)
    price = product.unit_price
    if disc:
        return calc_by_percentage(price, disc.percentage)
    else:
        return price

register.filter('sale_price', sale_price)

def discount_cart_total(cart, discount):
    """Returns the discounted line total for this cart item"""
    if discount:
        total = Decimal('0.00')
    
        for item in cart:
            total += discount_line_total(item, discount)
    else:
        total = cart.total
        
    return total
        
register.filter('discount_cart_total', discount_cart_total)

def discount_line_total(cartitem, discount):
    """Returns the discounted line total for this cart item"""
    lt = cartitem.line_total
    if discount and discount.valid_for_product(cartitem.product):
        return calc_by_percentage(lt, discount.percentage)
    else:
        return lt
        
register.filter('discount_line_total', discount_line_total)
   
def discount_price(product, discount):
    """Returns the product price with the discount applied.
    
    Ex: product|discount_price:sale
    """
    up = product.unit_price
    if discount and discount.valid_for_product(product):
        return calc_by_percentage(up, discount.percentage)
    else:
        return up

register.filter('discount_price', discount_price)

def discount_ratio(discount):
    """Returns the discount as a ratio, making sure that the percent is under 1"""
    pcnt = discount.percentage
    if pcnt > 1:
        pcnt = pcnt/100
    
    return 1-pcnt

register.filter('discount_ratio', discount_ratio)

def discount_saved(product, discount):
    """Returns the amount saved by the discount"""
    
    if discount and discount.valid_for_product(product):
        price = product.unit_price
        discounted = calc_by_percentage(price, discount.percentage)
        saved = price-discounted
        cents = Decimal("0.01")
        return saved.quantize(cents)
    else:
        return Decimal('0.00')

register.filter('discount_saved', discount_saved)


