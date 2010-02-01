from livesettings import *
from django.utils.translation import ugettext_lazy as _

PAYMENT_GROUP = ConfigurationGroup('PAYMENT_PAYPAL', 
    _('Paypal Payment Module Settings'), 
    ordering = 101)

config_register_list(

StringValue(PAYMENT_GROUP,
    'CURRENCY_CODE',
    description=_('Currency Code'),
    help_text=_('Currency code for Paypal transactions.'),
    default = 'USD'),
    
StringValue(PAYMENT_GROUP,
    'POST_URL',
    description=_('Post URL'),
    help_text=_('The Paypal URL for real transaction posting.'),
    default="https://www.paypal.com/cgi-bin/webscr"),

StringValue(PAYMENT_GROUP,
    'POST_TEST_URL',
    description=_('Post URL'),
    help_text=_('The Paypal URL for test transaction posting.'),
    default="https://www.sandbox.paypal.com/cgi-bin/webscr"),

StringValue(PAYMENT_GROUP,
    'BUSINESS',
    description=_('Paypal account email'),
    help_text=_('The email address for your paypal account'),
    default=""),

StringValue(PAYMENT_GROUP,
    'BUSINESS_TEST',
    description=_('Paypal test account email'),
    help_text=_('The email address for testing your paypal account'),
    default=""),

StringValue(PAYMENT_GROUP,
    'RETURN_ADDRESS',
    description=_('Return URL'),
    help_text=_('Where Paypal will return the customer after the purchase is complete.  This can be a named url and defaults to the standard checkout success.'),
    default="satchmo_checkout-success"),
    
BooleanValue(PAYMENT_GROUP, 
    'SSL', 
    description=_("Use SSL for the module checkout pages?"), 
    default=False),
    
BooleanValue(PAYMENT_GROUP, 
    'LIVE', 
    description=_("Accept real payments"),
    help_text=_("False if you want to be in test mode"),
    default=False),
    
ModuleValue(PAYMENT_GROUP,
    'MODULE',
    description=_('Implementation module'),
    hidden=True,
    default = 'payment.modules.paypal'),
    
StringValue(PAYMENT_GROUP,
    'KEY',
    description=_("Module key"),
    hidden=True,
    default = 'PAYPAL'),

StringValue(PAYMENT_GROUP,
    'LABEL',
    description=_('English name for this group on the checkout screens'),
    default = 'PayPal',
    help_text = _('This will be passed to the translation utility')),

StringValue(PAYMENT_GROUP,
    'URL_BASE',
    description=_('The url base used for constructing urlpatterns which will use this module'),
    default = '^paypal/'),
    
BooleanValue(PAYMENT_GROUP,
    'EXTRA_LOGGING',
    description=_("Verbose logs"),
    help_text=_("Add extensive logs during post."),
    default=False)
)

PAYMENT_GROUP['TEMPLATE_OVERRIDES'] = {
    'shop/checkout/confirm.html' : 'shop/checkout/paypal/confirm.html',
}
