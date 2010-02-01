# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _
from livesettings import *
from satchmo_utils import load_module
from satchmo_store.shop import get_satchmo_setting

PRODUCT_GROUP = ConfigurationGroup('PRODUCT', _('Product Settings'))

PRODUCT_TYPES = config_register(MultipleStringValue(PRODUCT_GROUP,
    'PRODUCT_TYPES',
    description=_("Product Model Options"),
    default=['product::ConfigurableProduct', 'product::ProductVariation'],
    choices=[('product::ConfigurableProduct', _('Configurable Product')),
             ('product::ProductVariation', _('Product Variation')),
             ('product::CustomProduct', _('Custom Order Product')),
             ('product::SubscriptionProduct', _('Subscription Product')),
             ('product::DownloadableProduct', _('Downloadable Product'))]
    ))

config_register(
    StringValue(PRODUCT_GROUP,
        'IMAGE_DIR',
        description=_("Upload Image Dir"),
        help_text=_("""Directory name for storing uploaded images.
    This value will be appended to MEDIA_ROOT.  Do not worry about slashes.
    We can handle it any which way."""),
        default="images")
)

config_register_list(
    StringValue(PRODUCT_GROUP,
        'PROTECTED_DIR',
        description=_("Protected dir"),
        help_text=_("""This is only used if you use Downloadable Products.
This value will be appended to MEDIA_ROOT.  Do not worry about slashes.
We can handle it any which way."""),
        default="protected",
        requires=PRODUCT_TYPES,
        requiresvalue='product::DownloadableProduct'
    ),

    PositiveIntegerValue(PRODUCT_GROUP,
        'NUM_DISPLAY',
        description=_("Total featured"),
        help_text=_("Total number of featured items to display"),
        default=20
    ),

    PositiveIntegerValue(PRODUCT_GROUP,
        'NUM_PAGINATED',
        description=_("Number featured"),
        help_text=_("Number of featured items to display on each page"),
        default=10
    ),

    MultipleStringValue(PRODUCT_GROUP,
        'MEASUREMENT_SYSTEM',
        description=_("Measurement System"),
        help_text=_("Default measurement system to use for products."),
        choices=[('metric',_('Metric')),
                    ('imperial',_('Imperial'))],
        default="imperial"
    ),
    
    BooleanValue(PRODUCT_GROUP,
        'NO_STOCK_CHECKOUT',
        description=_("Allow checkout with 0 inventory?"),
        help_text=_("If yes, then customers can buy even if your inventory is 0 for a product."),
        default=True
    ),
    
    BooleanValue(PRODUCT_GROUP,
        'RANDOM_FEATURED',
        description= _("Random Display"),
        help_text= _("Enable random display of featured products on home page"),
        default=False
    ),

    BooleanValue(PRODUCT_GROUP,
        'TRACK_INVENTORY',
        description=_("Track inventory levels?"),
        help_text=_("If no, then inventory will not be tracked for products sold."),
        default=True
    ),
)
