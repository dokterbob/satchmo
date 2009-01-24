from django.core.management.base import NoArgsCommand
import os
import shutil

class Command(NoArgsCommand):
    help = "Copy the satchmo static directory and files to the local project."

    def handle_noargs(self, **options):
        import satchmo_store
        static_src = os.path.join(satchmo_store.__path__[0],'../../static')
        # The static dir could be in a different relative location
        # if satchmo was installed using setup utils
        if not os.path.exists(static_src):
            static_src = os.path.join(satchmo_store.__path__[0],'../static')
        static_dest = os.path.join(os.getcwd(), 'static')
        if os.path.exists(static_dest):
            print "Static directory exists. You must manually copy the files you need."
        else:
            shutil.copytree(static_src, static_dest)
            for root, dirs, files in os.walk(static_dest):
                if '.svn' in dirs:
                    shutil.rmtree(os.path.join(root,'.svn'), True)
            print "Copied %s to %s" % (static_src, static_dest)
