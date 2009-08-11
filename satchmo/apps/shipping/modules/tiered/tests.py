from datetime import datetime
from decimal import Decimal
from django.test import TestCase
from models import Carrier, ShippingTier, Shipper

def make_tiers(carrier, prices, expires=None):
    for min_total, price in prices:
        t = ShippingTier(carrier=carrier, 
            min_total=Decimal("%i.00" % min_total),
            price=Decimal("%i.00" % price),
            expires=expires
        )
        t.save()
    

class TieredCarrierSimpleTest(TestCase):
    fixtures = []

    def testCreate(self):
        c = Carrier(key="test", active=True)
        c.save()
        t = ShippingTier(carrier=c, 
            min_total=Decimal("0.00"),
            price=Decimal("10.00"),
            )
        t.save()
        
        self.assertEqual(c.price(Decimal("0.00")), Decimal("10.00"))
        
        
class TieredCarrierPricingTest(TestCase):
    fixtures = []

    def setUp(self):
        self.carrier = Carrier(name="pricing", active=True)
        self.carrier.save()
        t = ShippingTier(carrier=self.carrier, 
            min_total=Decimal("0.00"),
            price=Decimal("10.00"),
            )
        t.save()
        
    def testBase(self):
        self.assertEqual(self.carrier.price(Decimal("0.00")), Decimal("10.00"))
        
    def test2Prices(self):
        t = ShippingTier(carrier=self.carrier, 
            min_total=Decimal("20.00"),
            price=Decimal("15.00"),
            )
        t.save()
        
        self.assertEqual(self.carrier.price(Decimal("0.00")), Decimal("10.00"))
        self.assertEqual(self.carrier.price(Decimal("20.00")), Decimal("15.00"))

    def test4Prices(self):
        prices = (
            (20, 15),
            (30, 16),
            (40, 17)
        )
        
        make_tiers(self.carrier, prices)

        self.assertEqual(self.carrier.price(Decimal("0.00")), Decimal("10.00"))
        self.assertEqual(self.carrier.price(Decimal("20.00")), Decimal("15.00"))
        self.assertEqual(self.carrier.price(Decimal("25.00")), Decimal("15.00"))
        self.assertEqual(self.carrier.price(Decimal("30.00")), Decimal("16.00"))
        self.assertEqual(self.carrier.price(Decimal("39.99")), Decimal("16.00"))
        self.assertEqual(self.carrier.price(Decimal("40.01")), Decimal("17.00"))


class TieredCarrierExpiringTest(TestCase):
    fixtures = []

    def setUp(self):
        self.carrier = Carrier(name="pricing", active=True)
        self.carrier.save()

        base_prices = (
            (0, 10),
            (20, 15),
            (30, 16),
            (40, 17)
        )
        make_tiers(self.carrier, base_prices)
        
    def testExpired(self):
        dt = datetime(2000, 1, 1)
        
        sale_prices = (
            (0, 1),
            (20, 2),
            (30, 3),
            (40, 4)
        )
        
        make_tiers(self.carrier, sale_prices, expires=dt)

        self.assertEqual(self.carrier.price(Decimal("0.00")), Decimal("10.00"))
        self.assertEqual(self.carrier.price(Decimal("20.00")), Decimal("15.00"))
        self.assertEqual(self.carrier.price(Decimal("30.00")), Decimal("16.00"))
        self.assertEqual(self.carrier.price(Decimal("40.01")), Decimal("17.00"))

    def testNotExpired(self):
        
        now = datetime.now()
        nextyear = datetime(now.year+1, now.month, now.day)
        sale_prices = (
            (0, 1),
            (20, 2),
            (30, 3),
            (40, 4)
        )
        
        make_tiers(self.carrier, sale_prices, expires=nextyear)

        self.assertEqual(self.carrier.price(Decimal("0.00")), Decimal("1.00"))
        self.assertEqual(self.carrier.price(Decimal("20.00")), Decimal("2.00"))
        self.assertEqual(self.carrier.price(Decimal("30.00")), Decimal("3.00"))
        self.assertEqual(self.carrier.price(Decimal("40.01")), Decimal("4.00"))

        
        
        