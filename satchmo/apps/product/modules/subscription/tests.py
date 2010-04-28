from decimal import Decimal
from django.contrib.sites.models import Site
from django.core import urlresolvers
from django.test import TestCase
from django.test.client import Client
from product.models import *
from satchmo_store.contact.models import *
from satchmo_store.shop.models import *
import keyedcache

class TestRecurringBilling(TestCase):
    fixtures = ['l10n-data.yaml', 'test_shop.yaml', 'sub_products.yaml', 'config', 'initial_data.yaml']

    def setUp(self):
        self.customer = Contact.objects.create(first_name='Jane', last_name='Doe')
        US = Country.objects.get(iso2_code__iexact="US")
        self.customer.addressbook_set.create(street1='123 Main St', city='New York', state='NY', postal_code='12345', country=US)
        import datetime
        site = Site.objects.get_current()
        for product in Product.objects.all():
            price, expire_length = self.getTerms(product)
            if price is None:
                continue
            order = Order.objects.create(contact=self.customer, shipping_cost=0, site=site)
            order.orderitem_set.create(
                product=product,
                quantity=Decimal('1'),
                unit_price=price,
                line_item_price=price,
                expire_date=datetime.datetime.now() + datetime.timedelta(days=expire_length),
                completed=True
            )
            order.recalculate_total()
            order.payments.create(order=order, payment='DUMMY', amount=order.total)
            order.save()

    def tearDown(self):
        keyedcache.cache_delete()

    def testProductType(self):
        product1 = Product.objects.get(slug='membership-p1')
        product2 = Product.objects.get(slug='membership-p2')
        self.assertEqual(product1.subscriptionproduct.expire_length, 21)
        self.assertEqual(product1.subscriptionproduct.recurring, True)
        self.assertEqual(product1.subscriptionproduct.recurring, True)
        self.assertEqual(product1.price_set.all()[0].price, Decimal('3.95'))
        self.assertEqual(product2.subscriptionproduct.get_trial_terms(0).expire_length, 7)

    def testCheckout(self):
       pass

    def testCronRebill(self):
        for order in OrderItem.objects.all():
            price, expire_length = self.getTerms(order.product)
            if price is None:
                continue
            self.assertEqual(order.expire_date, datetime.date.today() + datetime.timedelta(days=expire_length))
            #set expire date to today for upcoming cron test
            order.expire_date = datetime.date.today()
            order.save()

        order_count = OrderItem.objects.count()
        self.c = Client()
        url = urlresolvers.reverse('satchmo_cron_rebill')
        self.response = self.c.get(url)
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(self.response.content, 'Authentication Key Required')

        self.response = self.c.get(url, data={'key': config_value('PAYMENT','CRON_KEY')})
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(self.response.content, '')
        self.assert_(order_count < OrderItem.objects.count())
        self.assertEqual(order_count, OrderItem.objects.count()/2.0)
        for order in OrderItem.objects.filter(expire_date__gt=datetime.datetime.now()):
            price, expire_length = self.getTerms(order.product, ignore_trial=True)
            if price is None:
                continue
            self.assertEqual(order.expire_date, datetime.date.today() + datetime.timedelta(days=expire_length))
            self.assertEqual(order.order.balance, Decimal('0.00'))

    def getTerms(self, object, ignore_trial=False):
        if object.subscriptionproduct.get_trial_terms().count() and ignore_trial is False:
            price = object.subscriptionproduct.get_trial_terms(0).price
            expire_length = object.subscriptionproduct.get_trial_terms(0).expire_length
            return price, expire_length
        elif object.is_subscription or ignore_trial is True:
            price = object.price_set.all()[0].price
            expire_length = object.subscriptionproduct.expire_length
            return price, expire_length
        else:
            return None, None #it's not a recurring object so no test will be done

