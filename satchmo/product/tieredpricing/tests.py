try:
    from decimal import Decimal
except:
    from django.utils._decimal import Decimal

from django.contrib.auth.models import User, Group
from django.test import TestCase
from satchmo import caching
from satchmo.product.models import Product, Price
from satchmo.product.tieredpricing.models import *
from threaded_multihost.threadlocals import set_current_user

class TieredTest(TestCase):
    """Test Tiered Pricing"""
    fixtures = ['l10n-data.yaml','sample-store-data.yaml', 'products.yaml', 'test-config.yaml']

    def setUp(self):
        tieruser = User.objects.create_user('timmy', 'timmy@example.com', '12345')
        stduser = User.objects.create_user('tommy', 'tommy@example.com', '12345')
        tieruser.save()
        stduser.save()
        self.tieruser = tieruser
        self.stduser = stduser
        tiergroup = Group(name="tiertest")
        tiergroup.save()
        tieruser.groups.add(tiergroup)
        self.tier = PricingTier(group=tiergroup, title="Test Tier", discount_percent=Decimal('10.0'))
        self.tier.save()
        set_current_user(tieruser)

    def tearDown(self):
        caching.cache_delete()

    def test_simple_tier(self):
        """Check quantity price for a standard product using the default pricing tier"""

        product = Product.objects.get(slug='PY-Rocks')
        # 10% discount from 19.50
        self.assertEqual(product.unit_price, Decimal("17.550"))
        
    def test_no_tier_user(self):
        """Check price when user doesn't have a tier"""
        product = Product.objects.get(slug='PY-Rocks')
        set_current_user(self.stduser)
        self.assertEqual(product.unit_price, Decimal("19.50"))
        
    def test_tieredprice(self):
        """Test setting an explicit tieredprice on a product"""
        product = Product.objects.get(slug='PY-Rocks')
        tp = TieredPrice(product=product, pricingtier=self.tier, quantity=1, price=Decimal('10.00'))
        tp.save()
        self.assertEqual(product.unit_price, Decimal("10.00"))        

    def test_tieredprice_no_tier_user(self):
        """Test setting an explicit tieredprice on a product, but no tier for user"""
        product = Product.objects.get(slug='PY-Rocks')
        tp = TieredPrice(product=product, pricingtier=self.tier, quantity=1, price=Decimal('5.00'))
        tp.save()
        set_current_user(self.stduser)
        self.assertEqual(product.unit_price, Decimal("19.50"))
    