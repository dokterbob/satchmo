from livesettings import *
from django.utils.translation import ugettext_lazy as _

# this is so that the translation utility will pick up the string
gettext = lambda s: s

PAYMENT_GROUP = ConfigurationGroup('PAYMENT_DUMMY', 
    _('Payment Test Module Settings'), 
    ordering = 100)

config_register_list(
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
        default = 'payment.modules.dummy'),
        
    StringValue(PAYMENT_GROUP,
        'KEY',
        description=_("Module key"),
        hidden=True,
        default = 'DUMMY'),

    StringValue(PAYMENT_GROUP,
        'LABEL',
        description=_('English name for this group on the checkout screens'),
        default = 'Payment test module',
        help_text = _('This will be passed to the translation utility')),

    StringValue(PAYMENT_GROUP,
        'URL_BASE',
        description=_('The url base used for constructing urlpatterns which will use this module'),
        default = '^dummy/'),

    MultipleStringValue(PAYMENT_GROUP,
        'CREDITCHOICES',
        description=_('Available credit cards'),
        choices = (
            (('Visa','Visa')),
            (('Mastercard','Mastercard')),
            (('Discover','Discover')),
            (('American Express', 'American Express'))),
        default = ('Visa', 'Mastercard', 'Discover', 'American Express')),
        
    BooleanValue(PAYMENT_GROUP,
        'CAPTURE',
        description=_('Capture Payment immediately?'),
        default=True,
        help_text=_('IMPORTANT: If false, a capture attempt will be made when the order is marked as shipped."')),
        
    BooleanValue(PAYMENT_GROUP,
        'AUTH_EARLY',
        description=_("Early AUTH"),
        help_text=_("Authenticate on the card entry page, causes an immediate $.01 AUTH and release, allowing errors with the card to show on the card entry page."),
        default=False),

    BooleanValue(PAYMENT_GROUP,
        'EXTRA_LOGGING',
        description=_("Verbose logs"),
        help_text=_("Add extensive logs during post."),
        default=False)
)
