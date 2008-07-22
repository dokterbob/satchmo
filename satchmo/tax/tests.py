import datetime
try:
    from decimal import Decimal
except:
    from django.utils._decimal import Decimal

from django.test import TestCase
from models import *
from satchmo.contact.models import AddressBook, Contact, Order, OrderItem
from satchmo.product.models import Product
from satchmo.configuration import config_get
from satchmo.caching import cache_delete

def make_test_order(country, state, include_non_taxed=False):
    c = Contact(first_name="Tax", last_name="Tester", 
        role="Customer", email="tax@example.com")
    c.save()
    ad = AddressBook(contact=c, description="home",
        street1 = "test", state=state, city="Portland",
        country = country, is_default_shipping=True,
        is_default_billing=True)
    ad.save()
    o = Order(contact=c, shipping_cost=Decimal('10.00'))
    o.save()
    
    p = Product.objects.get(slug='DJ-Rocks_S_B')
    price = p.unit_price
    item1 = OrderItem(order=o, product=p, quantity=5,
        unit_price=price, line_item_price=price*5)
    item1.save()
    
    if include_non_taxed:
        p = Product.objects.get(slug='neat-book_hard')
        price = p.unit_price
        item2 = OrderItem(order=o, product=p, quantity=1,
            unit_price=price, line_item_price=price)
        item2.save()
    
    return o

class TaxTest(TestCase):
    
    fixtures = ['l10n_data.xml', 'test_tax.yaml', 'test_discount.yaml']
            
    def testAreaCountries(self):
        """Test Area tax module"""
        cache_delete()
        tax = config_get('TAX','MODULE')
        tax.update('satchmo.tax.modules.area')
        
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
        tax.update('satchmo.tax.modules.area')

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
        cache_delete()
        tax = config_get('TAX','MODULE')
        tax.update('satchmo.tax.modules.percent')
        pcnt = config_get('TAX', 'PERCENT')
        pcnt.update('10')
        shp = config_get('TAX', 'TAX_SHIPPING')
        shp.update(False)
        
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
        cache_delete()
        tax = config_get('TAX','MODULE')
        tax.update('satchmo.tax.modules.percent')
        pcnt = config_get('TAX', 'PERCENT')
        pcnt.update('10')
        shp = config_get('TAX', 'TAX_SHIPPING')
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
        
        
        