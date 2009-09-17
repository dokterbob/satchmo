#!/usr/bin/env python
"""
This is the bootsrap installation script for Satchmo. It will make sure that
the dependencies are in place, then will create the base Satchmo configuration.

Before running this script, you must have python and pip installed.
It is also recommended that you install Python Imaging using your distribution's
package method.

To execute, download this script to a directory and run:
python getsatchmo.py

Notes:
- This file can attempt (using -p) to install Python Imaging from source. On some platforms, 
  the jpeg or other image libraries may not work as expected. The recommendation is
  to install PIL from your distributions binaries.

"""

import os
import shutil
from random import choice
import re
from optparse import OptionParser
import string

__VERSION__ = "0.1"

pip_requirements = """
django
pycrypto
http://www.satchmoproject.com/snapshots/trml2pdf-1.2.tar.gz
django-registration
PyYAML
http://www.reportlab.org/ftp/ReportLab_2_3.tar.gz
-e hg+http://bitbucket.org/bkroeze/django-threaded-multihost/#egg=django-threaded-multihost
-e hg+http://bitbucket.org/bkroeze/django-caching-app-plugins/#egg=django-caching-app-plugins
-e hg+http://bitbucket.org/bkroeze/django-signals-ahoy/#egg=django-signals-ahoy
-e hg+https://sorl-thumbnail.googlecode.com/hg/#egg=sorl-thumbnail
"""

pil_requirements = "http://effbot.org/downloads/Imaging-1.1.6.tar.gz"

def parse_command_line():
    usage = 'usage: %prog [options]'
    version = 'Version: %prog ' + '%s' % __VERSION__
    parser = OptionParser(usage=usage, version=version)
    
    parser.add_option('-s', '--site', action='store',type='string', default='store',
                     dest='site_name', help="Top level directory name for the site. [default: %default]")
    
    parser.add_option('-l', '--localsite', action='store',type='string', default='localsite',
                     dest='local_site_name', help="Name for the local application stub. [default: %default]")
                     
    parser.add_option('-p', action='store_true',dest='pil_install', default=False,
                        help="Attempt to install Python Imaging Library.")
        
    opts, args = parser.parse_args()
    
    return opts, args

def run_pip_commands():
    for line in pip_requirements.split('\n'):
        os.system('pip install %s' % line)

def install_pil():
    os.system('pip install %s' % pil_requirements)
    
def create_satchmo_site(site_name):
    import satchmo_store
    base_dir = satchmo_store.__path__[0]
    src_dir = os.path.abspath(os.path.join(base_dir, '../../projects/skeleton'))
    dest_dir = os.path.join('./',site_name)
    shutil.copytree(src_dir, dest_dir)

def customize_files(site_name, local_site_name):
    """
    We need to make a couple of change to the files copied from the skeleton directory.
    Set the SECRET_KEY to a random value
    Set the ROOT_URLCONF
    Set the DJANGO_PROJECT
    Set the DJANGO_SETTINGS_MODULE
    We also need to change the directory name to local_site_name
    """
    dest_dir = os.path.join('./',site_name)
    # Create a random SECRET_KEY hash, and put it in the main settings.
    main_settings_file = os.path.join(dest_dir, 'settings.py')
    settings_contents = open(main_settings_file, 'r').read()
    fp = open(main_settings_file, 'w')
    secret_key = ''.join([choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50)])
    settings_contents = re.sub(r"(?<=SECRET_KEY = ')'", secret_key + "'", settings_contents)
    # Configure the other variables that need to be modified
    root_urlconf = site_name + '.urls'
    settings_contents = re.sub(r"(?<=ROOT_URLCONF = ')'", root_urlconf + "'",settings_contents)
    django_settings = site_name + '.settings'
    settings_contents = re.sub(r"(?<=DJANGO_PROJECT = ')'", site_name + "'",settings_contents)
    settings_contents = re.sub(r"(?<=DJANGO_SETTINGS_MODULE = ')'", django_settings + "'",settings_contents)
    local_app = "%s.%s" % (site_name,local_site_name)
    settings_contents = settings_contents.replace("simple.localsite",local_app)
    fp.write(settings_contents)
    fp.close()
    # rename the local_app directory
    os.rename(os.path.join(dest_dir,'localsite'), os.path.join(dest_dir,local_site_name))  

def setup_satchmo(site_name, local_site_name):
    """
    Do the final configs for satchmo
    """
    os.system('cd %s && python manage.py satchmo_copy_static' % site_name)
    os.system('cd %s && python manage.py syncdb' % site_name)
    os.system('cd %s && python manage.py satchmo_load_l10n' % site_name)
    os.system('cd %s && python manage.py satchmo_load_store' % site_name)
    os.system('cd %s && python manage.py satchmo_rebuild_pricing' % site_name)
    
if __name__ == '__main__':
    opts, args = parse_command_line()
    
    errors = []
    try:
        import pip
    except:
        errors.append("You must install pip: easy_install pip")
    dest_dir = os.path.join('./',opts.site_name)
    if os.path.isdir(dest_dir):
        errors.append("The destination directory already exists. This script can only be used to create new projects.")
    if opts.pil_install:
        print "Installing Python Imaging Library"
        install_pil()
    else:
        try:
            import PIL as Image
        except ImportError:
            errors.append("The Python Imaging Library is not installed. Install from your distribution binaries of use the -p flag.")
    if errors:
        for error in errors:
            print error
        exit()
    print "Downloading and installing additional dependencies"
    run_pip_commands()
    print "Creating the Satchmo Application"
    create_satchmo_site(opts.site_name)
    print "Customizing the files"
    customize_files(opts.site_name, opts.local_site_name)
    print "Performing initial data synching"
    setup_satchmo(opts.site_name, opts.local_site_name)
    print "Store installation complete."
    print "You may run the server by typying: \n cd %s \n python manage.py runserver" % opts.site_name
