from satchmo.configuration import config_register, StringValue, IntegerValue, SHOP_GROUP

from django.utils.translation import ugettext_lazy as _

# I am doing it this way instead of a boolean for email verification because I
# intend to add a "manual approval" style of account verification. -Bruce
ACCOUNT_VERIFICATION = config_register(StringValue(SHOP_GROUP,
    'ACCOUNT_VERIFICATION',
    description=_("Account Verification"),
    help_text=_("Select the style of account verification.  'Immediate' means no verification needed."),
    default="IMMEDIATE",
    choices=[('IMMEDIATE', _('Immediate')),
             ('EMAIL', _('Email'))]
    ))
             
config_register([

IntegerValue(SHOP_GROUP,
    'ACCOUNT_ACTIVATION_DAYS',
    description=_('Days to verify account'),
    default=7,
    requires=ACCOUNT_VERIFICATION,
    requiresvalue='EMAIL')
    
])
