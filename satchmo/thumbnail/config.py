from satchmo.configuration import config_register, IntegerValue, SHOP_GROUP
from django.utils.translation import ugettext_lazy as _

#### SHOP Group ####

config_register(
    IntegerValue(SHOP_GROUP, 
        'IMAGE_QUALITY', 
        description= _("Thumbnail quality"), 
        help_text = _("Use a 1-100 value here, which will change the quality of JPG thumbnails created for products and categories."),
        default=75,
        ordering=0)
)
