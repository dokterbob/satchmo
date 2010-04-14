# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _
from livesettings import ConfigurationGroup, StringValue, config_register

PRODUCT_GROUP = ConfigurationGroup('PRODUCT', _('Product Settings'))

config_register(
    StringValue(PRODUCT_GROUP,
        'PROTECTED_DIR',
        description=_("Protected dir"),
        help_text=_("""This is only used if you use Downloadable Products.
This value will be appended to MEDIA_ROOT/MEDIA_URL.  Do not worry about slashes.
We can handle it any which way."""),
        default="protected",
    ))
