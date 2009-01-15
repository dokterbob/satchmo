from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import get_language, to_locale
from livesettings import config_value
from satchmo_utils.numbers import trunc_decimal
import locale
import logging

log = logging.getLogger('l10n.utils')

def get_locale_conv(loc=None):
    if loc is None:
        loc = to_locale(get_language())
    startloc = loc

    # '-' is a language delimiter, not a locale, but people often mess that up
    if loc.find('-') > -1:
        loc = to_locale(loc)

    try:
        #log.debug('setting locale: %s', loc.encode('utf-8'))
        locale.setlocale(locale.LC_ALL, locale.normalize(loc))
        return locale.localeconv()
    except (locale.Error, ValueError):
        # darn, try a different path
        pos = loc.find('_')
        if pos > -1:
            loc = loc[:pos]
            return get_locale_conv(loc)
        else:
            loc = to_locale(settings.LANGUAGE_CODE)
            if loc != startloc and loc[:loc.find('_')] != startloc:
                log.warn(u"Cannot set locale to '%s'. Using default locale '%s'.", startloc.encode('utf-8'), loc.encode('utf-8'))
                return get_locale_conv(loc)
            else:
                log.fatal(u"Cannot set locale to default locale '%s'. Something is misconfigured.", loc.encode('utf-8'))
                raise ImproperlyConfigured("bad settings.LANGUAGE_CODE")

#backport from python2.5
### Number formatting APIs

# Author: Martin von Loewis
# improved by Georg Brandl

#perform the grouping from right to left
def _group(s, conv, monetary=False):
    thousands_sep = conv[monetary and 'mon_thousands_sep' or 'thousands_sep']
    grouping = conv[monetary and 'mon_grouping' or 'grouping']
    if not grouping:
        return (s, 0)
    result = ""
    seps = 0
    spaces = ""
    if s[-1] == ' ':
        sp = s.find(' ')
        spaces = s[sp:]
        s = s[:sp]
    while s and grouping:
        # if grouping is -1, we are done
        if grouping[0] == locale.CHAR_MAX:
            break
        # 0: re-use last group ad infinitum
        elif grouping[0] != 0:
            #process last group
            group = grouping[0]
            grouping = grouping[1:]
        if result:
            result = s[-group:] + thousands_sep + result
            seps += 1
        else:
            result = s[-group:]
        s = s[:-group]
        if s and s[-1] not in "0123456789":
            # the leading string is only spaces and signs
            return s + result + spaces, seps
    if not result:
        return s + spaces, seps
    if s:
        result = s + thousands_sep + result
        seps += 1
    return result + spaces, seps

#backport from python2.5
def format(percent, value, loc_conv, grouping=False, monetary=False, *additional):
    """Returns the locale-aware substitution of a %? specifier
    (percent).

    additional is for format strings which contain one or more
    '*' modifiers."""
    # this is only for one-percent-specifier strings and this should be checked
    if percent[0] != '%':
        raise ValueError("format() must be given exactly one %char "
                         "format specifier")
    if additional:
        formatted = percent % ((value,) + additional)
    else:
        formatted = percent % value
    # floats and decimal ints need special action!
    if percent[-1] in 'eEfFgG':
        seps = 0
        parts = formatted.split('.')
        if grouping:
            parts[0], seps = _group(parts[0], loc_conv, monetary=monetary)
        decimal_point = loc_conv[monetary and 'mon_decimal_point'
                                              or 'decimal_point']
        formatted = decimal_point.join(parts)
        while seps:
            sp = formatted.find(' ')
            if sp == -1: break
            formatted = formatted[:sp] + formatted[sp+1:]
            seps -= 1
    elif percent[-1] in 'diu':
        if grouping:
            formatted = _group(formatted, monetary=monetary)[0]
    return formatted
               
def moneyfmt(val, curr=None, places=-1, grouping=True, wrapcents='', current_locale=None):
    """Formats val according to the currency settings in the current locale.
    Ported-and-modified from Python 2.5
    """
    conv = get_locale_conv(current_locale)

    if places < 0:
        places = conv['int_frac_digits']
    
    val = trunc_decimal(val, places)
        
    try:    # Required because Python < 2.5 does not have monetary arg
        s = format('%%.%if' % places, abs(val), conv, grouping, monetary=True)
    except TypeError:
        s = format('%%.%if' % places, abs(val), conv, grouping)
    # '<' and '>' are markers if the sign must be inserted between symbol and value
    s = '<' + s + '>'

    if curr is None:
        curr = config_value('LANGUAGE','CURRENCY')
        curr = curr.replace("_", " ")
    precedes = conv[val<0 and 'n_cs_precedes' or 'p_cs_precedes']
    separated = conv[val<0 and 'n_sep_by_space' or 'p_sep_by_space']

    if precedes:
        s = curr + (separated and ' ' or '') + s
    else:
        s = s + (separated and ' ' or '') + curr

    sign_pos = conv[val<0 and 'n_sign_posn' or 'p_sign_posn']
    sign = conv[val<0 and 'negative_sign' or 'positive_sign']

    if sign_pos == 0:
        s = '(' + s + ')'
    elif sign_pos == 1:
        s = sign + s
    elif sign_pos == 2:
        s = s + sign
    elif sign_pos == 3:
        s = s.replace('<', sign)
    elif sign_pos == 4:
        s = s.replace('>', sign)
    else:
        # the default if nothing specified;
        # this should be the most fitting sign position
        s = sign + s

    val = s.replace('<', '').replace('>', '')

    if wrapcents:
        pos = s.rfind(conv['decimal_point'])
        if pos>-1:
            pos +=1 
            val = u"%s<%s>%s</%s>" % val[:pos], wrapcents, val[pos:], wrapcents

    return val
