from django.core.management.base import NoArgsCommand
import os
import shutil
import string

class Command(NoArgsCommand):
    help = "Copy the satchmo template directory and files to the local project."

    def handle_noargs(self, **options):
        import satchmo
        template_src = os.path.join(satchmo.__path__[0],'templates')
        template_dest = os.path.join(os.getcwd(), 'templates')
        if os.path.exists(template_dest):
            print "Template directory exists. You must manually copy the files you need."
        else:
            shutil.copytree(template_src, template_dest)
            shutil.rmtree(os.path.join(template_dest,'.svn'), True)
            print "Copied %s to %s" % (template_src, template_dest)

