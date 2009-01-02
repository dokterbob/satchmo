from django.utils.translation import ugettext_lazy as _
from livesettings import *
from satchmo_store.shop.config import SHOP_GROUP

config_register(
    StringValue(SHOP_GROUP,
        'WISHLIST_SLUG',
        description=_("Wishlist slug"),
        help_text=_("The url slug for wishlists.  Requires server restart if changed."),
        default="wishlist"))
