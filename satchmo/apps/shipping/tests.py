from decimal import Decimal
from django.contrib.sites.models import Site
from django.db import models
from django.test import TestCase
from livesettings import config_value
from product.models import *
from satchmo_store.shop.models import *
from shipping.modules.flat.shipper import Shipper as flat
from shipping.modules.per.shipper import Shipper as per
import keyedcache

class ShippingBaseTest(TestCase):

    fixtures = ['l10n-data.yaml','test_shop.yaml']

    def setUp(self):
        self.site = Site.objects.get_current()
        self.product1 = Product.objects.create(slug='p1', name='p1', site=self.site)
        self.cart1 = Cart.objects.create(site=self.site)
        self.cartitem1 = self.cart1.add_item(self.product1, 3)
        
    def tearDown(self):
        keyedcache.cache_delete()
        
    def test_downloadable_zero_shipping(self):
        subtypes = config_value('PRODUCT','PRODUCT_TYPES')
        if "product::DownloadableProduct" in subtypes:
            subtype2 = DownloadableProduct.objects.create(product=product1)
            self.assertEqual(product1.get_subtypes(), ('ConfigurableProduct', 'DownloadableProduct'))
            
            self.assertFalse(subtype2.is_shippable)
            self.assertFalse(self.product1.is_shippable)
            self.assertFalse(self.cart1.is_shippable)
            self.assertEqual(flat(self.cart1, None).cost(), Decimal("0.00"))
            self.assertEqual(per(self.cart1, None).cost(), Decimal("0.00"))


    def test_simple_shipping(self):
        # Product.is_shippable should be True unless the Product has a subtype
        # where is_shippable == False
        subtype1 = ConfigurableProduct.objects.create(product=self.product1)
        self.assert_(getattr(subtype1, 'is_shippable', True))
        self.assert_(self.cartitem1.is_shippable)
        self.assert_(self.product1.is_shippable)
        self.assert_(self.cart1.is_shippable)
        self.assertEqual(flat(self.cart1, None).cost(), Decimal("4.00"))
        self.assertEqual(per(self.cart1, None).cost(), Decimal("12.00"))
