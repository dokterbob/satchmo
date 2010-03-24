from django.core.management.base import NoArgsCommand

class Command(NoArgsCommand):
    help = ("Invokes recurring billing system to do stuff like "
            "charge subscription customers each month.  You typically "
            "want to invoke this from a cron script.  For non-root "
            "users this is generally done with ``crontab -e``.")

    def handle_noargs(self, **options):
        from payment.views.cron import cron_rebill
        cron_rebill()
