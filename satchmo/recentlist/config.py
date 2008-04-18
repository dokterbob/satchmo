from satchmo.configuration import *
from django.utils.translation import ugettext_lazy as _

config_register([

IntegerValue(SHOP_GROUP,
    'RECENT_MAX',
    description=_("Maximum recent items"),
    help_text=_("""The maximum number of items show in the recent box."""),
    default=4,
    ),

])
