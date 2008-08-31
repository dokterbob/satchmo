from django.core.management.base import NoArgsCommand
import sys
try:
    from decimal import Decimal
except:
    from django.utils._decimal import Decimal


class Command(NoArgsCommand):
    help = "Check the system to see if the Satchmo components are installed correctly."
    
    def handle_noargs(self, **options):
        from django.conf import settings
        errors = []
        print "Checking your satchmo configuration."
        try:
            import satchmo
        except ImportError:
            errors.append("Satchmo is not installed correctly. Please verify satchmo is on your sys path.")
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
             from satchmo.l10n.utils import get_locale_conv
             get_locale_conv()
        except:
            errors.append("""
            Locale is not set correctly.  Try 
            Unix: sudo locale-gen en_US  
            Windows: set LANGUAGE_CODE in settings.py to LANGUAGE_CODE = 'us'
            """)
        try:
            cache_avail = settings.CACHE_BACKEND
        except AttributeError:
            errors.append("A CACHE_BACKEND must be configured.")

        if 'satchmo.shop.SSLMiddleware.SSLRedirect' not in settings.MIDDLEWARE_CLASSES:
            errors.append("You must have satchmo.shop.SSLMiddleware.SSLRedirect in your MIDDLEWARE_CLASSES.")
        if 'satchmo.shop.context_processors.settings' not in settings.TEMPLATE_CONTEXT_PROCESSORS:
            errors.append("You must have satchmo.shop.context_processors.settings in your TEMPLATE_CONTEXT_PROCESSORS.")
        if 'satchmo.accounts.email-auth.EmailBackend' not in settings.AUTHENTICATION_BACKENDS:
            errors.append("You must have satchmo.accounts.email-auth.EmailBackend in your AUTHENTICATION_BACKENDS")
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
