from django.utils.translation import ugettext_lazy, ugettext
from livesettings import *
from payment import signals, active_gateways
from satchmo_store.shop import get_satchmo_setting
from satchmo_utils import is_string_like, load_module
import logging
import signals

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
        'AUTH_EARLY',
        description=_("Early AUTH"),
        help_text=_("Where possible, Authenticate on the card entry page.  This causes an immediate $.01 AUTH and release, allowing errors with the card to show on the card entry page instead of on the confirmation page.  Note that this is only supported for payment modules that can do Authorizations.  It will be silently ignored for any other processors."),
        default=False),

    BooleanValue(PAYMENT_GROUP,
        'COUNTRY_MATCH',
        description=_("Country match required?"),
        help_text=_("If True, then customers may not have different countries for shipping and billing."),
        default=True),

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
        default="0.00"),

    BooleanValue(PAYMENT_GROUP,
        'STORE_CREDIT_NUMBERS',
        description=_("Save Credit Card Numbers"),
        help_text=_("If False, then the credit card will never be written to disk.  For PCI compliance, this is required unless you have your database server on a separate server not connected to the internet."),
        default=False),

    PositiveIntegerValue(PAYMENT_GROUP,
        'CC_NUM_YEARS',
        description=_("Number of years to display for CC expiration"),
        help_text=_("Number of years that will be added to today's year for the CC expiration drop down"),
        default=10),
    
    BooleanValue(PAYMENT_GROUP,
        'USE_DISCOUNTS',
        description=_("Use discounts"),
        help_text=_("""If disabled, customers will not be asked for any discount codes."""),
        default=True)
)

# --- helper functions ---

def credit_choices(settings=None, include_module_if_no_choices=False):
    choices = []
    keys = []
    for module, group in active_gateways():
        vals = config_choice_values(group, 'CREDITCHOICES')
        for key, label in vals:
            if not key in keys:
                keys.append(key)
                pair = (key, ugettext(label))
                choices.append(pair)
        if include_module_if_no_choices and not vals:
            key = config_value(group, 'KEY')
            label = config_value(group, 'LABEL')
            pair = (key, ugettext(label))
            choices.append(pair)
    return choices

def labelled_gateway_choices():
    choices = []
    for module, group in active_gateways():
        defaultlabel = module.split('.')[-1]
        label = _(config_value(group, 'LABEL', default = defaultlabel))
        choices.append((group, label))
    
    signals.payment_choices.send(None, choices=choices)
    return choices

def gateway_live(settings):
    if is_string_like(settings):
        settings = config_get_group(settings)
    
    try:    
        if config_value('PAYMENT', 'LIVE'):
            return settings['LIVE'].value
            
    except SettingNotSet:
        pass
        
    return False
