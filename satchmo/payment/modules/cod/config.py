from satchmo.configuration import *
from django.utils.translation import ugettext_lazy as _

# this is so that the translation utility will pick up the string
gettext = lambda s: s

PAYMENT_MODULES = config_get('PAYMENT', 'MODULES')
PAYMENT_MODULES.add_choice(('PAYMENT_COD', _('COD')))

PAYMENT_GROUP = ConfigurationGroup('PAYMENT_COD', 
    _('COD Payment Module Settings'), 
    requires=PAYMENT_MODULES,
    ordering = 100)

config_register([
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
        default = 'satchmo.payment.modules.cod'),
        
    StringValue(PAYMENT_GROUP,
        'KEY',
        description=_("Module key"),
        hidden=True,
        default = 'COD'),

    StringValue(PAYMENT_GROUP,
        'LABEL',
        description=_('English name for this group on the checkout screens'),
        default = 'COD Payment',
        help_text = _('This will be passed to the translation utility')),

    StringValue(PAYMENT_GROUP,
        'URL_BASE',
        description=_('The url base used for constructing urlpatterns which will use this module'),
        default = '^cod/'),

])
