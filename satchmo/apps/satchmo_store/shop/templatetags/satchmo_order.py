from django import template

from livesettings import config_get_group
from satchmo_utils.templatetags import get_filter_args

register = template.Library()

def order_details(context, order, default_view_tax=False):
    """Output a formatted block giving order details."""
    return {'order' : order,
        'default_view_tax' : default_view_tax,
        'request' : context['request']
    }

register.inclusion_tag('shop/_order_details.html', takes_context=True)(order_details)

def order_tracking_details(order, paylink=False, default_view_tax=False):
    """Output a formatted block giving order tracking details."""
    return {'order' : order,
        'default_view_tax': default_view_tax,
        'paylink' : paylink }

register.inclusion_tag('shop/_order_tracking_details.html')(order_tracking_details)

def order_variable(order, args):
    """
    Get a variable from an order

    Sample usage::

      {{ order|order_variable:'variable' }}

    """
    args, kwargs = get_filter_args(args)
    if not len(args == 1):
        raise template.TemplateSyntaxError("%r filter expected variable, got: %s" % (args[0], args))

    return order.get_variable(args[0])

register.filter(order_variable)

# def giftcertificate(order):
#     """Get the giftcertificate from the order, if any"""
#     try:
#         return GiftCertificate.objects.from_order(order)
#     except GiftCertificate.DoesNotExist:
#         pass
#
#     return None
#
# register.filter(giftcertificate)

@register.filter
def order_payment_methods(order):
    """
    Returns a list of payment method labels for an order.

    Usage::

      {{ order|order_payment_methods|join:", " }}

    """
    return (config_get_group('PAYMENT_%s' % p.payment).LABEL.value
             for p in order.payments.all())
