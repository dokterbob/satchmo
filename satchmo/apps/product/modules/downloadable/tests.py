from decimal import Decimal
from django.contrib.sites.models import Site
from django.test import TestCase
from product.models import Product
from product.modules.downloadable.models import DownloadableProduct
from satchmo_store.shop.models import Cart
from shipping.modules.flat.shipper import Shipper as flat
from shipping.modules.per.shipper import Shipper as per
import keyedcache

class DownloadableShippingTest(TestCase):

    fixtures = ['l10n-data.yaml','test_shop.yaml']

    def setUp(self):
        self.site = Site.objects.get_current()
        self.product1 = Product.objects.create(slug='p1', name='p1', site=self.site)
        self.cart1 = Cart.objects.create(site=self.site)
        self.cartitem1 = self.cart1.add_item(self.product1, 3)

    def tearDown(self):
        keyedcache.cache_delete()

    def test_downloadable_zero_shipping(self):
        subtype2 = DownloadableProduct.objects.create(product=self.product1)
        self.assertEqual(self.product1.get_subtypes(), ('DownloadableProduct',))

        self.assertFalse(subtype2.is_shippable)
        self.assertFalse(self.product1.is_shippable)
        self.assertFalse(self.cart1.is_shippable)
        self.assertEqual(flat(self.cart1, None).cost(), Decimal("0.00"))
        self.assertEqual(per(self.cart1, None).cost(), Decimal("0.00"))

