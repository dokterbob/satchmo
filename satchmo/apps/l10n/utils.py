from decimal import Decimal

from django.core.exceptions import ImproperlyConfigured
from django.utils.safestring import mark_safe
from django.utils.translation import get_language
from l10n.l10n_settings import get_l10n_setting
import logging
import re

# Create a regex to strip out the decimal places with currency formatting
# Example string = u"$%(val)0.2f" so this regex should let us get the 0.2f portion
decimal_fmt = re.compile(r'(\.\d+f)')

log = logging.getLogger('l10n.utils')

# Defined outside the function, so won't be recompiled each time
# moneyfmt is called.
# This is required because some currencies might include a . in the description
decimal_separator = re.compile(r'(\d)\.(\d)')

UNSET = object()

def lookup_translation(obj, attr, language_code=None, version=-1):
    """Get a translated attribute by language.

    If specific language isn't found, returns the attribute from the base object.
    """
    if not language_code:
        language_code = get_language()

    if not hasattr(obj, '_translationcache'):
        obj._translationcache = {}

    short_code = language_code
    pos = language_code.find('_')
    if pos > -1:
        short_code = language_code[:pos]

    else:
        pos = language_code.find('-')
        if pos > -1:
            short_code = language_code[:pos]

    trans = None
    has_key = obj._translationcache.has_key(language_code)
    if has_key:
        if obj._translationcache[language_code] == None and short_code != language_code:
            return lookup_translation(obj, attr, short_code)

    if not has_key:
        q = obj.translations.filter(
            languagecode__iexact = language_code)

        if q.count() == 0:
            obj._translationcache[language_code] = None

            if short_code != language_code:
                return lookup_translation(obj, attr, language_code=short_code, version=version)

            else:
                q = obj.translations.filter(
                    languagecode__istartswith = language_code)

        if q.count() > 0:
            trans = None
            if version > -1:
                trans = q.order_by('-version')[0]
            else:
                # try to get the requested version, if it is available,
                # else fallback to the most recent version
                fallback = None
                for t in q.order_by('-version'):
                    if not fallback:
                        fallback = t
                    if t.version == version:
                        trans = t
                        break
                if not trans:
                    trans = fallback

            obj._translationcache[language_code] = trans

    if not trans:
        trans = obj._translationcache[language_code]

    if not trans:
        trans = obj

    val = getattr(trans, attr, UNSET)
    if trans != obj and (val in (None, UNSET)):
        val = getattr(obj, attr)

    return mark_safe(val)



def moneyfmt(val, currency_code=None, wrapcents='', places=None):
    """Formats val according to the currency settings for the desired currency, as set in L10N_SETTINGS"""
    if val is None or val == '':
       val = Decimal('0')

    currencies = get_l10n_setting('currency_formats')
    currency = None

    if currency_code:
        currency = currencies.get(currency_code, None)
        if not currency:
            log.warn('Could not find currency code definitions for "%s", please look at l10n.l10n_settings for examples.')

    if not currency:
        default_currency_code = get_l10n_setting('default_currency', None)

        if not default_currency_code:
            log.fatal("No default currency code set in L10N_SETTINGS")
            raise ImproperlyConfigured("No default currency code set in L10N_SETTINGS")

        if currency_code == default_currency_code:
            raise ImproperlyConfigured("Default currency code '%s' not found in currency_formats in L10N_SETTINGS", currency_code)

        return moneyfmt(val, currency_code=default_currency_code, wrapcents=wrapcents, places=places)

    # here we are assured we have a currency format

    if val>=0:
        key = 'positive'
    else:
        val = abs(val)
        key = 'negative'
    
    # If we've been passed places, modify the format to use the new value
    if places is None or places == '':
        fmt = currency[key]
    else:
        start_fmt = currency[key]
        fmt_parts = re.split(decimal_fmt, start_fmt)
        new_decimal = u".%sf" % places
        # We need to keep track of all 3 parts because we might want to use
        # () to denote a negative value and don't want to lose the trailing )
        fmt = u''.join([fmt_parts[0], new_decimal, fmt_parts[2]])
    formatted = fmt % { 'val' : val }

    sep = currency.get('decimal', '.')
    if sep != '.':
        formatted = decimal_separator.sub(r'\1%s\2' % sep, formatted)

    if wrapcents:
        pos = formatted.rfind(sep)
        if pos>-1:
            pos +=1
            formatted = u"%s<%s>%s</%s>" % (formatted[:pos], wrapcents, formatted[pos:], wrapcents)

    return formatted
