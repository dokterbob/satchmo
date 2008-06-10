# Django settings for satchmo project.
# If you have an existing project, then ensure that you modify local_settings-customize.py
# and import it from your main settings file. (from local_settings import *)
import os

DIRNAME = os.path.abspath(os.path.dirname(__file__))

DJANGO_PROJECT = 'satchmo'
DJANGO_SETTINGS_MODULE = 'satchmo.settings'

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
    "satchmo.shop.SSLMiddleware.SSLRedirect",
    "satchmo.recentlist.middleware.RecentProductMiddleware",
)

#this is used to add additional config variables to each request
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.media',
    'satchmo.recentlist.context_processors.recent_products',
    'satchmo.shop.context_processors.settings',
)

ROOT_URLCONF = 'satchmo.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates".
    # Always use forward slashes, even on Windows.
    os.path.join(DIRNAME, "templates"),
)

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.comments',
    'comment_utils', # get this from http://code.google.com/p/django-comment-utils
    'django.contrib.sessions',
    'django.contrib.sitemaps',
    'django.contrib.sites',
    #'registration',
    'satchmo',
    'satchmo.caching',
    'satchmo.configuration',
    'satchmo.shop',
    'satchmo.contact',
    'satchmo.product',
    'satchmo.shipping',
    'satchmo.payment',
    'satchmo.discount',
    'satchmo.giftcertificate',
    'satchmo.supplier',
    'satchmo.thumbnail',
    'satchmo.l10n',
    'satchmo.tax',
    'satchmo.recentlist',
    'satchmo.wishlist',
    # enable tiered to activate the "tiered" shipping module
    # select it in the site settings, then configure it in the
    # admin/tiered section
    #'satchmo.shipping.modules.tiered'
    #'satchmo.newsletter',
    #'satchmo.feeds',
)

AUTHENTICATION_BACKENDS = (
    'satchmo.accounts.email-auth.EmailBackend',
    'django.contrib.auth.backends.ModelBackend',
)

# Load the local settings
from local_settings import *
