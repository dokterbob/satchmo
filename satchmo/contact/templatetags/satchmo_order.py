from django import template

register = template.Library()

@register.inclusion_tag('contact/_order_details.html')
def order_details(order):
    """Output a formatted block giving order details."""
    return {'order' : order}

@register.inclusion_tag('contact/_order_tracking_details.html')
def order_tracking_details(order):
    """Output a formatted block giving order tracking details."""
    return {'order' : order}
