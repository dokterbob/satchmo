from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from satchmo.configuration import *
from satchmo.utils import load_module

NEWSLETTER_GROUP = ConfigurationGroup('NEWSLETTER', _('Newsletter Settings'))

NEWSLETTER_ACTIVE = config_register(StringValue(NEWSLETTER_GROUP,
    'MODULE',
    description=_("Active newsletter module"),
    help_text=_("Select a newsletter, save and reload to set any module-specific newsletter settings."),
    default="satchmo.newsletter.simple",
    choices=[('satchmo.newsletter.ignore', _('No newsletter')),
            ('satchmo.newsletter.simple', _('Simple list')),
             ('satchmo.newsletter.mailman', _('Mailman'))]
    ))
    
config_register(StringValue(NEWSLETTER_GROUP,
    'NEWSLETTER_NAME',
    description=_("Name of Newsletter"),
    help_text=_("""Give the exact name that matches the mailing list set up in Mailman."""),
    requires=NEWSLETTER_ACTIVE,
    requiresvalue='satchmo.newsletter.mailman',
    default=""
    ))

# --- Load any extra payment modules. ---
extra_payment = getattr(settings, 'CUSTOM_NEWSLETTER_MODULES', ())

for extra in extra_payment:
    try:
        load_module("%s.config" % extra)
    except ImportError:
        log.warn('Could not load payment module configuration: %s' % extra)
