from django.core.management.base import NoArgsCommand
import os
import shutil

class Command(NoArgsCommand):
    help = "Copy the satchmo urls file to the current project."

    def handle_noargs(self, **options):
        import satchmo_store
        url_src = os.path.join(satchmo_store.__path__[0],'urls.py')
        url_dest = os.path.join(os.getcwd(), 'satchmo-urls.py')
        shutil.copyfile(url_src, url_dest)
        print "Copied %s to %s" % (url_src, url_dest)
