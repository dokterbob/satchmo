__author__="gary paulson"
__date__ ="$Jan 4, 2009 12:55:44 PM$"

from django import template
from satchmo_utils.templatetags import get_filter_args
from satchmo_utils.numbers import round_decimal, RoundedDecimalError

try:
    from django.utils.safestring import mark_safe
except ImportError:
    mark_safe = lambda s:s

import logging

log = logging.getLogger("satchmo_currency")

register = template.Library()

def normalize_decimal(value, args=""):
    """
    PARTIAL UNIT ROUNDING DECIMAL
    Converts a valid float, integer, or string to a decimal number with a specified
    number of decimal places, performs "partial unit rounding", and decimal normalization.

    Usage:
        val|normalize_decimal
        val|normalize_decimal:'places=2'
        val|normalize_decimal:'places=2:roundfactor=.5'
        val|normalize_decimal:'places=2:roundfactor=.5:normalize=False'

    val
        The value to be converted and optionally formated to decimal.
    places 
        The decimal place precision is defined by integer "places" and
        must be <= the precision defined in the decimal.Decimal context.  roundfactor represents
        the maximum number of decimal places to display if normalize is False.

    roundfactor
        (partial unit rounding factor) If roundfactor is between 0 and 1, roundfactor rounds up
        (positive roundfactor value) or down (negative roundfactor value) in factional "roundfactor" increments.
    
    normalize
        If normalize is True (any value other than False), then rightmost zeros are truncated.

    General Filter/Template Usage.
        normalize_decimal is generally used without parameters in the template.
        Defaults are: places=2, roundfactor=None, normalize=True
        If normalize_decimal is not used as a template filter, the value (quantity)
        will display the full decimal value in the template field.
    """
    
    if value == '' or value is None:
        return value
    args, kwargs = get_filter_args(args,
        keywords=('places','roundfactor', 'normalize'),
        intargs=('places',),
        boolargs=('normalize',), stripquotes=True)

    if not 'places' in kwargs:
        kwargs['places'] = 2

    try:
        return mark_safe(str(round_decimal(val=value, **kwargs)))

    except RoundedDecimalError, e:
        log.error("normalize_decimal error val=%s, id-%s, msg=%s", (e.val, e.id, e.msg))
        return value

register.filter('normalize_decimal', normalize_decimal)
normalize_decimal.is_safe = True
