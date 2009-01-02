from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from livesettings import *
from product.config import PRODUCT_GROUP

ENABLE_AKISMET = config_register(
    BooleanValue(PRODUCT_GROUP,
        'AKISMET_ENABLE',
        description= _("Enable Akismet ratings"),
        default=False))
        
AKISMET = config_register(
    StringValue(PRODUCT_GROUP,
        'AKISMET_KEY',
        description= _("Akismet API Key"),
        requires=ENABLE_AKISMET,
        default=""))
