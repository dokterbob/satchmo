from django.core import urlresolvers
from django.test import TestCase
from django.test.client import Client
import keyedcache
from livesettings import config_get
from satchmo_ext.newsletter import *
from satchmo_ext.newsletter.models import get_contact_or_fake, Subscription
import logging

log = logging.getLogger('test');

class NewsletterTest(TestCase):
    
    def setUp(self):
        cfg = config_get('NEWSLETTER', 'MODULE')
        cfg.update('satchmo_ext.newsletter.simple')
        
    def tearDown(self):
        keyedcache.cache_delete()
        
    def  testNewIsUnsubscribed(self):
        c = get_contact_or_fake('test test', 'testnew@test.com')
        sub = is_subscribed(c)
        self.assertFalse(sub)
        
    def  testExplicitUnsubscribed(self):
        c = get_contact_or_fake('test test', 'explicitno@test.com')
        results = update_subscription(c, False)
        sub = is_subscribed(c)
        self.assertFalse(sub)
        
    def  testExplicitSubscribed(self):
        c = get_contact_or_fake('test test', 'explicityes@test.com')
        results = update_subscription(c, True)
        sub = is_subscribed(c)
        self.assertTrue(sub)

    def testSetReset(self):
        c = get_contact_or_fake('test test', 'setreset@test.com')
        results = update_subscription(c, True)
        sub = is_subscribed(c)
        self.assertTrue(sub)
        
        results = update_subscription(c, False)
        sub = is_subscribed(c)
        self.assertFalse(sub)
        
    def testAttributeSetting(self):
        c = get_contact_or_fake('test test', 'setattr@test.com')
        results = update_subscription(c, True, attributes = {'var1' : 'True'})
        sub = Subscription.objects.get(email='setattr@test.com')
        self.assert_(sub)
        self.assertEqual(sub.attribute_value('var1'), 'True')
        self.assertTrue(sub.subscribed)
        
class NewsletterTestViews(TestCase):
    
    fixtures = ['l10n-data.yaml', 'sample-store-data.yaml']
    
    def setUp(self):
        cfg = config_get('NEWSLETTER', 'MODULE')
        cfg.update('satchmo_ext.newsletter.simple')
        self.client = Client()
        
    def tearDown(self):
        keyedcache.cache_delete()
    
    def  testNewIsSubscribed(self):
        url = urlresolvers.reverse('newsletter_subscribe_ajah')
        c = get_contact_or_fake('test test', 'testsubview@test.com')
        self.assertFalse(is_subscribed(c))
        
        response = self.client.post(url, {
            'full_name' : 'Testy Testerson',
            'email': c.email,
            })
    
        self.assertTrue(is_subscribed(c))

    def  testNewIsUnsubscribed(self):
        c = get_contact_or_fake('test test', 'testunsubview@test.com')
        update_subscription(c, True)
        self.assertTrue(is_subscribed(c))

        url = urlresolvers.reverse('newsletter_unsubscribe_ajah')
        response = self.client.post(url, {
            'full_name' : 'Testy Testerson',
            'email': c.email,
            })

        self.assertFalse(is_subscribed(c))
        
    
