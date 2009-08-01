from django import template
from django.template.loader import render_to_string
from livesettings import config_value
from satchmo_ext.productratings.utils import get_product_rating_string, get_product_rating
import logging

log = logging.getLogger('shop.templatetags')

register = template.Library()

def product_rating_form(request, product, form):
    """Output our product comment form with the proper redirect in it."""
    log.debug('returning product rating form for %s', product)
    return {
        "form" : form,
        "product" : product,
        "user" : request.user,
    }

register.inclusion_tag('productratings/product_rating_form.html')(product_rating_form)

def product_ratings(context):
    """
    Display the ratings for a specific product.
    """
    shop = context['shop']
    rendered = render_to_string('productratings/_product_ratings.html', context)
    return { 'rendered_product_ratings': rendered }

register.inclusion_tag('productratings/_render_product_ratings.html', takes_context=True)(product_ratings)
        
def product_rating_average_string(product): 
    """Get the average product rating as a string, for use in templates"""   
    return get_product_rating_string(product)

register.filter("product_rating_average_string", product_rating_average_string)

def product_rating_average(product):  
    """Get the average product rating as a number"""  
    return get_product_rating(product)

register.filter("product_rating_average", product_rating_average)
