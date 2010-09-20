#!/usr/bin/env python
import os.path
import sys

DIRNAME = os.path.dirname(__file__)
# trick to get the two-levels up directory, which for the "simple" project should be the satchmo dir
_parent = lambda x: os.path.normpath(os.path.join(x, '..'))

SATCHMO_DIRNAME = _parent(_parent(DIRNAME))
SATCHMO_APPS = os.path.join(SATCHMO_DIRNAME, 'apps')

if not SATCHMO_APPS in sys.path:
    sys.path.append(SATCHMO_APPS)

if not DIRNAME in sys.path:
    sys.path.append(DIRNAME)

from django.core.management import execute_manager
try:
    import settings # Assumed to be in the same directory.
except ImportError:
    import sys
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n" % __file__)
    sys.exit(1)

if __name__ == "__main__":
    execute_manager(settings)
