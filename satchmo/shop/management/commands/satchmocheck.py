from django.core.management.base import NoArgsCommand
import sys
from decimal import Decimal

class Command(NoArgsCommand):
    help = "Check the system to see if the Satchmo components are installed correctly."
    
    def handle_noargs(self, **options):
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
            import comment_utils
        except ImportError:
            errors.append("Django comment_utils is not installed.")
        try:
            import registration
        except ImportError:
            errors.append("Django registration is not installed.")
        try:
            import yaml
        except ImportError:
            errors.append("YAML is not installed.")
        python_ver = Decimal("%s.%s" % (sys.version_info[0], sys.version_info[1]))
        if python_ver < Decimal("2.4"):
            errors.append("Python version must be at least 2.4.")
        if python_ver < Decimal("2.5"):
            try:
                from xml.etree.ElementTree import Element
            except ImportError:
                errors.append("Elementtree is not installed.")
        if len(errors) == 0:
            print "Your configuration has no errors."
        else:
            print "The following errors were found:"
            for error in errors:
                print error
