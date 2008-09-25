import datetime
from satchmo.contact.models import *
from satchmo.l10n.models import Country
from satchmo.contact.forms import ContactInfoForm

from django.test import TestCase

US = Country.objects.get(iso2_code__iexact="US")

class ContactTest(TestCase):
    fixtures = ['l10n-data.yaml', 'test-config.yaml']
    
    def test_base_contact(self):
        """Test creating a contact"""

        contact1 = Contact.objects.create(first_name="Jim", last_name="Tester", 
            role="Customer", email="Jim@JimWorld.com")
            
        self.assertEqual(contact1.full_name, u'Jim Tester')

        # Add a phone number for this person and make sure that it's the default
        phone1 = PhoneNumber.objects.create(contact=contact1, type='Home', phone="800-111-9900")
        self.assert_(contact1.primary_phone)
        self.assertEqual(contact1.primary_phone.phone, '800-111-9900')
        self.assertEqual(phone1.type, 'Home') 

        # Make sure that new primary phones become the default, and that
        # non-primary phones don't become the default when a default already exists.
        phone2 = PhoneNumber.objects.create(contact=contact1, type='Work', phone="800-222-9901", primary=True)
        phone3 = PhoneNumber.objects.create(contact=contact1, type="Mobile", phone="800-333-9902")
        self.assertEqual(contact1.primary_phone, phone2)

        #Add an address & make sure it is default billing and shipping
        add1 = AddressBook.objects.create(contact=contact1, description="Home Address",
            street1="56 Cool Lane", city="Niftyville", state="IA", postal_code="12344",
            country=US)
        self.assert_(contact1.billing_address)
        self.assertEqual(contact1.billing_address, add1)
        self.assertEqual(contact1.billing_address.description, "Home Address")
        self.assertEqual(add1.street1, "56 Cool Lane")

        self.assertEqual(contact1.billing_address, contact1.shipping_address)
        self.assertEqual(contact1.billing_address.street1, "56 Cool Lane")

        #Add a new shipping address
        add2 = AddressBook(description="Work Address", street1="56 Industry Way", city="Niftytown", 
            state="IA", postal_code="12366", country=US, is_default_shipping=True)
        add2.contact = contact1
        add2.save()
        contact1.save()
        self.assertNotEqual(contact1.billing_address, contact1.shipping_address)
        self.assertEqual(contact1.billing_address.description, "Home Address")
        self.assertEqual(contact1.shipping_address.description, "Work Address")
        
class ContactInfoFormTest(TestCase):
    fixtures = ['l10n-data.yaml', 'test_shop.yaml', 'test-config.yaml']
    
    def test_missing_first_and_last_name_should_not_raise_exception(self):
        form = ContactInfoForm(None, None, None, {'phone':'800-111-9900'})
        self.assertEqual(False, form.is_valid())
        
