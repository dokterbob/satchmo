# this is an extremely simple Satchmo standalone store.

import logging
import os, os.path

LOCAL_DEV = True
DEBUG = True
TEMPLATE_DEBUG = DEBUG

if LOCAL_DEV:
    INTERNAL_IPS = ('127.0.0.1',)

DIRNAME = os.path.dirname(os.path.abspath(__file__))

SATCHMO_DIRNAME = DIRNAME
    
gettext_noop = lambda s:s

LANGUAGE_CODE = 'en-us'
LANGUAGES = (
   ('en', gettext_noop('English')),
)

#These are used when loading the test data
SITE_NAME = "simple"

DATABASE_NAME = os.path.join(DIRNAME, 'simple.db')
SECRET_KEY = 'EXAMPLE SECRET KEY'

##### For Email ########
# If this isn't set in your settings file, you can set these here
#EMAIL_HOST = 'host here'
#EMAIL_PORT = 587
#EMAIL_HOST_USER = 'your user here'
#EMAIL_HOST_PASSWORD = 'your password'
#EMAIL_USE_TLS = True

#These are used when loading the test data
SITE_DOMAIN = "localhost"
SITE_NAME = "Simple Satchmo"

# not suitable for deployment, for testing only, for deployment strongly consider memcached.
CACHE_BACKEND = "locmem:///"
CACHE_TIMEOUT = 60*5
CACHE_PREFIX = "Z"

ACCOUNT_ACTIVATION_DAYS = 7

#Configure logging
LOGFILE = "satchmo.log"
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename=os.path.join(DIRNAME,LOGFILE),
                    filemode='w')

logging.getLogger('keyedcache').setLevel(logging.INFO)
logging.getLogger('l10n').setLevel(logging.INFO)
logging.info("Satchmo Started")
