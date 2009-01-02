from django.utils.translation import ugettext_lazy as _
from livesettings import *
from product.config import PRODUCT_GROUP

BRAND_SLUG = config_register(
    StringValue(PRODUCT_GROUP,
        'BRAND_SLUG',
        description=_("Brand Slug"),
        help_text=_("The url slug for brands.  Requires server restart if changed."),
        default="brand"))
