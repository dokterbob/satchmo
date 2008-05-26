#!/usr/bin/env python

# This will effectively place satchmo files but there needs to
# be extra work before this would work correctly

from distutils.core import setup
import os

# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir:
    os.chdir(root_dir)

for dirpath, dirnames, filenames in os.walk('satchmo'):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        pkg = dirpath.replace(os.path.sep, '.')
        if os.path.altsep:
            pkg = pkg.replace(os.path.altsep, '.')
        packages.append(pkg)
    elif filenames:
        prefix = dirpath[8:] # Strip "satchmo/" or "satchmo\"
        for f in filenames:
            data_files.append(os.path.join(prefix, f))

# Dynamically calculate the version based on django.VERSION.
version_tuple = __import__('satchmo').VERSION
if version_tuple[2] is not None:
    version = "%d.%d_%s" % version_tuple
else:
    version = "%d.%d" % version_tuple[:2]

setup(name = "Satchmo",
      version = version,
      author = "Chris Moffitt",
      author_email = "chris@moffitts.net",
      url = "http://www.satchmoproject.com",
      license = "BSD",
      description = "The webshop for perfectionists with deadlines.",
      long_description = "Satchmo is an ecommerce framework created using Django.",
      package_dir = {'satchmo': 'satchmo'},
      packages = packages,
      package_data = {'satchmo': data_files},
      classifiers = [
      'Development Status :: 4 - Beta',
      'License :: OSI Approved :: BSD License',
      'Operating System :: OS Independent', 
      'Topic :: Office/Business',
      ]
     )

