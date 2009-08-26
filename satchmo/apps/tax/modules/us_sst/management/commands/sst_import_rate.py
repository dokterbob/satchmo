from django.core.management.base import BaseCommand
import os
from datetime import date
from tax.modules.us_sst.models import TaxRate
from decimal import Decimal

class Command(BaseCommand):
    '''Manage command to import one of the CSV files from the SST website.

    To update: Simple re-run on the newer CSV file.
    Any unchanged entries will be left alone, and any changed ones will get
    their end dates set properly and the new rows inserted. You will need to do
    this quartly or as-needed by your tax jurisdictions.'''

    def handle(self, *args, **options):
        new = 0
        updated = 0
        unchanged = 0
        file = args[0]
        if not os.path.isfile(file):
            raise RuntimeError("File: %s is not a normal file or doesn't exist." % file)
        file = open(file)
        for line in file:
            (state, type, code, rate_intra, rate_inter, food_intra, food_inter,
             start, end) = line.split(',')
            state = int(state)
            start = date(int(start[0:4]), int(start[4:6]), int(start[6:9]))
            end = date(int(end[0:4]), int(end[4:6]), int(end[6:9]))
            try:
                tr = TaxRate.objects.get(
                    state=state,
                    jurisdictionType=type,
                    jurisdictionFipsCode=code,
                    startDate=start,
                )
                # Over time, end dates can change. A new row with a new start
                # date will also appear. This way, loading a new file correctly
                # updates the map. (I hope.)
                if tr.endDate != end:
                    tr.endDate = end
                    tr.save()
                    updated += 1
                else:
                    unchanged += 1

            except TaxRate.DoesNotExist:
                TaxRate(
                    state=state,
                    jurisdictionType=type,
                    jurisdictionFipsCode=code,
                    startDate=start,
                    endDate=end,
                    generalRateIntrastate = Decimal(rate_intra),
                    generalRateInterstate = Decimal(rate_inter),
                    foodRateIntrastate = Decimal(food_intra),
                    foodRateInterstate = Decimal(food_inter),
                ).save()
                new += 1
        print "Done: New: %d. End date changed: %d. Unchanged: %d" % (new, updated, unchanged)
