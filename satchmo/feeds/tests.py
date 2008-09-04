from django.conf import settings
from django.core import urlresolvers
from django.test import TestCase
from satchmo import caching
from satchmo.shop import get_satchmo_setting

domain = 'http://example.com'
prefix = get_satchmo_setting('SHOP_BASE')
if prefix == '/':
    prefix = ''

class GoogleBaseTest(TestCase):
    """Test Google Base feed."""

    fixtures = ['l10n-data.yaml','sample-store-data.yaml', 'products.yaml', 'test-config.yaml']

    def tearDown(self):
        caching.cache_delete

    def test_feed(self):
        url = urlresolvers.reverse('satchmo_atom_feed')
        print "url == " + url
        response = self.client.get(url)
        self.assertContains(response,
            "<title>Robots Attack! (Hard cover)</title>",
            count=1, status_code=200)
        self.assertContains(response,
            "<link href=\"%s%s/product/robot-attack-hard/\" />" % (
            domain, prefix), count=1, status_code=200)
