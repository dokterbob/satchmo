from django.conf import settings
from django.core import urlresolvers
from django.test import TestCase

domain = 'http://example.com'
prefix = settings.SHOP_BASE
if prefix == '/':
    prefix = ''

class GoogleBaseTest(TestCase):
    """Test Google Base feed."""

    fixtures = ['sample-store-data.yaml', 'products.yaml', 'test-config.yaml']

    def test_feed(self):
        response = self.client.get(urlresolvers.reverse('satchmo_atom_feed'))
        self.assertContains(response,
            "<title>Robots Attack! (Hard cover)</title>",
            count=1, status_code=200)
        self.assertContains(response,
            "<link href=\"%s%s/product/robot-attack_hard/\" />" % (
            domain, prefix), count=1, status_code=200)
