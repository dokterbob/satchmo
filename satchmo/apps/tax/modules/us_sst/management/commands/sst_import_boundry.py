from django.core.management.base import BaseCommand
import os
from datetime import date

# We don't actually need it, but otherwise livesettings chokes.
import tax.config

from tax.modules.us_sst.models import TaxRate, TaxBoundry
from decimal import Decimal

def ash_split(arg, qty):
    """Unfortunately, states don't alwys publish the full SST fields in the
    boundry files like they are required to. It's a shame really. So this function
    will force a string to split to 'qty' fields, adding None values as needed to
    get there.
    """
    l = arg.split(',')
    if len(l) < qty:
        l.extend([None for x in xrange(qty-len(l))])
    return l

CSV_MAP = (
    'recordType', 'startDate', 'endDate',
    'lowAddress', 'highAddress', 'oddEven',
    'streetPreDirection', 'streetName', 'streetSuffix', 'streetPostDirection',
    'addressSecondaryAbbr', 'addressSecondaryLow', 'addressSecondaryHigh', 'addressSecondaryOddEven',
    'cityName', 'zipCode', 'plus4', 
    'zipCodeLow', 'zipExtensionLow', 'zipCodeHigh', 'zipExtensionHigh',
    'serCode',
    'fipsStateCode', 'fipsStateIndicator', 'fipsCountyCode', 'fipsPlaceCode', 'fipsPlaceType',
    'long', 'lat',
    'special_1_source', 'special_1_code', 'special_1_type',
    'special_2_source', 'special_2_code', 'special_2_type',
    'special_3_source', 'special_3_code', 'special_3_type',
    'special_4_source', 'special_4_code', 'special_4_type',
    'special_5_source', 'special_5_code', 'special_5_type',
    'special_6_source', 'special_6_code', 'special_6_type',
    'special_7_source', 'special_7_code', 'special_7_type',
    'special_8_source', 'special_8_code', 'special_8_type',
    'special_9_source', 'special_9_code', 'special_9_type',
    'special_10_source', 'special_10_code', 'special_10_type',
    'special_11_source', 'special_11_code', 'special_11_type',
    'special_12_source', 'special_12_code', 'special_12_type',
    'special_13_source', 'special_13_code', 'special_13_type',
    'special_14_source', 'special_14_code', 'special_14_type',
    'special_15_source', 'special_15_code', 'special_15_type',
    'special_16_source', 'special_16_code', 'special_16_type',
    'special_17_source', 'special_17_code', 'special_17_type',
    'special_18_source', 'special_18_code', 'special_18_type',
    'special_19_source', 'special_19_code', 'special_19_type',
    'special_20_source', 'special_20_code', 'special_20_type',
)
# Some fields we're not using.
DELETE_FIELDS = (
    'long', 'lat',
    'special_1_source',
    'special_2_source',
    'special_3_source',
    'special_4_source',
    'special_5_source',
    'special_6_source',
    'special_7_source',
    'special_8_source',
    'special_9_source',
    'special_10_source',
    'special_11_source',
    'special_12_source',
    'special_13_source',
    'special_14_source',
    'special_15_source',
    'special_16_source',
    'special_17_source',
    'special_18_source',
    'special_19_source',
    'special_20_source',
)
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
        total = 0
        file = args[0]
        if not os.path.isfile(file):
            raise RuntimeError("File: %s is not a normal file or doesn't exist." % file)
        file = open(file)
        print "Processing: ",
        for line in file:
            line = line.strip()
            #Z,20080701,99991231,,,,,,,,,,,,,,,00073,,00073,,EXTRA
            fields = ash_split(line, len(CSV_MAP))

            # Turn it all into a dict so we can search for a duplicate,
            # Then remove the keys we don't care about or use.
            d = dict([(x, fields.pop(0)) for x in CSV_MAP])
            for v in DELETE_FIELDS:
                del(d[v])

            d['recordType'] = d['recordType'].upper()
            d['startDate'] = date(int(d['startDate'][0:4]), int(d['startDate'][4:6]), int(d['startDate'][6:9]))
            d['endDate'] = date(int(d['endDate'][0:4]), int(d['endDate'][4:6]), int(d['endDate'][6:9]))

            # Empty strings are nulls.
            for k in d.keys():
                if d[k] == '':
                    d[k] = None

            if d['recordType'] == 'A':
                # For now, skip these, as they barely work.
                # Zip+4 is the best way always. These are a bad idea in general.
                continue

                d['lowAddress'] = int(d['lowAddress'])
                d['highAddress'] = int(d['highAddress'])
                d['oddEven'] = d['oddEven'].upper()
                d['addressSecondaryOddEven'] = d['addressSecondaryOddEven'].upper()
                d['zipCode']          = int(d['zipCode'])
                d['plus4']            = int(d['plus4'])
            elif d['recordType'] == '4':
                d['zipCodeLow']       = int(d['zipCodeLow'])
                d['zipExtensionLow']  = int(d['zipExtensionLow'])
                d['zipCodeHigh']      = int(d['zipCodeHigh'])
                d['zipExtensionHigh'] = int(d['zipExtensionHigh'])
            elif d['recordType'] == 'Z':
                d['zipCodeLow']       = int(d['zipCodeLow'])
                d['zipCodeHigh']      = int(d['zipCodeHigh'])

            end = d['endDate']
            del(d['endDate'])

            try:
                tb = TaxBoundry.objects.get(**d)
                # Over time, end dates can change. A new row with a new start
                # date will also appear. This way, loading a new file correctly
                # updates the map. (I hope.)
                if tb.endDate != end:
                    tb.endDate = end
                    tb.save()
                    total += 1
                    updated += 1
                else:
                    total += 1
                    unchanged += 1

            except TaxBoundry.DoesNotExist:
                # Put the end back, and save it.
                d['endDate'] = end
                try:
                    TaxBoundry(**d).save()
                    total += 1
                    new += 1
                except:
                    print "Error loading the following row:"
                    for k in CSV_MAP:
                        if k in d:
                            print "%s: '%s'" % (k, d[k])
                    raise

            if total % 100 == 0:
                print "%s," % total,
                
            # Now, handle mapping boundries to rates.
            #extra = SER,state_providing,state_taxed,County,Place,Class,Long,Lat, (ST/VD,Special Code,Special Type,) x 20
            # IF SER, then the tax module should report all sales taxes by that SER code.
            # Otherwise, report it by each applicable tax.
            # Total tax is still the same in both cases. Just the state wants it reported differently.
        print ""
        print "Done: New: %d. End date changed: %d. Unchanged: %d" % (new, updated, unchanged)
