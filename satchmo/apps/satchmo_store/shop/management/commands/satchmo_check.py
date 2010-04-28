from django.core.management.base import NoArgsCommand
from django.core import urlresolvers
import sys
import django
from decimal import Decimal
import types

class Command(NoArgsCommand):
    help = "Check the system to see if the Satchmo components are installed correctly."
    
    def handle_noargs(self, **options):
        from django.conf import settings
        errors = []
        print "Checking your satchmo configuration."
        try:
            import satchmo_store
        except ImportError:
            errors.append("Satchmo is not installed correctly. Please verify satchmo is on your sys path.")
        print "Using Django version %s" % django.get_version()
        print "Using Satchmo version %s" % satchmo_store.get_version()
        
        # Try importing all our dependencies
        try:
            import Crypto.Cipher
        except ImportError:
            errors.append("The Python Cryptography Toolkit is not installed.")
        try:
            import Image
        except ImportError:
            try:
                import PIL as Image
            except ImportError:
                errors.append("The Python Imaging Library is not installed.")
        try:
            import reportlab
        except ImportError:
            errors.append("Reportlab is not installed.")
        try:
            import trml2pdf
        except ImportError:
            errors.append("Tiny RML2PDF is not installed.")
        try:
            import registration
        except ImportError:
            errors.append("Django registration is not installed.")
        try:
            import yaml
        except ImportError:
            errors.append("YAML is not installed.")
        try:
            import sorl
        except ImportError:
            errors.append("Sorl imaging library is not installed.")
        try:
            import app_plugins
        except ImportError:
            errors.append("App plugins is not installed.")
        try:
            import livesettings
        except ImportError:
            errors.append("Livesettings is not installed.")
        try:
            import keyedcache
        except ImportError:
            errors.append("Keyedcache is not installed.")
        try:
            cache_avail = settings.CACHE_BACKEND
        except AttributeError:
            errors.append("A CACHE_BACKEND must be configured.")
        # Try looking up a url to see if there's a misconfiguration there    
        try:
            url = urlresolvers.reverse('satchmo_search')
        except Exception, e:
            errors.append("Unable to resolve url. Received error- %s" % e)
        from l10n.l10n_settings import get_l10n_default_currency_symbol
        if not isinstance(get_l10n_default_currency_symbol(),types.UnicodeType):
            errors.append("Your currency symbol should be a unicode string.")
        if 'satchmo_store.shop.SSLMiddleware.SSLRedirect' not in settings.MIDDLEWARE_CLASSES:
            errors.append("You must have satchmo_store.shop.SSLMiddleware.SSLRedirect in your MIDDLEWARE_CLASSES.")
        if 'satchmo_store.shop.context_processors.settings' not in settings.TEMPLATE_CONTEXT_PROCESSORS:
            errors.append("You must have satchmo_store.shop.context_processors.settings in your TEMPLATE_CONTEXT_PROCESSORS.")
        if 'threaded_multihost.middleware.ThreadLocalMiddleware' not in settings.MIDDLEWARE_CLASSES:
            errors.append("You must install django threaded multihost \n and place threaded_multihost.middleware.ThreadLocalMiddleware in your MIDDLEWARE_CLASSES.")
        if 'satchmo_store.accounts.email-auth.EmailBackend' not in settings.AUTHENTICATION_BACKENDS:
            errors.append("You must have satchmo_store.accounts.email-auth.EmailBackend in your AUTHENTICATION_BACKENDS")
        if len(settings.SECRET_KEY) == 0:
            errors.append("You must have SECRET_KEY set to a valid string in your settings.py file")
        python_ver = Decimal("%s.%s" % (sys.version_info[0], sys.version_info[1]))
        if python_ver < Decimal("2.4"):
            errors.append("Python version must be at least 2.4.")
        if python_ver < Decimal("2.5"):
            try:
                from elementtree.ElementTree import Element
            except ImportError:
                errors.append("Elementtree is not installed.")
        if len(errors) == 0:
            print "Your configuration has no errors."
        else:
            print "The following errors were found:"
            for error in errors:
                print error
