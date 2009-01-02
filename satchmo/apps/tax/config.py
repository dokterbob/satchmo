from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from livesettings import *
from satchmo_utils import is_string_like, load_module

TAX_GROUP = ConfigurationGroup('TAX', _('Tax Settings'))
TAX_MODULE = config_register(StringValue(TAX_GROUP,
    'MODULE',
    description=_("Active tax module"),
    help_text=_("Select a module, save and reload to set any module-specific settings."),
    default="tax.modules.no",
    choices=[('tax.modules.no', _('No Tax')),
    ]
))

DEFAULT_VIEW_TAX = config_register(BooleanValue(TAX_GROUP,
    'DEFAULT_VIEW_TAX',
    description=_("Show with tax included"),
    help_text=_("If yes, then all products and the cart will display with tax included."),
    default=False
))
