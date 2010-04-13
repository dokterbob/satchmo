"""A central mechanism for shop-wide settings which have defaults.

Repurposed from Sphene Community Tools: http://sct.sphene.net
"""

from django.conf import settings

satchmo_settings_defaults = {
    # Only settings for core `satchmo` applications are defined here,
    # (or global settings) -- all other defaults should be added using
    # the add_setting_defaults method !

    'SHOP_URLS' : [],
    'SHOP_BASE' : '/shop',
    'MULTISHOP' : False    ,
    'CUSTOM_NEWSLETTER_MODULES' : [],
    'CUSTOM_SHIPPING_MODULES' : [],
    'CUSTOM_PRODUCT_MODULES' : [],
    'CUSTOM_TAX_MODULES' : [],
    'ALLOW_PRODUCT_TRANSLATIONS' : True,
    'COOKIE_MAX_SECONDS' : 60*60*24*30, #one month
    'CATEGORY_SLUG': 'category', # Used for the category url
    'PRODUCT_SLUG' : 'product', # Used for the product url
    'SSL' : False, # Used for checkout pages
    }


def add_setting_defaults(newdefaults):
    """
    This method can be used by other applications to define their
    default values.

    newdefaults has to be a dictionary containing name -> value of
    the settings.
    """
    satchmo_settings_defaults.update(newdefaults)


def set_satchmo_setting(name, value):
    if not hasattr(settings, 'SATCHMO_SETTINGS'):
        settings.SATCHMO_SETTINGS = {}
    settings.SATCHMO_SETTINGS[name] = value


def get_satchmo_setting(name, default_value = None):
    if not hasattr(settings, 'SATCHMO_SETTINGS'):
        return satchmo_settings_defaults.get(name, default_value)

    return settings.SATCHMO_SETTINGS.get(name, satchmo_settings_defaults.get(name, default_value))

