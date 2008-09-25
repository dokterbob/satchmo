from django import forms
from django.utils.translation import ugettext_lazy as _, ugettext
from satchmo.configuration import config_value, config_get_group, SettingNotSet, SHOP_GROUP
from satchmo.contact.models import Contact, AddressBook, PhoneNumber
from satchmo.l10n.models import Country
from satchmo.shop.models import Config
from django.contrib.auth.models import User
import signals
import datetime
import logging

log = logging.getLogger('satchmo.contact.forms')

selection = ''

class ContactInfoForm(forms.Form):
    email = forms.EmailField(max_length=75, label=_('Email'))
    first_name = forms.CharField(max_length=30, label=_('First Name'))
    last_name = forms.CharField(max_length=30, label=_('Last Name'))
    phone = forms.CharField(max_length=30, label=_('Phone'))
    addressee = forms.CharField(max_length=61, required=False, label=_('Addressee'))
    street1 = forms.CharField(max_length=30, label=_('Street'))
    street2 = forms.CharField(max_length=30, required=False)
    city = forms.CharField(max_length=30, label=_('City'))
    state = forms.CharField(max_length=30, required=False, label=_('State'))
    country = forms.ModelChoiceField(Country.objects.all(), required=False, label=_('Country'))
    postal_code = forms.CharField(max_length=10, label=_('Zipcode/Postcode'))
    copy_address = forms.BooleanField(required=False, label=_('Shipping same as billing?'))
    ship_addressee = forms.CharField(max_length=61, required=False, label=_('Addressee'))
    ship_street1 = forms.CharField(max_length=30, required=False, label=_('Street'))
    ship_street2 = forms.CharField(max_length=30, required=False)
    ship_city = forms.CharField(max_length=30, required=False, label=_('City'))
    ship_state = forms.CharField(max_length=30, required=False, label=_('State'))
    ship_postal_code = forms.CharField(max_length=10, required=False, label=_('Zipcode/Postcode'))
    ship_country = forms.ModelChoiceField(Country.objects.all(), required=False, label=_('Country'))

    def __init__(self, countries, areas, contact, *args, **kwargs):
        self.shippable = True
        if kwargs.has_key('shippable'):
            self.shippable = kwargs['shippable']
            del(kwargs['shippable'])
        self._billing_data_optional = config_value(SHOP_GROUP, 'BILLING_DATA_OPTIONAL'),
        super(ContactInfoForm, self).__init__(*args, **kwargs)   
        if areas is not None and countries is None:
            log.debug('populating admin areas')
            areas = [(area.abbrev or area.name, area.name) for area in areas]
            self.fields['state'] = forms.ChoiceField(choices=areas, initial=selection)
            self.fields['ship_state'] = forms.ChoiceField(choices=areas, initial=selection, required=False)
        if countries is not None:
            self.fields['country'] = forms.ModelChoiceField(countries)
            if self.shippable:
                self.fields['ship_country'] = forms.ModelChoiceField(countries)

        shop_config = Config.objects.get_current()
        self._local_only = shop_config.in_country_only
        # country = shop_config.sales_country
        # if not country:
        #     self._default_country = Country.objects.get(iso2_code__iequals='US')
        # else:
        #     self._default_country = country
        country = shop_config.sales_country
        self._default_country = country.pk
        self.fields['country'].initial = country.pk
        self.fields['ship_country'].initial = country.pk
        self.contact = contact
        if self._billing_data_optional:
            for fname in ('phone', 'street1', 'street2', 'city', 'state', 'country', 'postal_code'):
                self.fields[fname].required = False
                
        # slap a star on the required fields
        for f in self.fields:
            fld = self.fields[f]
            if fld.required:
                fld.label = (fld.label or f) + '*'

    def clean_email(self):
        """Prevent account hijacking by disallowing duplicate emails."""
        email = self.cleaned_data.get('email', None)
        if self.contact:
            if self.contact.email and self.contact.email == email:
                return email
            users_with_email = Contact.objects.filter(email=email)
            if len(users_with_email) == 0:
                return email
            if len(users_with_email) > 1 or users_with_email[0].id != self.contact.id:
                raise forms.ValidationError(
                    ugettext("That email address is already in use."))
        return email
        
    def clean_postal_code(self):
        return self.validate_postcode_by_country(self.cleaned_data.get('postal_code'))
    
    def clean_ship_postal_code(self):
        code = self.ship_charfield_clean('postal_code')
        return self.validate_postcode_by_country(code)
        
    def clean_state(self):
        data = self.cleaned_data.get('state')
        if self._local_only:
            country_pk = self._default_country
        else:
            if not 'country' in self.data:
                # The user didn't even submit a country, but this error will
                # be handled by the clean_country function
                return data
            country_pk = self.data['country']
        country = Country.objects.get(pk=country_pk)
        if country.adminarea_set.filter(active=True).count() > 0 and not self._billing_data_optional:
            if not data or data == selection:
                raise forms.ValidationError(
                    self._local_only and _('This field is required.') \
                               or _('State is required for your country.'))
        return data

    def clean_ship_state(self):
        data = self.cleaned_data.get('ship_state')
        if self.cleaned_data.get('copy_address'):
            if 'state' in self.cleaned_data:
                self.cleaned_data['ship_state'] = self.cleaned_data['state']
            return self.cleaned_data['ship_state']

        if self._local_only:
            country_pk = self._default_country
        else:
            if not 'ship_country' in self.data:
                # This user didn't even submit a country, but this error will
                # be handled by the clean_ship_country function
                return data
            country_pk = self.data['ship_country']
        country = Country.objects.get(pk=country_pk)
        if country.adminarea_set.filter(active=True).count() > 0:
            if not data or data == selection:
                raise forms.ValidationError(
                    self._local_only and _('This field is required.') \
                               or _('State is required for your country.'))
        return data

    def clean_addressee(self):
        if not self.cleaned_data.get('addressee'):
            first_and_last = u' '.join((self.cleaned_data.get('first_name', ''),
                                       self.cleaned_data.get('last_name', '')))
            return first_and_last
        else:
            return self.cleaned_data['addressee']
    
    def clean_ship_addressee(self):
        if not self.cleaned_data.get('ship_addressee') and \
                not self.cleaned_data.get('copy_address'):
            first_and_last = u' '.join((self.cleaned_data.get('first_name', ''),
                                       self.cleaned_data.get('last_name', '')))
            return first_and_last
        else:
            return self.cleaned_data['ship_addressee']
    
    def clean_country(self):
        if self._local_only:
            return self._default_country
        else:
            if not self.cleaned_data.get('country'):
                raise forms.ValidationError(_('This field is required.'))
        return self.cleaned_data['country']
        
    def clean_ship_country(self):
        copy_address = self.cleaned_data.get('copy_address')
        if copy_address:
            return self.cleaned_data['country']
        if self._local_only:
            return self._default_country
        if not self.shippable:
            return self.cleaned_data['country']
        shipcountry = self.cleaned_data.get('ship_country')
        if not shipcountry:
            raise forms.ValidationError(_('This field is required.'))
        if config_value('PAYMENT', 'COUNTRY_MATCH'):
            country = self.cleaned_data.get('country')
            if shipcountry != country:
                raise forms.ValidationError(_('Shipping and Billing countries must match'))
        return shipcountry

    def ship_charfield_clean(self, field_name):
        if self.cleaned_data.get('copy_address'):
            if field_name in self.cleaned_data:
                self.cleaned_data['ship_' + field_name] = self.cleaned_data[field_name]
            return self.cleaned_data['ship_' + field_name]
        field = forms.CharField(max_length=30)
        return field.clean(self.cleaned_data['ship_' + field_name])

    def clean_ship_street1(self):
        return self.ship_charfield_clean('street1')

    def clean_ship_street2(self):
        if self.cleaned_data.get('copy_address'):
            if 'street2' in self.cleaned_data:
                self.cleaned_data['ship_street2'] = self.cleaned_data.get('street2')
        return self.cleaned_data.get('ship_street2')

    def clean_ship_city(self):
        return self.ship_charfield_clean('city')

    def clean_ship_postal_code(self):
        return self.ship_charfield_clean('postal_code')

    def save(self, contact=None, update_newsletter=True):
        """Save the contact info into the database.
        Checks to see if contact exists. If not, creates a contact
        and copies in the address and phone number."""

        if not contact:
            customer = Contact()
        else:
            customer = contact

        data = self.cleaned_data.copy()

        country = data['country']
        if not isinstance(country, Country):
            country = Country.objects.get(pk=country)
            data['country'] = country
        data['country_id'] = country.id

        shipcountry = data['ship_country']
        if not isinstance(shipcountry, Country):
            shipcountry = Country.objects.get(pk=shipcountry)
            data['ship_country'] = shipcountry
        
        data['ship_country_id'] = shipcountry.id
        
        for field in customer.__dict__.keys():
            try:
                setattr(customer, field, data[field])
            except KeyError:
                pass

        if update_newsletter and config_get_group('NEWSLETTER'):
            from satchmo.newsletter import update_subscription
            if 'newsletter' not in data:
                subscribed = False
            else:
                subscribed = data['newsletter']
            
            update_subscription(contact, subscribed)

        if not customer.role:
            customer.role = "Customer"

        customer.save()
        
        # we need to make sure we don't blindly add new addresses
        # this isn't ideal, but until we have a way to manage addresses
        # this will force just the two addresses, shipping and billing
        # TODO: add address management like Amazon.
        
        bill_address = customer.billing_address
        if not bill_address:
            bill_address = AddressBook(contact=customer)
                
        changed_location = False
        address_keys = bill_address.__dict__.keys()
        for field in address_keys:
            if (not changed_location) and field in ('state', 'country', 'city'):
                if getattr(bill_address, field) != data[field]:
                    changed_location = True
            try:
                setattr(bill_address, field, data[field])
            except KeyError:
                pass

        bill_address.is_default_billing = True
        
        copy_address = data['copy_address']

        ship_address = customer.shipping_address
        
        if copy_address:
            # make sure we don't have any other default shipping address
            if ship_address and ship_address.id != bill_address.id:
                ship_address.delete()
            bill_address.is_default_shipping = True

        bill_address.save()
        
        if not copy_address:
            if not ship_address or ship_address.id == bill_address.id:
                ship_address = AddressBook()
            
            for field in address_keys:
                if (not changed_location) and field in ('state', 'country', 'city'):
                    if getattr(ship_address, field) != data[field]:
                        changed_location = True
                try:
                    setattr(ship_address, field, data['ship_' + field])
                except KeyError:
                    pass
            ship_address.is_default_shipping = True
            ship_address.is_default_billing = False
            ship_address.contact = customer
            ship_address.save()
            
        if not customer.primary_phone:
            phone = PhoneNumber()
            phone.primary = True
        else:
            phone = customer.primary_phone
        phone.phone = data['phone']
        phone.contact = customer
        phone.save()
        
        if changed_location:
            signals.satchmo_contact_location_changed.send(self, contact=contact)
        
        return customer.id
        
    def validate_postcode_by_country(self, postcode):
        country = None
        
        if self._local_only:
            shop_config = Config.objects.get_current()
            country = shop_config.sales_country
        else:
            country = self.cleaned_data.get('country')
                
        responses = signals.validate_postcode.send(self, postcode=postcode, country=country)
        # allow responders to reformat the code, but if they don't return
        # anything, then just use the existing code
        for responder, response in responses:
            if response:
                return response
                
        return postcode

class DateTextInput(forms.TextInput):
    def render(self, name, value, attrs=None):
        if isinstance(value, datetime.date):
            value = value.strftime("%m.%d.%Y")
        return super(DateTextInput, self).render(name, value, attrs)

class ExtendedContactInfoForm(ContactInfoForm):
    """Contact form which includes birthday and newsletter."""
    dob = forms.DateField(required=False)
    newsletter = forms.BooleanField(label=_('Newsletter'), widget=forms.CheckboxInput(), required=False)
