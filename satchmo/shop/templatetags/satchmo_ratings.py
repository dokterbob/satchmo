import logging
from django.template import Library

log = logging.getLogger('shop.templatetags')

register = Library()

def product_ratings(context):
    shop = context['shop']
    rendered = ''
    if shop.options.SHOP.RATINGS.value:
        from django.template.loader import render_to_string
        rendered = render_to_string('_product_ratings.html', context)
    return { 'rendered_product_ratings': rendered }

register.inclusion_tag('_render_product_ratings.html', takes_context=True)(product_ratings)
