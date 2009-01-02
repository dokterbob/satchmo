# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _
from livesettings import *

LANGUAGE_GROUP = ConfigurationGroup('LANGUAGE',_('Internationalization Settings'))

CURRENCY = config_register(
    StringValue(LANGUAGE_GROUP,
        'CURRENCY',
        description= _("Default currency symbol"),
        help_text= _("Use a '_' character to force a space."),
        default="$"))

ALLOW_TRANSLATIONS = config_register(
    BooleanValue(LANGUAGE_GROUP,
    'SHOW_TRANSLATIONS',
    description = _('Show translations?'),
    help_text = _("Show translations in admin."),
    default = True))

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
            ('he',"עִבְרִית"),
            ('it',"Italiano"),
            ('ko', "한국어"),
            ('sv', "Svenska"),
            ('pt-br',"Português"),
            ('bg',"Български"),
            ('tr',"Türkçe")]
    ))

