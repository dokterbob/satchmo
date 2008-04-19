from django.template import Node, NodeList
from django.template import TemplateSyntaxError
from django.template import Library
from logging import getLogger
from satchmo.product.models import Product
from satchmo.configuration import config_value

log = getLogger('satchmo_sss')

register = Library()

@register.inclusion_tag('recentlist/_recently_viewed.html')
def recentlyviewed(recent, slug=""):
    """Build a list of recent products, skipping the current one if given."""
    if slug:
        recent = [r for r in recent if slug != r.slug]
    
    rmax = config_value('SHOP','RECENT_MAX')
    if len(recent) > rmax:
        recent = recent[:rmax]
    return {
        'recent_products' : recent,
    }
