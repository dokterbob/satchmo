# Django settings for satchmo project.
# If you have an existing project, then ensure that you modify local_settings-customize.py
# and import it from your main settings file. (from local_settings import *)
import os

DIRNAME = os.path.dirname(__file__)

DJANGO_PROJECT = 'large'
DJANGO_SETTINGS_MODULE = 'large.settings'

ADMINS = (
     ('', ''),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'mysql'           # 'postgresql', 'mysql', 'sqlite3' or 'ado_mssql'.
# The following variables should be configured in your local_settings.py file
#DATABASE_NAME = ''             # Or path to database file if using sqlite3.
#DATABASE_USER = ''             # Not used with sqlite3.
#DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. All choices can be found here:
# http://www.postgresql.org/docs/current/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE
TIME_ZONE = 'US/Pacific'

# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
# http://blogs.law.harvard.edu/tech/stories/storyReader$15
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
#Image files will be stored off of this path
MEDIA_ROOT = os.path.join(DIRNAME, 'static/')
#MEDIA_ROOT = "/static"
# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
#MEDIA_URL = 'site_media'
MEDIA_URL="/static/"
# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = ''

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.middleware.doc.XViewMiddleware",
    "threaded_multihost.middleware.ThreadLocalMiddleware",
    "satchmo_store.shop.SSLMiddleware.SSLRedirect",
    "satchmo_ext.recentlist.middleware.RecentProductMiddleware",
    #'djangologging.middleware.LoggingMiddleware',
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
    "django.contrib.flatpages.middleware.FlatpageFallbackMiddleware",
)

#this is used to add additional config variables to each request
# NOTE: overridden in local_settings.py
TEMPLATE_CONTEXT_PROCESSORS = ('satchmo_store.shop.context_processors.settings',
                               'django.core.context_processors.auth',
                               #'satchmo_ext.recentlist.context_processors.recent_products',
                               )

#ROOT_URLCONF = 'satchmo.urls'
ROOT_URLCONF = 'large.urls'

INSTALLED_APPS = (
    'django.contrib.sites',
    'satchmo_store.shop',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.comments',
    'django.contrib.sessions',
    'django.contrib.sitemaps',
    'registration',
    'sorl.thumbnail',
    'keyedcache',
    'livesettings',
    'l10n',
    'satchmo_utils.thumbnail',
    'satchmo_store.contact',
    'tax',
    'tax.modules.no',
    'tax.modules.area',
    'tax.modules.percent',
    'shipping',
    'satchmo_store.contact.supplier',
    'shipping.modules.tiered',
    'satchmo_ext.newsletter',
    'satchmo_ext.recentlist',
    'testimonials',
    'product',
    'satchmo_ext.product_feeds',
    'satchmo_ext.brand',
    'payment',
    'payment.modules.purchaseorder',
    'payment.modules.giftcertificate',
    'satchmo_ext.wishlist',
    'satchmo_ext.upsell',
    'satchmo_ext.productratings',
    'satchmo_utils',
    'shipping.modules.tieredquantity',
    #'django_extensions',
    'satchmo_ext.tieredpricing',
    'typogrify',
    #'debug_toolbar',
    'app_plugins',
    'large.localsite',
    'django.contrib.flatpages',
)

AUTHENTICATION_BACKENDS = (
    'satchmo_store.accounts.email-auth.EmailBackend',
    'django.contrib.auth.backends.ModelBackend',
)

#DEBUG_TOOLBAR_CONFIG = {
#    'INTERCEPT_REDIRECTS' : False,
#}

#### Satchmo unique variables ####
#from django.conf.urls.defaults import patterns, include
SATCHMO_SETTINGS = {
    'SHOP_BASE' : '/shop',
    'MULTISHOP' : False,
    #'SHOP_URLS' : patterns('satchmo_store.shop.views',)
}

# Load the local settings
from local_settings import *
