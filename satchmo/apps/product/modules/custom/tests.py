from decimal import Decimal
from django.core import mail
from django.core.urlresolvers import reverse as url
from django.test import TestCase
from django.test.client import Client
from django.utils.encoding import smart_str
from keyedcache import cache_delete
from l10n.models import Country
from l10n.utils import moneyfmt
from product.utils import rebuild_pricing
from satchmo_store.shop.satchmo_settings import get_satchmo_setting
from satchmo_store.shop.tests import get_step1_post_data

domain = 'http://example.com'
prefix = get_satchmo_setting('SHOP_BASE')
if prefix == '/':
    prefix = ''

class ShopTest(TestCase):
    fixtures = ['l10n-data.yaml', 'sample-store-data.yaml', 'products.yaml', 'test-config.yaml', 'initial_data.yaml']

    def setUp(self):
        # Every test needs a client
        cache_delete()
        self.client = Client()
        self.US = Country.objects.get(iso2_code__iexact = "US")
        rebuild_pricing()

    def tearDown(self):
        cache_delete()

    def test_custom_product(self):
        """
        Verify that the custom product is working as expected.
        """
        response = self.client.get(prefix+"/")
        self.assertContains(response, "Computer", count=1)
        response = self.client.get(prefix+"/product/satchmo-computer/")
        self.assertContains(response, "Memory", count=1)
        self.assertContains(response, "Case", count=1)
        self.assertContains(response, "Monogram", count=1)
        response = self.client.post(prefix+'/cart/add/', { "productname" : "satchmo-computer",
                                                      "5" : "1.5gb",
                                                      "6" : "mid",
                                                      "custom_monogram": "CBM",
                                                      "quantity" : '1'})
        self.assertRedirects(response, prefix + '/cart/',
            status_code=302, target_status_code=200)
        response = self.client.get(prefix+'/cart/')
        self.assertContains(response, '/satchmo-computer/">satchmo computer', count=1, status_code=200)
        amount = smart_str(moneyfmt(Decimal('168.00')))
        self.assertContains(response, amount, count=3)

        amount = smart_str('Monogram: CBM  ' + moneyfmt(Decimal('10.00')))
        self.assertContains(response, amount, count=1)

        amount = smart_str('Case - External Case: Mid  ' + moneyfmt(Decimal('10.00')))
        self.assertContains(response, amount, count=1)

        amount = smart_str('Memory - Internal RAM: 1.5 GB  ' + moneyfmt(Decimal('25.00')))
        self.assertContains(response, amount, count=1)

        response = self.client.post(url('satchmo_checkout-step1'), get_step1_post_data(self.US))
        self.assertRedirects(response, url('DUMMY_satchmo_checkout-step2'),
            status_code=302, target_status_code=200)
        data = {
            'credit_type': 'Visa',
            'credit_number': '4485079141095836',
            'month_expires': '1',
            'year_expires': '2012',
            'ccv': '552',
            'shipping': 'FlatRate'}
        response = self.client.post(url('DUMMY_satchmo_checkout-step2'), data)
        self.assertRedirects(response, url('DUMMY_satchmo_checkout-step3'),
            status_code=302, target_status_code=200)
        response = self.client.get(url('DUMMY_satchmo_checkout-step3'))

        amount = smart_str('satchmo computer - ' + moneyfmt(Decimal('168.00')))
        self.assertContains(response, amount, count=1, status_code=200)
        response = self.client.post(url('DUMMY_satchmo_checkout-step3'), {'process' : 'True'})
        self.assertRedirects(response, url('DUMMY_satchmo_checkout-success'),
            status_code=302, target_status_code=200)
        self.assertEqual(len(mail.outbox), 1)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
