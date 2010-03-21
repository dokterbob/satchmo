from decimal import Decimal

from django.core.exceptions import ImproperlyConfigured
from django.conf import settings
from django.utils.translation import get_language, to_locale
from l10n.l10n_settings import get_l10n_setting
import logging
import re

log = logging.getLogger('l10n.utils')

# Defined outside the function, so won't be recompiled each time
# moneyfmt is called.
# This is required because some currencies might include a . in the description
decimal_separator = re.compile(r'(\d)\.(\d)')

def moneyfmt(val, currency_code=None, wrapcents=''):
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

        return moneyfmt(val, currency_code=default_currency_code, wrapcents=wrapcents)

    # here we are assured we have a currency format

    if val>=0:
        key = 'positive'
    else:
        val = abs(val)
        key = 'negative'

    fmt = currency[key]
    formatted = fmt % { 'val' : val }

    sep = currency.get('decimal', '.')
    if sep != '.':
        formatted = decimal_separator.sub(r'\1%s\2' % sep, formatted)

    if wrapcents:
        pos = formatted.rfind(sep)
        if pos>-1:
            pos +=1
            formatted = u"%s<%s>%s</%s>" % formatted[:pos], wrapcents, formatted[pos:], wrapcents

    return formatted
