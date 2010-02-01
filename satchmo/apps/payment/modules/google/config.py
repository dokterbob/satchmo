from livesettings import *
from django.utils.translation import ugettext_lazy as _

# this is so that the translation utility will pick up the string
gettext = lambda s: s

PAYMENT_GROUP = ConfigurationGroup('PAYMENT_GOOGLE', 
    _('Google Checkout Module Settings'), 
    ordering = 101)

config_register_list(

    StringValue(PAYMENT_GROUP,
        'CART_XML_TEMPLATE',
        description=_("XML Template"),
        help_text=_("The XML template to use when submitting to Google. Probably you should not change this."),
        default = "shop/checkout/google/cart.xml"),
    
    StringValue(PAYMENT_GROUP,
        'CURRENCY_CODE',
        description=_('Currency Code'),
        help_text=_('Currency code for Google Checkout transactions.'),
        default = 'USD'),
    
    StringValue(PAYMENT_GROUP,
        'CHECKOUT_BUTTON_URL',
        description=_('Checkout Button URL'),
        default="http://checkout.google.com/buttons/checkout.gif"),
        
    StringValue(PAYMENT_GROUP,
        'CHECKOUT_BUTTON_SIZE',
        description=_('Checkout Button Size'),
        choices=(
            ('SMALL', _('Small')), 
            ('MEDIUM', _('Medium')), 
            ('LARGE', _('Large'))),
        default='MEDIUM'),
    
    StringValue(PAYMENT_GROUP,
        'POST_URL',
        description=_('Post URL'),
        help_text=_('The Google URL for real transaction posting.'),
        default="https://checkout.google.com/api/checkout/v2/checkout/Merchant/%(MERCHANT_ID)s"),

    StringValue(PAYMENT_GROUP,
        'POST_TEST_URL',
        description=_('Post URL'),
        help_text=_('The Google URL for test transaction posting.'),
        default="https://sandbox.google.com/checkout/api/checkout/v2/checkout/Merchant/%(MERCHANT_ID)s"),

    StringValue(PAYMENT_GROUP,
        'MERCHANT_ID',
        description=_('Merchant ID'),
        default=""),

    StringValue(PAYMENT_GROUP,
        'MERCHANT_KEY',
        description=_('Merchant Key'),
        default=""),

    StringValue(PAYMENT_GROUP,
        'MERCHANT_TEST_ID',
        description=_('Merchant Test ID'),
        default=""),

    StringValue(PAYMENT_GROUP,
        'MERCHANT_TEST_KEY',
        description=_('Merchant Test Key'),
        default=""),
    
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
        default = 'payment.modules.google'),
        
    StringValue(PAYMENT_GROUP,
        'KEY',
        description=_("Module key"),
        hidden=True,
        default = 'GOOGLE'),

    StringValue(PAYMENT_GROUP,
        'LABEL',
        description=_('English name for this group on the checkout screens'),
        default = 'Google Checkout',
        help_text = _('This will be passed to the translation utility')),

    StringValue(PAYMENT_GROUP,
        'URL_BASE',
        description=_('The url base used for constructing urlpatterns which will use this module'),
        default = '^google/'),
        
    BooleanValue(PAYMENT_GROUP,
        'EXTRA_LOGGING',
        description=_("Verbose logs"),
        help_text=_("Add extensive logs during post."),
        default=False)

)

PAYMENT_GROUP['TEMPLATE_OVERRIDES'] = {
    'shop/checkout/confirm.html' : 'shop/checkout/google/confirm.html',
}
