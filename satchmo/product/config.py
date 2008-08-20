from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from satchmo.configuration import *
from satchmo.shop import get_satchmo_setting
from satchmo.utils import load_module


PRODUCT_GROUP = ConfigurationGroup('PRODUCT', _('Product Settings'))

PRODUCT_TYPES = config_register(MultipleStringValue(PRODUCT_GROUP,
    'PRODUCT_TYPES',
    description=_("Product Model Options"),
    default=['product::ConfigurableProduct', 'product::ProductVariation'],
    choices=[('product::ConfigurableProduct', _('Configurable Product')),
             ('product::ProductVariation', _('Product Variation')),
             ('product::CustomProduct', _('Custom Order')),
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

config_register(
    StringValue(PRODUCT_GROUP,
        'PROTECTED_DIR',
        description=_("Protected dir"),
        help_text=_("""This is only used if you use Downloadable Products.
This value will be appended to MEDIA_ROOT.  Do not worry about slashes.
We can handle it any which way."""),
        default="protected",
        requires=PRODUCT_TYPES,
        requiresvalue='product::DownloadableProduct')
)

# --- Load any extra product modules. ---
extra_product = get_satchmo_setting('CUSTOM_PRODUCT_MODULES')

for extra in extra_product:
    try:
        load_module("%s.config" % extra)
    except ImportError:
        log.warn('Could not load product module configuration: %s' % extra)
