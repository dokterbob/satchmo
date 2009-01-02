from livesettings import ConfigurationGroup, config_register_list, IntegerValue, BooleanValue
from django.utils.translation import ugettext_lazy as _

THUMB_GROUP = ConfigurationGroup('THUMBNAIL', _('Thumbnail Settings'))

config_register_list(
    IntegerValue(THUMB_GROUP, 
        'IMAGE_QUALITY', 
        description= _("Thumbnail quality"), 
        help_text = _("Use a 1-100 value here, which will change the quality of JPG thumbnails created for products and categories."),
        default=75,
        ordering=0),
        
    BooleanValue(THUMB_GROUP,
        'RENAME_IMAGES',
        description=_("Rename product images?"),
        help_text=_("Automatically rename product images on upload?"),
        default=True)
)
