from django import template
from django.utils import translation
from livesettings import config_get_group, config_get
from satchmo_store.shop.models import ORDER_STATUS 

register = template.Library()

@register.filter
def payment_label(group):
    """convert a payment key into its translated text"""
    if not group.startswith('PAYMENT_'):
        group = "PAYMENT_" + group.upper()
    config = config_get_group(group)
    label = translation.ugettext(config.LABEL.value)
    return label.capitalize()

@register.inclusion_tag('payment/_order_payment_summary.html')
def order_payment_summary(order, paylink=False):
    """Output a formatted block giving attached payment details."""
   
    return {'order' : order,
        'paylink' : paylink}

@register.filter
def status_label(value):
    """convert a order status into its translated text"""
   
    for status, descr in ORDER_STATUS:
        if status == value:
            return descr
    return value
