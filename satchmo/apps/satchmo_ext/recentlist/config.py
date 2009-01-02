from livesettings import *
from django.utils.translation import ugettext_lazy as _
from product.config import PRODUCT_GROUP
config_register(
IntegerValue(PRODUCT_GROUP,
    'RECENT_MAX',
    description=_("Maximum recent items"),
    help_text=_("""The maximum number of items show in the recent box."""),
    default=4,
    ),
)
