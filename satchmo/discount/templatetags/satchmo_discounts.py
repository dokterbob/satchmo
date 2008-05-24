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
