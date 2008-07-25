try:
    from decimal import Decimal, InvalidOperation
except:
    from django.utils._decimal import Decimal, InvalidOperation

from django import template
from django.conf import settings
from django.utils.encoding import force_unicode
from satchmo.configuration import config_value
from satchmo.shop.templatetags import get_filter_args
from satchmo.l10n.utils import moneyfmt
try:
    from django.utils.safestring import mark_safe
except ImportError:
    mark_safe = lambda s:s

import logging

log = logging.getLogger("satchmo_currency")

register = template.Library()

def currency(value, args=""):
    """Convert a value to a money formatted string.

    places:  required number of places after the decimal point
    curr:    optional currency symbol before the sign (may be blank)
    wrapcents:tag to wrap the part after the decimal point

    Usage:
        val|currency
        val|currency:'places=2'
        val|currency:'places=2:wrapcents=sup'
    """
    
    if value == '' or value is None:
        return value

    args, kwargs = get_filter_args(args, 
        keywords=('places','curr', 'wrapcents'),
        intargs=('places',), stripquotes=True)

    try:
        value = Decimal(str(value))
    except InvalidOperation:
        log.error("Could not convert value '%s' to decimal", value)
        raise
        
    if not 'places' in kwargs:
        kwargs['places'] = 2
        
    return mark_safe(moneyfmt(value, **kwargs))

register.filter('currency', currency)
currency.is_safe = True
