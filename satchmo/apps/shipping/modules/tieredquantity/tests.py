from datetime import datetime
from decimal import Decimal
from django.test import TestCase
from models import Carrier, QuantityTier, Shipper

def make_tiers(carrier, prices, expires=None):
    for qty, handling, price in prices:
        t = QuantityTier(carrier=carrier, 
            handling=Decimal("%i.00" % handling),
            price=Decimal("%i.00" % price),
            quantity=Decimal(qty),
            expires=expires
        )
        t.save()
    

class TieredCarrierSimpleTest(TestCase):
    fixtures = []

    def testCreate(self):
        c = Carrier(key="test", active=True)
        c.save()
        t = QuantityTier(carrier=c, 
            quantity=Decimal('1'),
            handling=Decimal("10.00"),
            price=Decimal("0.00"),
            )
        t.save()
        
        self.assertEqual(c.price(1), Decimal("10.00"))
        self.assertEqual(c.price(4), Decimal("10.00"))
        
class TieredCarrierPricingTest(TestCase):
    fixtures = []

    def setUp(self):
        self.carrier = Carrier(name="pricing", active=True)
        self.carrier.save()
        t = QuantityTier(carrier=self.carrier, 
            quantity=Decimal('1'),
            handling=Decimal("10.00"),
            price=Decimal("0.00"),
            )
        t.save()
        
    def testBase(self):
        self.assertEqual(self.carrier.price(1), Decimal("10.00"))
        self.assertEqual(self.carrier.price(10), Decimal("10.00"))
        self.assertEqual(self.carrier.price(100), Decimal("10.00"))
        
    def test2Prices(self):
        t = QuantityTier(carrier=self.carrier, 
            quantity=Decimal('10'),
            handling=Decimal("100.00"),
            price=Decimal("1.00"),
            )
        t.save()
        
        self.assertEqual(self.carrier.price(1), Decimal("10.00"))
        self.assertEqual(self.carrier.price(9), Decimal("10.00"))
        self.assertEqual(self.carrier.price(10), Decimal("110.00"))
        self.assertEqual(self.carrier.price(100), Decimal("200.00"))

class TieredCarrierExpiringTest(TestCase):
    fixtures = []

    def setUp(self):
        self.carrier = Carrier(name="pricing", active=True)
        self.carrier.save()

        base_prices = (
            (1, 10, 0),
            (20, 20, 1),
            (30, 30, 2),
            (40, 40, 1)
        )
        make_tiers(self.carrier, base_prices)
        
    def testExpired(self):
        dt = datetime(2000, 1, 1)
        
        sale_prices = (
            (1, 1, 0),
            (20, 2, 1),
            (30, 3, 1),
            (40, 4, 1)
        )
        
        make_tiers(self.carrier, sale_prices, expires=dt)

        self.assertEqual(self.carrier.price(1), Decimal("10.00"))
        self.assertEqual(self.carrier.price(20), Decimal("40.00"))
        self.assertEqual(self.carrier.price(30), Decimal("90.00"))
        self.assertEqual(self.carrier.price(100), Decimal("140.00"))

    def testNotExpired(self):
        
        now = datetime.now()
        nextyear = datetime(now.year+1, now.month, now.day)
        sale_prices = (
            (1, 1, 0),
            (20, 2, 1),
            (30, 3, 1),
            (40, 4, 1)
        )
        
        make_tiers(self.carrier, sale_prices, expires=nextyear)

        self.assertEqual(self.carrier.price(1), Decimal("1.00"))
        self.assertEqual(self.carrier.price(10), Decimal("1.00"))
        self.assertEqual(self.carrier.price(20), Decimal("22.00"))
        self.assertEqual(self.carrier.price(30), Decimal("33.00"))
        self.assertEqual(self.carrier.price(100), Decimal("104.00"))
