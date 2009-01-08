from django import template
from django.utils.safestring import mark_safe
from l10n.utils import moneyfmt
from satchmo_utils.templatetags import get_filter_args
from shipping.modules.productshipping.models import Carrier

register = template.Library()

def product_shipping(product, args=''):
    if not args:
        raise template.TemplateSyntaxError('product_shipping needs the name of the carrier, as product|productshipping:"carrier"')
    
    try:
        c = Carrier.objects.get(key=args)
    except Carrier.DoesNotExist:
        raise template.TemplateSyntaxError('product_shipping needs the name of a valid carrier, could not find carrier "%s"' % args)
    shipping = c.price(product)
    
    return mark_safe(moneyfmt(shipping))

register.filter(product_shipping)
