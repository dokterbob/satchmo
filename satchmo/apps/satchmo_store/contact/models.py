"""
Stores customer, organization, and order information.
"""
from django.conf import settings
from django.contrib.auth.models import User
from django.core import urlresolvers
from django.db import models
from django.utils.translation import ugettext, ugettext_lazy as _
from livesettings import config_get_group
from l10n.models import Country
from satchmo_store.contact import CUSTOMER_ID
import datetime
import logging
import sys

log = logging.getLogger('contact.models')

CONTACT_CHOICES = (
    ('Customer', _('Customer')),
    ('Supplier', _('Supplier')),
    ('Distributor', _('Distributor')),
)

ORGANIZATION_CHOICES = (
    ('Company', _('Company')),
    ('Government', _('Government')),
    ('Non-profit', _('Non-profit')),
)

ORGANIZATION_ROLE_CHOICES = (
    ('Supplier', _('Supplier')),
    ('Distributor', _('Distributor')),
    ('Manufacturer', _('Manufacturer')),
    ('Customer', _('Customer')),
)

class OrganizationManager(models.Manager):
    def by_name(self, name, create=False, role='Customer', orgtype='Company'):        
        org = None
        orgs = self.filter(name=name, role=role, type=orgtype)
        if orgs.count() > 0:
            org = orgs[0]
            
        if not org:
            if not create:
                raise Organization.DoesNotExist()
            else:
                log.debug('Creating organization: %s', name)
                org = Organization(name=name, role=role, type=orgtype)
                org.save()
        
        return org

class Organization(models.Model):
    """
    An organization can be a company, government or any kind of group.
    """
    name = models.CharField(_("Name"), max_length=50, )
    type = models.CharField(_("Type"), max_length=30,
        choices=ORGANIZATION_CHOICES)
    role = models.CharField(_("Role"), max_length=30,
        choices=ORGANIZATION_ROLE_CHOICES)
    create_date = models.DateField(_("Creation Date"))
    notes = models.TextField(_("Notes"), max_length=200, blank=True, null=True)

    objects = OrganizationManager()
    
    def __unicode__(self):
        return self.name

    def save(self, force_insert=False, force_update=False):
        """Ensure we have a create_date before saving the first time."""
        if not self.pk:
            self.create_date = datetime.date.today()
        super(Organization, self).save(force_insert=force_insert, force_update=force_update)

    class Meta:
        verbose_name = _("Organization")
        verbose_name_plural = _("Organizations")

class ContactManager(models.Manager):

    def from_request(self, request, create=False):
        """Get the contact from the session, else look up using the logged-in
        user. Create an unsaved new contact if `create` is true.

        Returns:
        - Contact object or None
        """
        contact = None
        if request.session.get(CUSTOMER_ID):
            try:
                contact = Contact.objects.get(id=request.session[CUSTOMER_ID])
            except Contact.DoesNotExist:
                del request.session[CUSTOMER_ID]
            
        if contact is None and request.user.is_authenticated():
            try:
                contact = Contact.objects.get(user=request.user.id)
                request.session[CUSTOMER_ID] = contact.id
            except Contact.DoesNotExist:
                pass
        else:
            # Don't create a Contact if the user isn't authenticated.
            create = False

        if contact is None:
            if create:
                contact = Contact(user=request.user)

            else:
                raise Contact.DoesNotExist()

        return contact


class Contact(models.Model):
    """
    A customer, supplier or any individual that a store owner might interact
    with.
    """
    title = models.CharField(_("Title"), max_length=30, blank=True, null=True)
    first_name = models.CharField(_("First name"), max_length=30, )
    last_name = models.CharField(_("Last name"), max_length=30, )
    user = models.ForeignKey(User, blank=True, null=True, unique=True)
    role = models.CharField(_("Role"), max_length=20, blank=True, null=True,
        choices=CONTACT_CHOICES)
    organization = models.ForeignKey(Organization, verbose_name=_("Organization"), blank=True, null=True)
    dob = models.DateField(_("Date of birth"), blank=True, null=True)
    email = models.EmailField(_("Email"), blank=True, max_length=75)
    notes = models.TextField(_("Notes"), max_length=500, blank=True)
    create_date = models.DateField(_("Creation date"))

    objects = ContactManager()

    def _get_full_name(self):
        """Return the person's full name."""
        return u'%s %s' % (self.first_name, self.last_name)
    full_name = property(_get_full_name)

    def _shipping_address(self):
        """Return the default shipping address or None."""
        try:
            return self.addressbook_set.get(is_default_shipping=True)
        except AddressBook.DoesNotExist:
            return None
    shipping_address = property(_shipping_address)

    def _billing_address(self):
        """Return the default billing address or None."""
        try:
            return self.addressbook_set.get(is_default_billing=True)
        except AddressBook.DoesNotExist:
            return None
    billing_address = property(_billing_address)

    def _primary_phone(self):
        """Return the default phone number or None."""
        try:
            return self.phonenumber_set.get(primary=True)
        except PhoneNumber.DoesNotExist:
            return None
    primary_phone = property(_primary_phone)

    def __unicode__(self):
        return self.full_name

    def save(self, force_insert=False, force_update=False):
        """Ensure we have a create_date before saving the first time."""
        if not self.pk:
            self.create_date = datetime.date.today()
        # Validate contact to user sync
        if self.user:
            dirty = False
            user = self.user
            if user.email != self.email:
                user.email = self.email
                dirty = True
            
            if user.first_name != self.first_name:
                user.first_name = self.first_name
                dirty = True

            if user.last_name != self.last_name:
                user.last_name = self.last_name
                dirty = True
                
            if dirty:
                self.user = user
                self.user.save()

        super(Contact, self).save(force_insert=force_insert, force_update=force_update)

    class Meta:
        verbose_name = _("Contact")
        verbose_name_plural = _("Contacts")        

PHONE_CHOICES = (
    ('Work', _('Work')),
    ('Home', _('Home')),
    ('Fax', _('Fax')),
    ('Mobile', _('Mobile')),
)

INTERACTION_CHOICES = (
    ('Email', _('Email')),
    ('Phone', _('Phone')),
    ('In Person', _('In Person')),
)

class Interaction(models.Model):
    """
    A type of activity with the customer.  Useful to track emails, phone calls,
    or in-person interactions.
    """
    contact = models.ForeignKey(Contact, verbose_name=_("Contact"))
    type = models.CharField(_("Type"), max_length=30,choices=INTERACTION_CHOICES)
    date_time = models.DateTimeField(_("Date and Time"), )
    description = models.TextField(_("Description"), max_length=200)

    def __unicode__(self):
        return u'%s - %s' % (self.contact.full_name, self.type)

    class Meta:
        verbose_name = _("Interaction")
        verbose_name_plural = _("Interactions")

class PhoneNumber(models.Model):
    """
    Phone number associated with a contact.
    """
    contact = models.ForeignKey(Contact)
    type = models.CharField(_("Description"), choices=PHONE_CHOICES,
        max_length=20, blank=True)
    phone = models.CharField(_("Phone Number"), blank=True, max_length=30,
        )
    primary = models.BooleanField(_("Primary"), default=False)

    def __unicode__(self):
        return u'%s - %s' % (self.type, self.phone)

    def save(self, force_insert=False, force_update=False):
        """
        If this number is the default, then make sure that it is the only
        primary phone number. If there is no existing default, then make
        this number the default.
        """
        existing_number = self.contact.primary_phone
        if existing_number:
            if self.primary:
                existing_number.primary = False
                super(PhoneNumber, existing_number).save()
        else:
            self.primary = True
        super(PhoneNumber, self).save(force_insert=force_insert, force_update=force_update)

    class Meta:
        ordering = ['-primary']
        verbose_name = _("Phone Number")
        verbose_name_plural = _("Phone Numbers")

class AddressBook(models.Model):
    """
    Address information associated with a contact.
    """
    contact = models.ForeignKey(Contact)
    description = models.CharField(_("Description"), max_length=20, blank=True,
        help_text=_('Description of address - Home, Office, Warehouse, etc.',))
    addressee = models.CharField(_("Addressee"), max_length=80)
    street1 = models.CharField(_("Street"), max_length=80)
    street2 = models.CharField(_("Street"), max_length=80, blank=True)
    state = models.CharField(_("State"), max_length=50, blank=True)
    city = models.CharField(_("City"), max_length=50)
    postal_code = models.CharField(_("Zip Code"), max_length=30)
    country = models.ForeignKey(Country, verbose_name=_("Country"))
    is_default_shipping = models.BooleanField(_("Default Shipping Address"),
        default=False)
    is_default_billing = models.BooleanField(_("Default Billing Address"),
        default=False)

    def __unicode__(self):
       return u'%s - %s' % (self.contact.full_name, self.description)

    def save(self, force_insert=False, force_update=False):
        """
        If this address is the default billing or shipping address, then
        remove the old address's default status. If there is no existing
        default, then make this address the default.
        """
        existing_billing = self.contact.billing_address
        if existing_billing:
            if self.is_default_billing:
                existing_billing.is_default_billing = False
                super(AddressBook, existing_billing).save()
        else:
            self.is_default_billing = True

        existing_shipping = self.contact.shipping_address
        if existing_shipping:
            if self.is_default_shipping:
                existing_shipping.is_default_shipping = False
                super(AddressBook, existing_shipping).save()
        else:
            self.is_default_shipping = True

        super(AddressBook, self).save(force_insert=force_insert, force_update=force_update)

    class Meta:
        verbose_name = _("Address Book")
        verbose_name_plural = _("Address Books")

import config