# Django settings for satchmo project.
# If you have an existing project, then ensure that you modify local_settings-customize.py
# and import it from your main settings file. (from local_settings import *)
import os

DIRNAME = os.path.abspath(os.path.dirname(__file__).decode('utf-8'))

DJANGO_PROJECT = 'satchmo'
DJANGO_SETTINGS_MODULE = 'satchmo_store.settings'

LOCAL_DEV = True
DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
     ('', ''),
)

MANAGERS = ADMINS

DATABASE_ENGINE = ''           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
# The following variables should be configured in your local_settings.py file
#DATABASE_NAME = ''             # Or path to database file if using sqlite3.
#DATABASE_USER = ''             # Not used with sqlite3.
#DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. All choices can be found here:
# http://www.postgresql.org/docs/8.1/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
# For windows, you must use 'us' instead
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
# Image files will be stored off of this path.
MEDIA_ROOT = os.path.join(DIRNAME, 'static/')
# URL that handles the media served from MEDIA_ROOT. Use a trailing slash.
# Example: "http://media.lawrence.com/"
MEDIA_URL = '/static/'
# URL that handles the media served from SSL.  You only need to set this
# if you are using a non-relative url.
# Example: "https://media.lawrence.com"
# MEDIA_SECURE_URL = "https://foo.com/"
# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
# SECRET_KEY = ''

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
#    "satchmo_ext.recentlist.middleware.RecentProductMiddleware",
)

#this is used to add additional config variables to each request
# NOTE: If you enable the recent_products context_processor, you MUST have the
# 'satchmo_ext.recentlist' app installed.
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.media',
#    'satchmo_ext.recentlist.context_processors.recent_products',
    'satchmo_store.shop.context_processors.settings',
    'django.core.context_processors.i18n'
)

ROOT_URLCONF = 'satchmo_store.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates".
    # Always use forward slashes, even on Windows.
    os.path.join(DIRNAME, "templates"),
)

INSTALLED_APPS = (
    'satchmo_store.shop',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.comments',
    'django.contrib.sessions',
    'django.contrib.sitemaps',
    'django.contrib.sites',
    #'registration',
    'sorl.thumbnail',
    'satchmo',
    'keyedcache',
    'livesettings',
    'satchmo_store.contact',
    'product',
    # ****
    # * Optional feature, product brands
    # * Uncomment below, and add the brand url in your satchmo_urls setting
    # * usually in local_settings.py
    # ****
    #'satchmo_ext.brand'
    'shipping',
    'payment',
    'payment.modules.giftcertificate',
    'satchmo_store.contact.supplier',
    'satchmo_utils',
    'satchmo_utils.thumbnail',
    'l10n',
    'tax',
#    'satchmo_ext.recentlist',
    'satchmo_ext.wishlist',
    'satchmo_ext.upsell',
    'satchmo_ext.productratings',
    'app_plugins',
    # ****
    # * Optional Feature, Tiered shipping
    # * uncomment below to make that shipping module available in your live site
    # * settings page. enable it there, then configure it in the
    # * admin/tiered section of the main admin page.
    # ****
    #'shipping.modules.tiered'
    # ****
    # * Optional feature newsletter
    # ****
    #'satchmo_ext.newsletter',
    # ****
    # * Optional feature product feeds
    # * These are usually for googlebase
    # ****
    #'satchmo_ext.product_feeds',
    # ****
    # * Optional feature, tiered pricing
    # * uncomment below, then set up in your main admin page.
    # ****
    #'satchmo_ext.tieredpricing',
    # ****
    # * Highly recommended app - use this to have access to the great
    # * "Jobs" system.  See http://code.google.com/p/django-command-extensions/
    # * Make sure to set up your crontab to run the daily, hourly and monthly
    # * jobs.
    # ****
    #'django_extensions',
    
)

AUTHENTICATION_BACKENDS = (
    'satchmo_store.accounts.email-auth.EmailBackend',
    'django.contrib.auth.backends.ModelBackend',
)

AUTH_PROFILE_MODULE='contact.Contact'
LOGIN_REDIRECT_URL = '/accounts/'

# Locale path settings.  Needs to be set for Translation compilation.
# It can be blank
# LOCALE_PATHS = ""

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

# Languages for your site.  The language name
# should be the utf-8 encoded local name for the language.
gettext_noop = lambda s:s

LANGUAGES = (
    ('en', gettext_noop('English')),
)

from django.conf.urls.defaults import patterns, include

SATCHMO_SETTINGS = {
    # this will override any urls set in the store url modules
    'SHOP_URLS' : patterns('',
        # disable this if you don't want multi-language
        (r'^i18n/', include('l10n.urls')),
    
        # paypal urls need special treatment
        # (r'^checkout/pay/$', 'payment.modules.paypal.checkout_step2.pay_ship_info', 
        #     {'SSL': False}, 'satchmo_checkout-step2'),
        # (r'^checkout/confirm/$', 'paypal.checkout_step3.confirm_info', 
        #     {'SSL': False}, 'satchmo_checkout-step3'),                
    ),
    
    # This is the base url for the shop.  Only include a leading slash
    # examples: '/shop' or '/mystore'
    # If you want the shop at the root directory, set SHOP_BASE to ''
    'SHOP_BASE' : '/store',
    
    # Set this to true if you want to use the multi-shop features
    # of satchmo.  It requires the "threaded_multihost" application
    # to be on your pythonpath.
    'MULTISHOP' : False,    
}

# Load the local settings
from local_settings import *
