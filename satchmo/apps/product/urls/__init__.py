from category import urlpatterns as catpatterns
from django.conf.urls.defaults import *
from livesettings import config_value
from product import urlpatterns as prodpatterns
import product
from satchmo_utils.signals import collect_urls

catbase = r'^' + config_value('PRODUCT','CATEGORY_SLUG') + '/'
prodbase = r'^' + config_value('PRODUCT','PRODUCT_SLUG') + '/'

urlpatterns = patterns('',
    (prodbase, include('product.urls.product')),
    (catbase, include('product.urls.category')),
)

collect_urls.send(product, section="__init__", patterns = urlpatterns)
