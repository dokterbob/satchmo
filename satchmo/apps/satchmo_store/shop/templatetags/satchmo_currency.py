from decimal import Decimal, InvalidOperation
from django import template
from django.utils.safestring import mark_safe
from l10n.utils import moneyfmt
from satchmo_utils.templatetags import get_filter_args

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

    return mark_safe(moneyfmt(value, **kwargs))

register.filter('currency', currency)
currency.is_safe = True
