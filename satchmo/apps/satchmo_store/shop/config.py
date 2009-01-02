# -*- coding: utf-8 -*-

import os
import urlparse
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from livesettings import config_register, BooleanValue, StringValue, MultipleStringValue, ConfigurationGroup, PositiveIntegerValue

SHOP_GROUP = ConfigurationGroup('SHOP', _('Satchmo Shop Settings'), ordering=0)

default_icon_url = urlparse.urlunsplit(
    ('file',
     '',
     os.path.join(settings.MEDIA_ROOT, 'images/sample-logo.bmp'),
     '',
     '')
    )

#### SHOP Group ####

LOGO_URI = config_register(
    StringValue(SHOP_GROUP,
    'LOGO_URI',
    description = _("URI to the logo for the store"),
    help_text = _(("For example http://www.example.com/images/logo.jpg or "
                   "file:///var/www/html/images/logo.jpg")),
    default = default_icon_url))
    
ENFORCE_STATE = config_register(
    BooleanValue(SHOP_GROUP,
    'ENFORCE_STATE',
    description = _('State required?'),
    help_text = _("Require a state during registration/checkout for countries that have states?"),
    default = True))

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
