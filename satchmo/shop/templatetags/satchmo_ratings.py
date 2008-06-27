import logging
from django.template import Library
from satchmo.product.comments import get_product_rating_string
from satchmo.configuration import config_value

log = logging.getLogger('shop.templatetags')

register = Library()

def product_ratings(context):
    shop = context['shop']
    rendered = ''
    if config_value('SHOP', 'RATINGS'):
        from django.template.loader import render_to_string
        rendered = render_to_string('_product_ratings.html', context)
    return { 'rendered_product_ratings': rendered }

register.inclusion_tag('_render_product_ratings.html', takes_context=True)(product_ratings)
        
def product_rating_average_string(product):    
    return get_product_rating_string(product)

register.filter("product_rating_average_string", product_rating_average_string)

def product_rating_average(product):    
    return get_product_rating(product)

register.filter("product_rating_average", product_rating_average)
