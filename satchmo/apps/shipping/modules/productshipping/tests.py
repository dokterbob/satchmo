from datetime import datetime
from decimal import Decimal
from django.test import TestCase
from models import Carrier, ProductShippingPrice, Shipper
from product.models import Product

class ProductShippingSimpleTest(TestCase):
    fixtures = ['products.yaml',]

    def testCreate(self):
        c = Carrier(key="test", active=True)
        c.save()
        product = Product.objects.get(slug='dj-rocks')
        p = ProductShippingPrice(carrier=c, 
            product=product,
            price=Decimal("10.00"),
            )
        p.save()
        
        self.assertEqual(c.price(product), Decimal("10.00"))
        
        
class ProductShippingPricingTest(TestCase):
    fixtures = ['products.yaml']

    def setUp(self):
        self.carrier = Carrier(name="pricing", active=True)
        self.carrier.save()
        self.product = Product.objects.get(slug='dj-rocks')
        t = ProductShippingPrice(carrier=self.carrier,
            product=self.product,
            price=Decimal("10.00"),
            )
        t.save()
        
    def testBase(self):
        self.assertEqual(self.carrier.price(self.product), Decimal("10.00"))
        
    def test2Prices(self):
        c2 = Carrier(name="test2", active=True)
        c2.save()
        t = ProductShippingPrice(carrier=c2,
            product=self.product,
            price=Decimal("20.00"),
            )
        t.save()
        
        self.assertEqual(self.carrier.price(self.product), Decimal("10.00"))
        self.assertEqual(c2.price(self.product), Decimal("20.00"))

    def testVariantPrices(self):
        """price for shipping a variant is the same as the master, except when it is explicitly set"""
        
        variant = Product.objects.get(slug='dj-rocks-s-b')
        
        self.assertEqual(self.carrier.price(variant), Decimal("10.00"))
        
        t = ProductShippingPrice(carrier=self.carrier,
            product=variant,
            price=Decimal("20.00"),
            )
        t.save()
        
        self.assertEqual(self.carrier.price(variant), Decimal("20.00"))
        
