from django.core.management.base import NoArgsCommand
import os
import shutil

class Command(NoArgsCommand):
    help = "Copy the satchmo urls and settings files to the current project."

    def handle_noargs(self, **options):
        import satchmo
        url_src = os.path.join(satchmo.__path__[0],'urls.py')
        url_dest = os.path.join(os.getcwd(), 'satchmo-urls.py')
        shutil.copyfile(url_src, url_dest)
        print "Copied %s to %s" % (url_src, url_dest)
        settings_src = os.path.join(satchmo.__path__[0],'local_settings-customize.py')
        settings_dest = os.path.join(os.getcwd(), 'local_settings.py')
        shutil.copyfile(settings_src, settings_dest)
        print "Copied %s to %s" % (settings_src, settings_dest)
        
