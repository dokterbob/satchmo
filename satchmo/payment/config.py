from django.conf import settings
from django.utils.translation import ugettext_lazy, ugettext
from satchmo.configuration import *
from satchmo.shop.utils import is_string_like, load_module
_ = ugettext_lazy

import logging
log = logging.getLogger('payment.config')

PAYMENT_GROUP = ConfigurationGroup('PAYMENT', _('Payment Settings'))

PAYMENT_LIVE = config_register(
    BooleanValue(PAYMENT_GROUP, 
        'LIVE', 
        description=_("Accept real payments"),
        help_text=_("False if you want to be in test mode.  This is the master switch, turn it off to force all payments into test mode."),
        default=False)
)

config_register([

BooleanValue(PAYMENT_GROUP,
    'COUNTRY_MATCH',
    description=_("Country match required?"),
    help_text=_("If True, then customers may not have different countries for shipping and billing."),
    default=True),

MultipleStringValue(PAYMENT_GROUP,
    'MODULES',
    description=_("Enable payment modules"),
    help_text=_("""Select the payment modules you want to use with your shop.  
If you are adding a new one, you should save and come back to this page, 
as it may have enabled a new configuration section."""),
    default=["PAYMENT_DUMMY"]),
    
BooleanValue(PAYMENT_GROUP,
    'SSL',
    description=_("Enable SSL"),
    help_text=_("""This enables for generic pages like contact information capturing.  
It does not set SSL for individual modules. 
You must enable SSL for each payment module individually."""),
    default=False)

])

# --- Load default payment modules.  Ignore import errors, user may have deleted them. ---
_default_modules = ('authorizenet','dummy','google','paypal', 'trustcommerce', 'cybersource', 'autosuccess', 'cod')

for module in _default_modules:
    try:
        load_module("satchmo.payment.modules.%s.config" % module)
    except ImportError:
        log.debug('Could not load default payment module configuration: %s', module)

# --- Load any extra payment modules. ---
extra_payment = getattr(settings, 'CUSTOM_PAYMENT_MODULES', ())

for extra in extra_payment:
    try:
        load_module("%s.config" % extra)
    except ImportError:
        log.warn('Could not load payment module configuration: %s' % extra)

# --- helper functions ---

def credit_choices(settings=None):
    choices = []
    keys = []
    for module in config_value('PAYMENT', 'MODULES'):
        vals = config_choice_values(module, 'CREDITCHOICES')
        for val in vals:
            key, label = val
            if not key in keys:
                keys.append(key)
                pair = (key, ugettext(label))
                choices.append(pair)
    return choices
    
def payment_choices():
    choices = []
    for module in config_value('PAYMENT', 'MODULES'):
        try:
            key = config_value(module, 'KEY')
            label = config_value(module, 'LABEL')
            choices.append((key, ugettext(label)))
        except SettingNotSet, se:
            log.warn("Could not load payment choice for: %s", module)
            log.error(se)
    return choices

def payment_live(settings):
    if is_string_like(settings):
        settings = config_get_group(settings)
        
    return config_value('PAYMENT', 'LIVE') and settings['LIVE']
