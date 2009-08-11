from decimal import Decimal
from django import template
from django.conf import settings
from django.core import urlresolvers
from django.template import Context, Template
from django.utils.translation import get_language, ugettext_lazy as _
from livesettings import config_value
from product.utils import calc_discounted_by_percentage, find_best_auto_discount
from satchmo_utils.templatetags import get_filter_args
from tax.templatetags import satchmo_tax

register = template.Library()

def sale_price(product):
    """Returns the sale price, including tax if that is the default."""
    if config_value('TAX', 'DEFAULT_VIEW_TAX'):
        return taxed_sale_price(product)
    else:
        return untaxed_sale_price(product)

register.filter('sale_price', sale_price)

def untaxed_sale_price(product):
    """Returns the product unit price with the best auto discount applied."""
    discount = find_best_auto_discount(product)
    price = product.unit_price
        
    if discount and discount.valid_for_product(product):
        price = calc_discounted_by_percentage(price, discount.percentage)
    
    return price

register.filter('untaxed_sale_price', untaxed_sale_price)

def taxed_sale_price(product):
    """Returns the product unit price with the best auto discount applied and taxes included."""
    taxer = satchmo_tax._get_taxprocessor()
    price = untaxed_sale_price(product)
    price = price + taxer.by_price(product.taxClass, price)
    return price

register.filter('taxed_sale_price', taxed_sale_price)

def discount_cart_total(cart, discount):
    """Returns the discounted total for this cart, with tax if that is the default."""
    if config_value('TAX', 'DEFAULT_VIEW_TAX'):
        return taxed_discount_cart_total(cart, discount)
    else:
        return untaxed_discount_cart_total(cart, discount)

register.filter('discount_cart_total', discount_cart_total)

def untaxed_discount_cart_total(cart, discount):
    """Returns the discounted total for this cart"""
    total = Decimal('0.00')
    
    for item in cart:
        total += untaxed_discount_line_total(item, discount)
    return total
        
register.filter('untaxed_discount_cart_total', untaxed_discount_cart_total)

def taxed_discount_cart_total(cart, discount):
    """Returns the discounted total for this cart with taxes included"""
    total = Decimal('0.00')
    
    for item in cart:
        total += taxed_discount_line_total(item, discount)
        
    return total
        
register.filter('taxed_discount_cart_total', taxed_discount_cart_total)

def discount_line_total(cartitem, discount):
    """Returns the discounted line total for this cart item, including tax if that is the default."""
    if config_value('TAX', 'DEFAULT_VIEW_TAX'):
        return taxed_discount_line_total(cartitem, discount)
    else:
        return untaxed_discount_line_total(cartitem, discount)

    
register.filter('discount_line_total', discount_line_total)

def untaxed_discount_line_total(cartitem, discount):
    """Returns the discounted line total for this cart item"""
    price = cartitem.line_total
    if discount and discount.valid_for_product(cartitem.product):
        price = calc_discounted_by_percentage(price, discount.percentage)
    
    return price
        
register.filter('untaxed_discount_line_total', untaxed_discount_line_total)

def taxed_discount_line_total(cartitem, discount):
    """Returns the discounted line total for this cart item with taxes included."""
    price = untaxed_discount_line_total(cartitem, discount)
    taxer = satchmo_tax._get_taxprocessor()
    price = price + taxer.by_price(cartitem.product.taxClass, price)
    
    return price
        
register.filter('taxed_discount_line_total', taxed_discount_line_total)

def discount_price(product, discount):
    """Returns the product price with the discount applied, including tax if that is the default.
    
    Ex: product|discount_price:sale
    """
    if config_value('TAX', 'DEFAULT_VIEW_TAX'):
        return taxed_discount_price(product, discount)
    else:
        return untaxed_discount_price(product, discount)


register.filter('discount_price', discount_price)
   
def untaxed_discount_price(product, discount):
    """Returns the product price with the discount applied.
    
    Ex: product|discount_price:sale
    """
    up = product.unit_price
    if discount and discount.valid_for_product(product):
        pcnt = calc_discounted_by_percentage(up, discount.percentage)
        return pcnt
    else:
        return up

register.filter('untaxed_discount_price', untaxed_discount_price)

def taxed_discount_price(product, discount):
    """Returns the product price with the discount applied, and taxes included.
    
    Ex: product|discount_price:sale
    """
    price = untaxed_discount_price(product, discount)
    taxer = satchmo_tax._get_taxprocessor()
    return price + taxer.by_price(product.taxClass, price)

register.filter('taxed_discount_price', taxed_discount_price)

def discount_ratio(discount):
    """Returns the discount as a ratio, making sure that the percent is under 1"""
    pcnt = discount.percentage
    if pcnt > 1:
        pcnt = pcnt/100
    
    return 1-pcnt

register.filter('discount_ratio', discount_ratio)

def discount_saved(product, discount):
    """Returns the amount saved by the discount, including tax if that is the default."""
    if config_value('TAX', 'DEFAULT_VIEW_TAX'):
        return taxed_discount_saved(product, discount)
    else:
        return untaxed_discount_saved(product, discount)

register.filter('discount_saved', discount_saved)


def untaxed_discount_saved(product, discount):
    """Returns the amount saved by the discount"""
    
    if discount and discount.valid_for_product(product):
        price = product.unit_price
        discounted = untaxed_discount_price(product, discount)
        saved = price - discounted
        cents = Decimal("0.01")
        return saved.quantize(cents)
    else:
        return Decimal('0.00')

register.filter('untaxed_discount_saved', untaxed_discount_saved)

def taxed_discount_saved(product, discount):
    """Returns the amount saved by the discount, after applying taxes."""
    
    if discount and discount.valid_for_product(product):
        price = product.unit_price
        discounted = taxed_discount_price(product, discount)
        saved = price - discounted
        cents = Decimal("0.01")
        return saved.quantize(cents)
    else:
        return Decimal('0.00')

register.filter('taxed_discount_saved', taxed_discount_saved)
