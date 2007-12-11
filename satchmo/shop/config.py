from satchmo.configuration import config_register, BooleanValue, StringValue, MultipleStringValue, SHOP_GROUP, ConfigurationGroup
from django.utils.translation import ugettext_lazy as _

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
        
#### Google Group ####

GOOGLE_GROUP = ConfigurationGroup('GOOGLE', 'Google Settings')

GOOGLE_ANALYTICS = config_register(
    BooleanValue(GOOGLE_GROUP, 
        'ANALYTICS', 
        description= _("Enable Analytics"), 
        default=False,
        ordering=0))
        
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

LANGUAGE_GROUP = ConfigurationGroup('LANGUAGE','Language Settings')

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
    choices=[('en', _("English")),
            ('fr', _("French")),
            ('de',_("German")),
            ('es', _("Spanish")),
            ('sv', _("Swedish"))]
    ))
    