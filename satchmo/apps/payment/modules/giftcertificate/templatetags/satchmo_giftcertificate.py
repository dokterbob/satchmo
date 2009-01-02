from django import template
from satchmo_utils.templatetags import get_filter_args

register = template.Library()

def giftcertificate_order_summary(order):
    """Output a formatted block giving attached gift certifificate details."""
    return {'order' : order}
    
register.inclusion_tag('giftcertificate/_order_summary.html')(giftcertificate_order_summary)
