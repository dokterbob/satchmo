from django.template import Node, NodeList
from django.template import TemplateSyntaxError
from django.template import Library
from product.models import Product
from livesettings import config_value

register = Library()

def recentlyviewed(recent, slug=""):
    """Build a list of recent products, skipping the current one if given."""
    if slug:
        recent = [r for r in recent if slug != r.slug]
    
    rmax = config_value('PRODUCT','RECENT_MAX')
    if len(recent) > rmax:
        recent = recent[:rmax]
    return {
        'recent_products' : recent,
    }
register.inclusion_tag('recentlist/_recently_viewed.html', takes_context=False)(recentlyviewed)