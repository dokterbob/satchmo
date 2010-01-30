# -*- coding: UTF-8 -*-
"""A central mechanism forsettings which have defaults.

Repurposed from Sphene Community Tools: http://sct.sphene.net
"""

from django.conf import settings
import logging
log = logging.getLogger('l10n.l10n_settings')

l10n_settings_defaults = {
    # (or global settings) -- all other defaults should be added using
    # the add_setting_defaults method !

    'currency_formats' : {
        'USD' : {'symbol': u'$', 'positive' : u"$%(val)0.2f", 'negative': u"-$%(val)0.2f", 'decimal' : '.'},
        'GBP' : {'symbol': u'£', 'positive' : u"£%(val)0.2f", 'negative': u"-£%(val)0.2f", 'decimal' : '.'},
    },
    
    'default_currency' : 'USD',
    'show_translations': True,  #Display in the admin
    'allow_translations' : True, #Display the list of languages to store user
}


def add_setting_defaults(newdefaults):
    """
    This method can be used by other applications to define their
    default values.
    
    newdefaults has to be a dictionary containing name -> value of
    the settings.
    """
    l10n_settings_defaults.update(newdefaults)


def set_l10n_setting(name, value):
    if not hasattr(settings, 'L10N_SETTINGS'):
        settings.L10N_SETTINGS = {}
    settings.L10N_SETTINGS[name] = value
    

def get_l10n_setting(name, default_value = None):
    if not hasattr(settings, 'L10N_SETTINGS'):
        return l10n_settings_defaults.get(name, default_value)

    return settings.L10N_SETTINGS.get(name, l10n_settings_defaults.get(name, default_value))

def get_l10n_default_currency_symbol():
    key = get_l10n_setting('default_currency', default_value='USD')
    try:
        return get_l10n_setting('currency_formats')[key]['symbol']
    except KeyError:
        log.warn('could not find default currency symbol, please make sure you have a L10N_SETTINGS in your settings file, and that it has a default currency.')
        return "$"
