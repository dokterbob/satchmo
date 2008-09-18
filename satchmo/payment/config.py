from django.conf import settings
from django.utils.translation import ugettext_lazy, ugettext
from satchmo.configuration import *
from satchmo.shop import get_satchmo_setting
from satchmo.utils import is_string_like, load_module
import logging

_ = ugettext_lazy

log = logging.getLogger('payment.config')

PAYMENT_GROUP = ConfigurationGroup('PAYMENT', _('Payment Settings'))

CRON_KEY = config_register(
    StringValue(PAYMENT_GROUP,
        'CRON_KEY',
        description=_("Cron Passkey"),
        help_text=_("Enter an authentication passkey to secure your recurring billing cron url."),
        default = "x1234replace_me")
)

ALLOW_URL_CRON = config_register(
    BooleanValue(PAYMENT_GROUP,
        'ALLOW_URL_REBILL',
        description=_("Allow URL Access to Cron for subscription rebills"),
        help_text=_("Do you want to allow remote url calls for subscription billing?"),
        default = False)
)

PAYMENT_LIVE = config_register(
    BooleanValue(PAYMENT_GROUP, 
        'LIVE', 
        description=_("Accept real payments"),
        help_text=_("False if you want to be in test mode.  This is the master switch, turn it off to force all payments into test mode."),
        default=False)
)

ORDER_EMAIL = config_register(
    BooleanValue(PAYMENT_GROUP,
        'ORDER_EMAIL_OWNER',
        description=_("Email owner?"),
        help_text=_("True if you want to email the owner on order"),
        default=False)
)
    
ORDER_EMAIL_EXTRA = config_register(
    StringValue(PAYMENT_GROUP,
        'ORDER_EMAIL_EXTRA',
        description=_("Extra order emails?"),
        requires=ORDER_EMAIL,
        help_text=_("Put all email addresses you want to email in addition to the owner when an order is placed."),
        default = "")
)

config_register_list(

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
        default=False),

    DecimalValue(PAYMENT_GROUP,
        'MINIMUM_ORDER',
        description=_("Minimum Order"),
        help_text=_("""The minimum cart total before checkout is allowed."""),
        default="0.00")
)

# --- Load default payment modules.  Ignore import errors, user may have deleted them. ---
_default_modules = ('authorizenet','dummy','google','paypal', 'trustcommerce', 'cybersource', 'autosuccess', 'cod', 'protx')

for module in _default_modules:
    try:
        load_module("satchmo.payment.modules.%s.config" % module)
    except ImportError:
        log.debug('Could not load default payment module configuration: %s', module)

# --- Load any extra payment modules. ---
extra_payment = get_satchmo_setting('CUSTOM_PAYMENT_MODULES')

for extra in extra_payment:
    try:
        load_module("%s.config" % extra)
    except ImportError:
        log.warn('Could not load payment module configuration: %s' % extra)

# --- helper functions ---

def credit_choices(settings=None, include_module_if_no_choices=False):
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
        if include_module_if_no_choices and not vals:
            key = config_value(module, 'KEY')
            label = config_value(module, 'LABEL')
            pair = (key, ugettext(label))
            choices.append(pair)
    return choices

def labelled_payment_choices():
    active_payment_modules = config_choice_values('PAYMENT', 'MODULES', translate=True)

    choices = []
    for module, module_name in active_payment_modules:
        label = config_value(module, 'LABEL', default = module_name)
        choices.append((module, label))
    
    return choices


def payment_live(settings):
    if is_string_like(settings):
        settings = config_get_group(settings)
    
    try:    
        if config_value('PAYMENT', 'LIVE'):
            return settings['LIVE'].value
            
    except SettingNotSet:
        pass
        
    return False
