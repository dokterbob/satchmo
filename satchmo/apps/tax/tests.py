from decimal import Decimal
from django.test import TestCase
from keyedcache import cache_delete
from livesettings import config_get
from models import *
from product.models import Product
from satchmo_store.contact.models import AddressBook, Contact
from satchmo_store.shop.models import Order, OrderItem, OrderPayment
from satchmo_store.shop.tests import make_test_order, make_order_payment
import datetime
import logging
log = logging.getLogger('tax.test')

def _set_percent_taxer(percent):
    
    cache_delete()
    tax = config_get('TAX','MODULE')
    tax.update('tax.modules.percent')
    pcnt = config_get('TAX', 'PERCENT')
    pcnt.update(percent)
    shp = config_get('TAX', 'TAX_SHIPPING')
    shp.update(False)
    
    return shp

class TaxTest(TestCase):
    
    fixtures = ['l10n_data.xml', 'test_tax.yaml', 'test_discount.yaml']
            
    def tearDown(self):
        cache_delete()
            
    def testAreaCountries(self):
        """Test Area tax module"""
        cache_delete()
        tax = config_get('TAX','MODULE')
        tax.update('tax.modules.area')
        
        order = make_test_order('DE', '', include_non_taxed=True)
        
        order.recalculate_total(save=False)
        price = order.total
        subtotal = order.sub_total
        tax = order.tax
        
        self.assertEqual(subtotal, Decimal('105.00'))
        self.assertEqual(tax, Decimal('20.00'))
        # 100 + 10 shipping + 20 tax
        self.assertEqual(price, Decimal('135.00'))
        
        taxes = order.taxes.all()
        self.assertEqual(2, len(taxes))
        t1 = taxes[0]
        t2 = taxes[1]
        self.assert_('Shipping' in (t1.description, t2.description))
        if t1.description == 'Shipping':
            tship = t1
            tmain = t2
        else:
            tship = t2
            tmain = t1
        self.assertEqual(tmain.tax, Decimal('20.00'))
        self.assertEqual(tship.tax, Decimal('0.00'))
        
        order = make_test_order('CH', '')
        
        order.recalculate_total(save=False)
        price = order.total
        subtotal = order.sub_total
        tax = order.tax
        
        self.assertEqual(subtotal, Decimal('100.00'))
        self.assertEqual(tax, Decimal('16.00'))
        # 100 + 10 shipping + 16 tax
        self.assertEqual(price, Decimal('126.00'))

        taxes = order.taxes.all()
        self.assertEqual(2, len(taxes))
        t1 = taxes[0]
        t2 = taxes[1]
        self.assert_('Shipping' in (t1.description, t2.description))
        if t1.description == 'Shipping':
            tship = t1
            tmain = t2
        else:
            tship = t2
            tmain = t1
        
        self.assertEqual(tmain.tax, Decimal('16.00'))
        self.assertEqual(tship.tax, Decimal('0.00'))
        
    def testDuplicateAdminAreas(self):
        """Test the situation where we have multiple adminareas with the same name"""
        cache_delete()
        tax = config_get('TAX','MODULE')
        tax.update('tax.modules.area')

        order = make_test_order('GB', 'Manchester')

        order.recalculate_total(save=False)
        price = order.total
        subtotal = order.sub_total
        tax = order.tax

        self.assertEqual(subtotal, Decimal('100.00'))
        self.assertEqual(tax, Decimal('20.00'))
        # 100 + 10 shipping + 20 tax
        self.assertEqual(price, Decimal('130.00'))

        taxes = order.taxes.all()
        self.assertEqual(2, len(taxes))
        t1 = taxes[0]
        t2 = taxes[1]
        self.assert_('Shipping' in (t1.description, t2.description))
        if t1.description == 'Shipping':
            tship = t1
            tmain = t2
        else:
            tship = t2
            tmain = t1
        self.assertEqual(tmain.tax, Decimal('20.00'))
        self.assertEqual(tship.tax, Decimal('0.00'))

    def testPercent(self):
        """Test percent tax without shipping"""
        shp = _set_percent_taxer('10')
        order = make_test_order('US', 'TX')
        
        order.recalculate_total(save=False)
        price = order.total
        subtotal = order.sub_total
        tax = order.tax        
        
        self.assertEqual(subtotal, Decimal('100.00'))
        self.assertEqual(tax, Decimal('10.00'))
        # 100 + 10 shipping + 10 tax
        self.assertEqual(price, Decimal('120.00'))
        
        taxes = order.taxes.all()
        self.assertEqual(1, len(taxes))
        self.assertEqual(taxes[0].tax, Decimal('10.00'))
        self.assertEqual(taxes[0].description, r'10%')
        
        
    def testPercentShipping(self):
        """Test percent tax with shipping"""
        shp = _set_percent_taxer('10')
        shp.update(False)

        order = make_test_order('US', 'TX')
        shp.update(True)
        order.recalculate_total(save=False)
        price = order.total
        tax = order.tax
        
        self.assertEqual(tax, Decimal('11.00'))
        # 100 + 10 shipping + 11 tax
        self.assertEqual(price, Decimal('121.00'))
        
        taxes = order.taxes.all()
        self.assertEqual(2, len(taxes))
        t1 = taxes[0]
        t2 = taxes[1]
        self.assert_('Shipping' in (t1.description, t2.description))
        if t1.description == 'Shipping':
            tship = t1
            tmain = t2
        else:
            tship = t2
            tmain = t1
            
        self.assertEqual(tmain.tax, Decimal('10.00'))
        self.assertEqual(tmain.description, r'10%')
        self.assertEqual(tship.tax, Decimal('1.00'))
        self.assertEqual(tship.description, 'Shipping')
        
    def testFractionalPercentShipping(self):
        """Test proper handling of taxes when using a fractional percent tax.  This can cause
        situations where the total is xx.xxxxx, the payment processor charges xx.xx, 
        leaving 00.00xxxx remaining."""
        
        log.debug('fractionalpercent')        
        shp = _set_percent_taxer('12.254')
        log.debug('making order')
        order = make_test_order('US', 'TX')
        order.recalculate_total(save=False)
        price = order.total
        tax = order.tax
        
        self.assertEqual(tax, Decimal('12.254'))
        self.assertEqual(order.balance, Decimal('122.26'))
        
        make_order_payment(order, amount=Decimal('122.26'))
        
        self.assertEqual(order.balance, Decimal("0.00"))
        self.assert_(order.paid_in_full)

        # try with a known bad case - from email
        shp = _set_percent_taxer('12.25')
        order = make_test_order('US', 'TX', price=Decimal('209.90'), quantity=1)
        order.recalculate_total(save=False)
        price = order.total
        tax = order.tax
        
        self.assertEqual(tax, Decimal('25.71275'))
        self.assertEqual(order.total, Decimal('245.61275'))
        self.assertEqual(order.balance, Decimal('245.62'))
        
        make_order_payment(order, amount=Decimal('245.62'))
        
        #self.assertEqual(order.balance, Decimal("0.00"))
        self.assert_(order.paid_in_full)
        