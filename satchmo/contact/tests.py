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

if __name__ == "__main__":
    import doctest
    doctest.testmod()
