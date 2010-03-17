from livesettings import *
from django.utils.translation import ugettext_lazy as _

gettext = lambda s:s
_strings = (gettext('CreditCard'), gettext('Credit Card'))

PAYMENT_GROUP = ConfigurationGroup('PAYMENT_TRUSTCOMMERCE', 
    _('TrustCommerce Payment Settings'), 
    ordering=102)

config_register_list(

    StringValue(PAYMENT_GROUP,
        'KEY',
        description=_("Module key"),
        hidden=True,
        default = 'TRUSTCOMMERCE'),

    ModuleValue(PAYMENT_GROUP,
        'MODULE',
        description=_('Implementation module'),
        hidden=True,
        default = 'payment.modules.trustcommerce'),
        
    BooleanValue(PAYMENT_GROUP, 
        'SSL', 
        description=_("Use SSL for the checkout pages?"), 
        default=False),
    
    BooleanValue(PAYMENT_GROUP, 
        'AVS', 
        description=_("Use Address Verification System (AVS)?"), 
        default=False),
    
    BooleanValue(PAYMENT_GROUP, 
        'LIVE', 
        description=_("Accept real payments"),
        help_text=_("False if you want to be in test mode"),
        default=False),
    
    StringValue(PAYMENT_GROUP,
        'AUTH_TYPE',
        description=_("Type of authorization to perform."),
        help_text = _("Refer to manual for details on the different types."),
        default = 'sale',
        choices = [('sale', _('Sale')),
                    ('preauth', _('Preauth'))]
        ),
        
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
        description=_('Your TrustCommerce login'),
        default=""),
    
    StringValue(PAYMENT_GROUP, 
        'PASSWORD', 
        description=_('Your TrustCommerce password'),
        default=""),
        
    BooleanValue(PAYMENT_GROUP,
        'EXTRA_LOGGING',
        description=_("Verbose logs"),
        help_text=_("Add extensive logs during post."),
        default=False)
)
