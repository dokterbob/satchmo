from livesettings import config_register, StringValue, IntegerValue, BooleanValue, MultipleStringValue
from satchmo_store.shop.config import SHOP_GROUP

from django.utils.translation import ugettext_lazy as _

config_register(
    BooleanValue(SHOP_GROUP,
    'AUTHENTICATION_REQUIRED',
    description=_("Only authenticated users can check out"),
    help_text=_("Users will be required to authenticate (and create an account if neccessary) before checkout."),
    default=False,
    )
)

config_register(
    MultipleStringValue(SHOP_GROUP,
    'REQUIRED_BILLING_DATA',
    description=_("Required billing data"),
    help_text=_(
        "Users may be required to provide some set of billing address. Other fields are optional. "
        "You may shorten the checkout process here, but be careful, as this may leave you orders "
        "with almost no customer data! Some payment modules may override this setting."
        ),
    default=('email', 'first_name', 'last_name', 'phone', 'street1', 'city', 'postal_code', 'country'),
    choices=(
        ('email', _("Email")),
        ('title', _("Title")),
        ('first_name', _("First name")),
        ('last_name', _("Last name")),
        ('phone', _("Phone")),
        ('addressee', _("Addressee")),
        ('organization', _("Organization")),
        ('street1', _("Street")),
        ('street2', _("Street (second line)")),
        ('city', _("City")),
        ('state', _("State/Province")),
        ('postal_code', _("Postal code/ZIP")),
        ('country', _("Country"))
        )
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
