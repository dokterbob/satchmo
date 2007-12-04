from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import get_language, to_locale
from satchmo.configuration import config_value
import locale
import logging

log = logging.getLogger('l10n.utils')

def get_locale_conv(loc=None):
    startloc = loc
    if not loc:
        loc = to_locale(get_language())

    # '-' is a language delimiter, not a locale, but people often mess that up
    if loc.find('-') > -1:
        loc = to_locale(loc)

    try:
        log.debug('setting locale: %s', loc)
        locale.setlocale(locale.LC_ALL, locale.normalize(loc))
        return locale.localeconv()
    except locale.Error:
        # darn, try a different path
        pos = loc.find('_')
        if pos>-1:
            loc = loc[:pos]
            return get_locale_conv(loc)
        else:
            loc = settings.LANGUAGE_CODE
            if loc != startloc:
                log.warn("Cannot set locale to '%s', using default locale '%s'", startloc, loc)
                return get_locale_conv(loc)
        
            else:
                log.fatal("Cannot set locale to default locale '%s', something is misconfigured", loc)
                raise ImproperlyConfigured("Bad settings LANGUAGE_CODE")
                
def moneyfmt(val, curr=None, places=-1, grouping=True, wrapcents='', current_locale=None):
    """Formats val according to the currency settings in the current locale.
    Ported-and-modified from Python 2.5
    """
    conv = get_locale_conv(current_locale)

    if places < 0:
        places = conv['int_frac_digits']
    s = locale.format('%%.%if' % places, abs(val), grouping, monetary=True)
    # '<' and '>' are markers if the sign must be inserted between symbol and value
    s = '<' + s + '>'

    if curr is None:
        curr = config_value('SHOP', 'CURRENCY')
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
        pos = s.rfind(conf['decimal_point'])
        if pos>-1:
            pos +=1 
            val = u"%s<%s>%s</%s>" % val[:pos], wrapcents, val[pos:], wrapcents

    return val
