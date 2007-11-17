from decimal import Decimal
from django import template
from django.conf import settings
from django.utils.encoding import force_unicode
from satchmo.configuration import config_value
from satchmo.shop.templatetags import get_filter_args
try:
    from django.utils.safestring import mark_safe
except ImportError:
    mark_safe = lambda s:s
    
#The moneyfmt script was taken from the Python decimal recipes.
#See it here - http://docs.python.org/lib/decimal-recipes.html

register = template.Library()


def currency(value, args=""):
    """Convert a value to a money formatted string.

    places:  required number of places after the decimal point
    curr:    optional currency symbol before the sign (may be blank)
    sep:     optional grouping separator (comma, period, space, or blank)
    dp:      decimal point indicator (comma or period)
             only specify as blank when places is zero
    pos:     optional sign for positive numbers: '+', space or blank
    neg:     optional sign for negative numbers: '-', '(', space or blank
    trailneg:optional trailing minus indicator:  '-', ')', space or blank
    wrapcents:tag to wrap the part after the decimal point

    Usage:
        val|currency
        val|currency:'places=2'
        val|currency:'places=2:wrapcents=sup'
    """
    
    if value == '':
        return value

    args, kwargs = get_filter_args(args, 
        keywords=('places','curr','sep','dp','pos','neg','trailneg','wrapcents'),
        intargs=('places',), stripquotes=True)

    value = Decimal(str(value))
        
    return mark_safe(moneyfmt(value, **kwargs))

def moneyfmt(value, places=2, curr=None, sep=',', dp='.',
             pos='', neg='-', trailneg='', wrapcents=''):
    """Convert Decimal to a money formatted string.

    places:  required number of places after the decimal point
    curr:    optional currency symbol before the sign (may be blank)
    sep:     optional grouping separator (comma, period, space, or blank)
    dp:      decimal point indicator (comma or period)
             only specify as blank when places is zero
    pos:     optional sign for positive numbers: '+', space or blank
    neg:     optional sign for negative numbers: '-', '(', space or blank
    trailneg:optional trailing minus indicator:  '-', ')', space or blank
    wrapcents:tag to wrap the part after the decimal point

    >>> d = Decimal('-1234567.8901')
    >>> moneyfmt(d, curr='$')
    '-$1,234,567.89'
    >>> moneyfmt(d, places=0, sep='.', dp='', neg='', trailneg='-')
    '1.234.568-'
    >>> moneyfmt(d, curr='$', neg='(', trailneg=')')
    '($1,234,567.89)'
    >>> moneyfmt(Decimal(123456789), sep=' ')
    '123 456 789.00'
    >>> moneyfmt(Decimal('-0.02'), neg='<', trailneg='>')
    '<.02>'

    """
    if curr is None:
        curr = config_value('SHOP', 'CURRENCY')

    q = Decimal((0, (1,), -places))    # 2 places --> '0.01'
    sign, digits, exp = value.quantize(q).as_tuple()
    assert exp == -places    
    result = []
    digits = map(str, digits)
    build, next = result.append, digits.pop
    if sign:
        build(trailneg)
        
    if wrapcents and places > 0:
        build("</%s>" % wrapcents)
    
    for i in range(places):
        if digits:
            build(next())
        else:
            build('0')

    if wrapcents and places > 0:
        build("<%s>" % wrapcents)
            
    build(dp)
    
    i = 0
    while digits:
        build(next())
        i += 1
        if i == 3 and digits:
            i = 0
            build(sep)
    build(force_unicode(curr))
    if sign:
        build(neg)
    else:
        build(pos)
    result.reverse()
    return u''.join(result)

register.filter('currency', currency)
currency.is_safe = True
