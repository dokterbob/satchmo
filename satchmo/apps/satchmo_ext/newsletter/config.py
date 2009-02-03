from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from livesettings import *
from satchmo_utils import load_module
from satchmo_store.shop import get_satchmo_setting

NEWSLETTER_GROUP = ConfigurationGroup('NEWSLETTER', _('Newsletter Settings'))

NEWSLETTER_ACTIVE = config_register(StringValue(NEWSLETTER_GROUP,
    'MODULE',
    description=_("Active newsletter module"),
    help_text=_("Select a newsletter, save and reload to set any module-specific newsletter settings."),
    default="satchmo_ext.newsletter.simple",
    choices=[('satchmo_ext.newsletter.ignore', _('No newsletter')),
            ('satchmo_ext.newsletter.simple', _('Simple list')),
             ('satchmo_ext.newsletter.mailman', _('Mailman'))]
    ))
    
config_register(StringValue(NEWSLETTER_GROUP,
    'NEWSLETTER_NAME',
    description=_("Name of Newsletter"),
    help_text=_("""Give the exact name that matches the mailing list set up in Mailman."""),
    requires=NEWSLETTER_ACTIVE,
    requiresvalue='satchmo_ext.newsletter.mailman',
    default=""
    ))

config_register(
    StringValue(NEWSLETTER_GROUP,
        'NEWSLETTER_SLUG',
        description=_('Newsletter Slug'),
        help_text=_("The url slug for the newsletter.  Requires server restart if changed."),
        default="newsletter"))

# --- Load any extra newsletter modules. ---
extra_payment = get_satchmo_setting('CUSTOM_NEWSLETTER_MODULES')

for extra in extra_payment:
    try:
        load_module("%s.config" % extra)
    except ImportError:
        log.warn('Could not load payment module configuration: %s' % extra)
