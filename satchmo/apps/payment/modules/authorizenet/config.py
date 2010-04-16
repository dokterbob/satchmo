from livesettings import *
from django.utils.translation import ugettext_lazy as _

# this is so that the translation utility will pick up the string
gettext = lambda s: s
_strings = (gettext('CreditCard'), gettext('Credit Card'))

PAYMENT_GROUP = ConfigurationGroup('PAYMENT_AUTHORIZENET',
    _('Authorize.net Payment Settings'),
    ordering=101)

config_register_list(

    StringValue(PAYMENT_GROUP,
        'CONNECTION',
        description=_("Submit to URL"),
        help_text=_("""This is the address to submit live transactions."""),
        default='https://secure.authorize.net/gateway/transact.dll'),

    StringValue(PAYMENT_GROUP,
        'CONNECTION_TEST',
        description=_("Submit to Test URL"),
        help_text=("""If you have a test account with authorize.net and you log in through
https://test.authorize.net/gateway/transact.dll, then you should use the default 
test URL.  If you do not have a test account you will get an Error 13 message 
unless you change the URL to https://secure.authorize.net/gateway/transact.dll.  
You will also need to login in to authorize.net and make sure your account has 
test mode turned on.
"""),
        default='https://test.authorize.net/gateway/transact.dll'),

    BooleanValue(PAYMENT_GROUP,
        'LIVE',
        description=_("Accept real payments"),
        help_text=_("False if you want to submit to the test urls.  NOTE: If you are testing, then you can use the cc# 4222222222222 to force a bad credit card response.  If you use that number and a ccv of 222, that will force a bad ccv response from authorize.net"),
        default=False),

    BooleanValue(PAYMENT_GROUP,
        'SIMULATE',
        description=_("Force a test post?"),
        help_text=_("True if you want to submit to the live url using a test flag, which won't be accepted."),
        default=False),

    ModuleValue(PAYMENT_GROUP,
        'MODULE',
        description=_('Implementation module'),
        hidden=True,
        default = 'payment.modules.authorizenet'),

    StringValue(PAYMENT_GROUP,
        'KEY',
        description=_("Module key"),
        hidden=True,
        default = 'AUTHORIZENET'),

    StringValue(PAYMENT_GROUP,
        'LABEL',
        description=_('English name for this group on the checkout screens'),
        default = 'Credit Cards',
        help_text = _('This will be passed to the translation utility')),

    StringValue(PAYMENT_GROUP,
        'URL_BASE',
        description=_('The url base used for constructing urlpatterns which will use this module'),
        default = r'^credit/'),

    MultipleStringValue(PAYMENT_GROUP,
        'CREDITCHOICES',
        description=_('Available credit cards'),
        choices = (
            (('American Express', 'American Express')),
            (('Visa','Visa')),
            (('Mastercard','Mastercard')),
            (('Discover','Discover'))),
        default = ('Visa', 'Mastercard', 'Discover')),

    StringValue(PAYMENT_GROUP,
        'LOGIN',
        description=_('Your authorize.net transaction login'),
        default=""),

    StringValue(PAYMENT_GROUP,
        'TRANKEY',
        description=_('Your authorize.net transaction key'),
        default=""),

    BooleanValue(PAYMENT_GROUP,
        'CAPTURE',
        description=_('Capture Payment immediately?'),
        default=True,
        help_text=_('IMPORTANT: If false, a capture attempt will be made when the order is marked as shipped."')),

    BooleanValue(PAYMENT_GROUP,
        'EXTRA_LOGGING',
        description=_("Verbose logs"),
        help_text=_("Add extensive logs during post."),
        default=False)
)

ARB_ENABLED = config_register(
    BooleanValue(PAYMENT_GROUP,
        'ARB',
        description=_('Enable ARB?'),
        default=False,
        help_text=_('Enable ARB processing for setting up subscriptions.  You must have this enabled in your Authorize account for it to work.')))

config_register(
    StringValue(PAYMENT_GROUP,
        'ARB_CONNECTION',
        description=_("Submit to URL (ARB)"),
        help_text=_("""This is the address to submit live transactions for ARB."""),
        requires=ARB_ENABLED,
        default='https://api.authorize.net/xml/v1/request.api'))

config_register(
    StringValue(PAYMENT_GROUP,
        'ARB_CONNECTION_TEST',
        description=_("Submit to Test URL (ARB)"),
        help_text=_("""This is the address to submit test transactions for ARB."""),
        requires=ARB_ENABLED,
        default='https://apitest.authorize.net/xml/v1/request.api'))

