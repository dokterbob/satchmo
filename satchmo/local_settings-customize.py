# This file is used to store your site specific settings
# for database access.
# It also store satchmo unique information
#
#
# Modify this file to reflect your settings, then rename it to 
# local_settings.py
#
# This file is helpful if you have an existing Django project.  
# These are specific things that Satchmo will need.
# you MUST make sure these settings are imported from your project settings file!

import os
import logging

# This is useful, since satchmo is not the "current directory" like load_data expects.
# SATCHMO_DIRNAME = ''

# Only set these if Satchmo is part of another Django project
#SITE_NAME = ''
#ROOT_URLCONF = ''
#MEDIA_ROOT = os.path.join(DIRNAME, 'static/')
#DJANGO_PROJECT = 'Your Main Project Name'
#DJANGO_SETTINGS_MODULE = 'main-project.settings'
#DATABASE_NAME = ''
#DATABASE_PASSWORD = ''
#DATABASE_USER = ''
#SECRET_KEY = ''

##### For Email ########
# If this isn't set in your settings file, you can set these here
#EMAIL_HOST = 'host here'
#EMAIL_PORT = 587
#EMAIL_HOST_USER = 'your user here'
#EMAIL_HOST_PASSWORD = 'your password'
#EMAIL_USE_TLS = True

#### Satchmo unique variables ####

#These are used when loading the test data
SITE_DOMAIN = "example.com"
SITE_NAME = "My Site"

from django.conf.urls.defaults import *

SATCHMO_SETTINGS = {
    # this will override any urls set in the store url modules
    #'SHOP_URLS' : patterns('satchmo.shop.views',
    #    (r'^checkout/pay/$', 'paypal.checkout_step2.pay_ship_info', {'SSL': False}, 'satchmo_checkout-step2'),
    #    (r'^checkout/confirm/$', 'paypal.checkout_step3.confirm_info', {'SSL': False}, 'satchmo_checkout-step3'),
    #   if you have satchmo.feeds, make sure to include its URL
    #    (r'^feed/', include('satchmo.feeds.urls')),
    #   likewise with newsletters
    #    (r'^newsletter/', include('satchmo.newsletter.urls'))
    #   enable brands here
    #    (r'^brand/', include('satchmo.product.brand.urls'))
    #}
    
    # This is the base url for the shop.  Only include a leading slash
    # examples: '/shop' or '/mystore'
    # If you want the shop at the root directory, set SHOP_BASE to ''
    'SHOP_BASE' : '/store',
    
    # Set this to true if you want to use the multi-shop features
    # of satchmo.  It requires the "threaded_multihost" application
    # to be on your pythonpath.
    'MULTISHOP' : False,
    
    # register custom external newsletter modules by listing their modules here
    # 'CUSTOM_NEWSLETTER_MODULES' : ['client.newsletter.autoresponder',]
    'CUSTOM_NEWSLETTER_MODULES' : [],

    # register custom external payment modules by listing their modules here
    # ex: 'CUSTOM_PAYMENT_MODULES' : ['client.payment.wondercharge',]
    'CUSTOM_PAYMENT_MODULES' : [],

    # register custom external shipping modules by listing their modules here
    # ex: 'CUSTOM_SHIPPING_MODULES' : ['client.shipping.fancyshipping',]
    'CUSTOM_SHIPPING_MODULES' : [],

    # register custom external product modules by listing their modules here
    # ex: 'CUSTOM_PRODUCT_MODULES' : ['client.product.myproducttype',]
    'CUSTOM_PRODUCT_MODULES' : [],
}

# These can override or add to the default URLs
from django.conf.urls.defaults import *
URLS = patterns('',
)

# a cache backend is required.  Do not use locmem, it will not work properly at all in production
# Preferably use memcached, but file or DB is OK.  File is faster, I don't know why you'd want to use
# db, personally.  See: http://www.djangoproject.com/documentation/cache/ for help setting up your
# cache backend
#CACHE_BACKEND = "memcached://127.0.0.1:11211/"
#CACHE_BACKEND = "file:///var/tmp/django_cache"
CACHE_TIMEOUT = 60*5

# modify the cache_prefix if you have multiple concurrent stores.
CACHE_PREFIX = "STORE"


# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

# Languages for your site.  The language name
# should be the utf-8 encoded local name for the language.
gettext_noop = lambda s:s

LANGUAGES = (
    ('en', gettext_noop('English')),
)

# Locale path settings.  Needs to be set for Translation compilation.
# It can be blank
# LOCALE_PATHS = ""

#Configure logging
LOGDIR = os.path.abspath(os.path.dirname(__file__))
LOGFILE = "satchmo.log"
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename=os.path.join(LOGDIR, LOGFILE),
                    filemode='w')

# define a Handler which writes INFO messages or higher to the sys.stderr
fileLog = logging.FileHandler(os.path.join(LOGDIR, LOGFILE), 'w')
fileLog.setLevel(logging.DEBUG)
# set a format which is simpler for console use
formatter = logging.Formatter('%(asctime)s %(name)-12s: %(levelname)-8s %(message)s')
# tell the handler to use this format
fileLog.setFormatter(formatter)
# add the handler to the root logger
logging.getLogger('').addHandler(fileLog)
logging.getLogger('caching').setLevel(logging.INFO)
logging.info("Satchmo Started")
