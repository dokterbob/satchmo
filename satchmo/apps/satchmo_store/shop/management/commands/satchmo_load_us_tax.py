from django.core.management.base import NoArgsCommand
from django.core.management import call_command

class Command(NoArgsCommand):
    help = "Load Satchmo country (l10n) data."
    
    def handle_noargs(self, **options):
        """Load l10n fixtures"""
        call_command('loaddata', 'us_tax.yaml', interactive=True)
