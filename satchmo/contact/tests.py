r"""
>>> import datetime
>>> from satchmo.contact.models import *

# Create a contact

>>> contact1 = Contact.objects.create(first_name="Jim", last_name="Tester", 
... role="Customer", email="Jim@JimWorld.com")
>>> contact1.full_name
u'Jim Tester'
>>> contact1
<Contact: Jim Tester>

# Add a phone number for this person and make sure that it's the default
>>> phone1 = PhoneNumber.objects.create(contact=contact1, type='Home', phone="800-111-9900")
>>> contact1.primary_phone
<PhoneNumber: Home - 800-111-9900>

# Make sure that new primary phones become the default, and that
# non-primary phones don't become the default when a default already exists.
>>> phone2 = PhoneNumber.objects.create(contact=contact1, type='Work', phone="800-222-9901", primary=True)
>>> phone3 = PhoneNumber.objects.create(contact=contact1, type="Mobile", phone="800-333-9902")
>>> contact1.primary_phone
<PhoneNumber: Work - 800-222-9901>

#Add an address & make sure it is default billing and shipping
>>> add1 = AddressBook.objects.create(contact=contact1, description="Home Address",
... street1="56 Cool Lane", city="Niftyville", state="IA", postal_code="12344",
... country="USA")
>>> contact1.billing_address
<AddressBook: Jim Tester - Home Address>
>>> contact1.shipping_address
<AddressBook: Jim Tester - Home Address>
>>> contact1.shipping_address.street1
u'56 Cool Lane'
>>> contact1.shipping_address.street2
u''
>>> contact1.billing_address.street1
u'56 Cool Lane'
>>> contact1.billing_address.street2
u''

#Add a new shipping address
>>> add2 = AddressBook(description="Work Address", street1="56 Industry Way", city="Niftytown", 
... state="IA", postal_code="12366", country="USA", is_default_shipping=True)
>>> add2.contact = contact1
>>> add2.save()
>>> contact1.save()
>>> contact1.billing_address
<AddressBook: Jim Tester - Home Address>
>>> contact1.shipping_address
<AddressBook: Jim Tester - Work Address>


#Need to add some more checks here
"""

import datetime
try:
    from decimal import Decimal
except:
    from django.utils._decimal import Decimal

from django.test import TestCase
from models import *
from satchmo.caching import cache_delete
from satchmo.configuration import config_get
from satchmo.product.models import Product
from satchmo.payment.config import payment_choices

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
    
    p = Product.objects.get(slug='dj-rocks-s-b')
    price = p.unit_price
    item1 = OrderItem(order=o, product=p, quantity=5,
        unit_price=price, line_item_price=price*5)
    item1.save()
    
    if include_non_taxed:
        p = Product.objects.get(slug='neat-book-hard')
        price = p.unit_price
        item2 = OrderItem(order=o, product=p, quantity=1,
            unit_price=price, line_item_price=price)
        item2.save()
    
    return o

class OrderTest(TestCase):
    fixtures = ['products.yaml']    

    def testBalanceMethods(self):
        order = make_test_order('US', '', include_non_taxed=True)
        order.recalculate_total(save=False)
        price = order.total
        subtotal = order.sub_total
    
        self.assertEqual(subtotal, Decimal('105.00'))
        self.assertEqual(price, Decimal('115.00'))
        self.assertEqual(order.balance, price)
    
        paytype = payment_choices()[0][0]
        pmt = OrderPayment(order = order, payment=paytype, amount=Decimal("5.00"))
        pmt.save()
    
        self.assertEqual(order.balance, Decimal("110.00"))
        self.assertEqual(order.balance_paid, Decimal("5.00"))

        self.assert_(order.is_partially_paid)
    
        pmt = OrderPayment(order = order, payment=paytype, amount=Decimal("110.00"))
        pmt.save()
    
        self.assertEqual(order.balance, Decimal("0.00"))
        self.assertEqual(order.is_partially_paid, False)
        self.assert_(order.paid_in_full)

    def testSmallPayment(self):
        order = make_test_order('US', '', include_non_taxed=True)
        order.recalculate_total(save=False)
        price = order.total
        subtotal = order.sub_total
        
        paytype = payment_choices()[0][0]
        pmt = OrderPayment(order = order, payment=paytype, amount=Decimal("0.000001"))
        pmt.save()
    
        self.assert_(order.is_partially_paid)

if __name__ == "__main__":
    import doctest
    doctest.testmod()

