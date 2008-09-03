from django import template
from django.conf import settings
from django.core import urlresolvers
from django.template import Context, Template
from django.utils.translation import get_language, ugettext_lazy as _
from satchmo.configuration import config_value
from satchmo.product.models import Category
from satchmo.shop.templatetags import get_filter_args

register = template.Library()

def is_producttype(product, ptype):
    """Returns True if product is ptype"""
    if ptype in product.get_subtypes():
        return True
    else:
        return False

register.filter('is_producttype', is_producttype)

def product_images(product, args=""):
    args, kwargs = get_filter_args(args,
        keywords=('include_main', 'maximum'),
        boolargs=('include_main'),
        intargs=('maximum'),
        stripquotes=True)

    q = product.productimage_set
    if kwargs.get('include_main', True):
        q = q.all()
    else:
        main = product.main_image
        q = q.exclude(id = main.id)

    maximum = kwargs.get('maximum', -1)
    if maximum>-1:
        q = list(q)[:maximum]

    return q

register.filter('product_images', product_images)

def smart_attr(product, key):
    """Run the smart_attr function on the spec'd product
    """
    return product.smart_attr(key)

register.filter('smart_attr', smart_attr)

def product_sort_by_price(products):
    """Sort a product list by unit price"""
    
    fast = [(product.unit_price, product) for product in products]
    fast.sort()
    return zip(*fast)[1]
    
register.filter('product_sort_by_price', product_sort_by_price)
