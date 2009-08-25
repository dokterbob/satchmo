from datetime import datetime
from django.test import TestCase
from l10n.models import Country
from shipping.modules.tieredweight.models import Carrier, TieredWeightException

try:
    from decimal import Decimal
except:
    from django.utils._decimal import Decimal


def make_tiers(zone, prices, expires=None):
    for weight, handling, price in prices:
        zone.tiers.create(
            min_weight=Decimal(weight),
            handling=Decimal('%i.00' % handling),
            price=Decimal('%i.00' % price),
            expires=expires
        )


class TieredWeightTest(TestCase):
    def setUp(self):
        self.carrier = Carrier.objects.create(name='pricing', active=True)
        self.zone = self.carrier.zones.create(name='zone 1')
        self.zone.tiers.create(
            min_weight=Decimal('1'),
            handling=Decimal('10.00'),
            price=Decimal('1.00'),
        )


    def testBase(self):
        self.assertEqual(self.zone.cost(1), Decimal('11.00'))
        self.assertRaises(TieredWeightException, self.zone.cost, 4)

        
    def testTwoPrices(self):
        self.zone.tiers.create(
            min_weight=Decimal('10.00'),
            handling=Decimal('10.00'),
            price=Decimal('2.00'),
        )
        self.assertEqual(self.zone.cost(1), Decimal('11.00'))
        self.assertEqual(self.zone.cost(9), Decimal('12.00'))
        self.assertEqual(self.zone.cost(10), Decimal('12.00'))
        self.assertRaises(TieredWeightException, self.zone.cost, 100)


class TieredWeightExpiringTest(TestCase):
    def setUp(self):
        self.carrier = Carrier.objects.create(name='pricing', active=True)
        self.zone = self.carrier.zones.create(name='zone 1')
        base_prices = (
            (1, 10, 0),
            (20, 20, 1),
            (30, 30, 2),
            (40, 40, 1)
        )
        make_tiers(self.zone, base_prices)


    def testExpired(self):
        expires = datetime(2000, 1, 1)
        sale_prices = (
            (1, 1, 0),
            (20, 2, 1),
            (30, 3, 1),
            (40, 4, 1)
        )
        make_tiers(self.zone, sale_prices, expires=expires)

        self.assertEqual(self.zone.cost(1), Decimal('10.00'))
        self.assertEqual(self.zone.cost(20), Decimal('21.00'))
        self.assertEqual(self.zone.cost(30), Decimal('32.00'))
        self.assertEqual(self.zone.cost(40), Decimal('41.00'))


    def testNotExpired(self):
        now = datetime.now()
        nextyear = datetime(now.year+1, now.month, now.day)
        sale_prices = (
            (1, 1, 0),
            (20, 2, 1),
            (30, 3, 1),
            (40, 4, 1)
        )
        make_tiers(self.zone, sale_prices, expires=nextyear)

        self.assertEqual(self.zone.cost(1), Decimal('1.00'))
        self.assertEqual(self.zone.cost(10), Decimal('3.00'))
        self.assertEqual(self.zone.cost(20), Decimal('3.00'))
        self.assertEqual(self.zone.cost(30), Decimal('4.00'))
        self.assertEqual(self.zone.cost(40), Decimal('5.00'))


class TieredWeightCountryTest(TestCase):
    def setUp(self):
        self.country1 = Country.objects.create(
            iso2_code='mc',
            name='MYCOUNTRY',
            printable_name='MyCountry',
            iso3_code='mgc',
            continent='EU'
        )
        self.country2 = Country.objects.create(
            iso2_code='nc',
            name='NOTMYCOUNTRY',
            printable_name='NotMyCountry',
            iso3_code='nmc',
            continent='EU'
        )
        self.carrier = Carrier.objects.create(name='pricing', active=True)
        self.zone1 = self.carrier.zones.create(name='zone 1')
        self.zone2 = self.carrier.zones.create(name='zone 2')

        self.zone1.countries.add(self.country1)
        self.carrier.default_zone = self.zone2


    def testDefault(self):
        zone = self.carrier.get_zone(self.country1)
        self.assertEqual(zone, self.zone1)


    def testCountry(self):
        zone = self.carrier.get_zone(self.country2)
        self.assertEqual(zone, self.zone2)
