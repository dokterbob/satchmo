# -*- coding: utf-8 -*-

import urlparse
import os
from satchmo.configuration import config_register, BooleanValue, StringValue, MultipleStringValue, SHOP_GROUP, ConfigurationGroup, PositiveIntegerValue
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

install_path = ((hasattr(settings, 'SATCHMO_DIRNAME') and SATCHMO_DIRNAME) or \
                settings.DIRNAME)
default_icon_url = urlparse.urlunsplit(
    ('file',
     '',
     os.path.join(install_path, 'templates/pdf/sample-logo.bmp'),
     '',
     '')
    )

#### SHOP Group ####

CURRENCY = config_register(
    StringValue(SHOP_GROUP, 
        'CURRENCY', 
        description= _("Default currency symbol"),
        help_text= _("Use a '_' character to force a space."),
        default="$"))

ENABLE_RATINGS = config_register(
    BooleanValue(SHOP_GROUP, 
        'RATINGS', 
        description= _("Enable product ratings"), 
        default=True))
        
RANDOM_FEATURED = config_register(
    BooleanValue(SHOP_GROUP,
        'RANDOM_FEATURED',
        description= _("Enable random display of featured products on home page"),
        default=False))

NUMBER_FEATURED = config_register(
    PositiveIntegerValue(SHOP_GROUP,
        'NUM_DISPLAY',
        description= _("Total number of featured items to display"),
        default=20))

NUMBER_PAGINATED = config_register(
    PositiveIntegerValue(SHOP_GROUP,
        'NUM_PAGINATED',
        description= _("Number of featured items to display on each page"),
        default=10))

MEASUREMENT_SYSTEM = config_register(
    MultipleStringValue(SHOP_GROUP,
    'MEASUREMENT_SYSTEM',
    description = _("Measurement system to use in store"),
    choices = [('metric',_('Metric')),
                ('imperial',_('Imperial'))],
    default = "imperial"))

LOGO_URI = config_register(
    StringValue(SHOP_GROUP,
    'LOGO_URI',
    description = _("URI to the logo for the store"),
    help_text = _(("For example http://www.example.com/images/logo.jpg or "
                   "file:///var/www/html/images/logo.jpg")),
    default = default_icon_url
))
                
#### Google Group ####

GOOGLE_GROUP = ConfigurationGroup('GOOGLE', _('Google Settings'))

GOOGLE_ANALYTICS = config_register(
    BooleanValue(GOOGLE_GROUP, 
        'ANALYTICS', 
        description= _("Enable Analytics"), 
        default=False,
        ordering=0))

GOOGLE_USE_URCHIN = config_register(
    BooleanValue(GOOGLE_GROUP, 
        'USE_URCHIN', 
        description= _("Use Urchin?"), 
        help_text=_("Use the old-style, urchin javascript?.  This is not needed unless your analytics account hasn't been updated yet."),
        default = False,
        ordering=5,
        requires = GOOGLE_ANALYTICS))
        
GOOGLE_ANALYTICS_CODE = config_register(
    StringValue(GOOGLE_GROUP, 
        'ANALYTICS_CODE', 
        description= _("Analytics Code"), 
        default = "",
        ordering=5,
        requires = GOOGLE_ANALYTICS))
    
GOOGLE_ADWORDS = config_register(
    BooleanValue(GOOGLE_GROUP, 
        'ADWORDS', 
        description= _("Enable Conversion Tracking"), 
        default=False,
        ordering=10))
        
GOOGLE_ADWORDS_ID = config_register(
    StringValue(GOOGLE_GROUP, 
        'ADWORDS_ID', 
        description= _("Adwords ID (ex: UA-abcd-1)"), 
        default = "",
        ordering=15,
        requires = GOOGLE_ADWORDS))

LANGUAGE_GROUP = ConfigurationGroup('LANGUAGE',_('Language Settings'))

LANGUAGE_ALLOW_TRANSLATIONS = config_register(
    BooleanValue(LANGUAGE_GROUP,
    'ALLOW_TRANSLATION',
    description=_("Allow user to choose from available translations"),
    default=False,
    ordering=1))

LANGUAGES_AVAILABLE = config_register(
    MultipleStringValue(LANGUAGE_GROUP,
    'LANGUAGES_AVAILABLE',
    requires = LANGUAGE_ALLOW_TRANSLATIONS,
    description = _("Available languages"),
    help_text=_("Languages that have valid translations"),
    choices=[('en', "English"),
            ('fr', "Français"),
            ('de',"Deutsch"),
            ('es', "Español"),
            ('ko', "한국어"),
            ('sv', "Svenska"),
            ('pt-br',"Português"),
            ('bg',"Български")]
    ))
    
