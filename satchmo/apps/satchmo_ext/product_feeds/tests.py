from django.conf import settings
from django.core import urlresolvers
from django.test import TestCase
from product.models import Product
import keyedcache

domain = 'http://example.com'

class GoogleBaseTest(TestCase):
    """Test Google Base feed."""

    fixtures = ['l10n-data.yaml','sample-store-data.yaml', 'products.yaml', 'test-config.yaml']

    def tearDown(self):
        keyedcache.cache_delete

    def test_feed(self):
        url = urlresolvers.reverse('satchmo_atom_feed')
        response = self.client.get(url)
        self.assertContains(response,
            "<title>Robots Attack! (Hard cover)</title>",
            count=1, status_code=200)
        product = Product.objects.get(slug='robot-attack-hard')
        producturl = product.get_absolute_url()
        self.assertContains(response,
            "<link href=\"%s%s\" />" % (domain, producturl), count=1, status_code=200)
