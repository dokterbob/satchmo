from django import template
from satchmo.shop.templatetags import get_filter_args

register = template.Library()

@register.inclusion_tag('giftcertificate/_order_summary.html')
def giftcertificate_order_summary(order):
    """Output a formatted block giving attached gift certifificate details."""
    return {'order' : order}
    

