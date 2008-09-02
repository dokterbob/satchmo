from satchmo.configuration import config_register, StringValue, IntegerValue, BooleanValue, SHOP_GROUP

from django.utils.translation import ugettext_lazy as _

config_register(
    BooleanValue(SHOP_GROUP,
    'AUTHENTICATION_REQUIRED',
    description=_("Only authenticated users can check out"),
    help_text=_("Users will be required to authenticate (and create an account if neccessary) before checkout."),
    default=False,
    )
)
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
             
config_register(
    IntegerValue(SHOP_GROUP,
    'ACCOUNT_ACTIVATION_DAYS',
    description=_('Days to verify account'),
    default=7,
    requires=ACCOUNT_VERIFICATION,
    requiresvalue='EMAIL')
)
