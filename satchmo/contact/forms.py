from django import newforms as forms
from django.dispatch import dispatcher
from django.utils.translation import ugettext_lazy as _, ugettext
from satchmo.configuration import config_value, config_get_group, SettingNotSet
from satchmo.contact.models import Contact, AddressBook, PhoneNumber
from satchmo.l10n.models import Country
from satchmo.shop.models import Config
from django.contrib.auth.models import User
from signals import satchmo_contact_location_changed
import datetime

selection = ''

class ContactInfoForm(forms.Form):
    email = forms.EmailField(max_length=75)
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    phone = forms.CharField(max_length=30)
    street1 = forms.CharField(max_length=30)
    street2 = forms.CharField(max_length=30, required=False)
    city = forms.CharField(max_length=30)
    state = forms.CharField(max_length=30, required=False)
    country = forms.CharField(max_length=30, required=False)
    postal_code = forms.CharField(max_length=10)
    copy_address = forms.BooleanField(required=False)
    ship_street1 = forms.CharField(max_length=30, required=False)
    ship_street2 = forms.CharField(max_length=30, required=False)
    ship_city = forms.CharField(max_length=30, required=False)
    ship_state = forms.CharField(max_length=30, required=False)
    ship_postal_code = forms.CharField(max_length=10, required=False)
    ship_country = forms.CharField(max_length=30, required=False)

    def __init__(self, countries, areas, contact, *args, **kwargs):
        self.shippable = True
        if kwargs.has_key('shippable'):
            self.shippable = kwargs['shippable']
            del(kwargs['shippable'])
        super(ContactInfoForm, self).__init__(*args, **kwargs)    
        if areas is not None and countries is None:
            self.fields['state'] = forms.ChoiceField(choices=areas, initial=selection)
            self.fields['ship_state'] = forms.ChoiceField(choices=areas, initial=selection, required=False)
        if countries is not None:
            self.fields['country'] = forms.ChoiceField(choices=countries)
            if self.shippable:
                self.fields['ship_country'] = forms.ChoiceField(choices=countries, required=False)

        shop_config = Config.get_shop_config()
        self._local_only = shop_config.in_country_only
        country = shop_config.sales_country
        if not country:
            self._default_country = 'US'
        else:
            self._default_country = country.iso2_code        
        self.contact = contact

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
        
    def clean_state(self):
        data = self.cleaned_data['state']
        if self._local_only:
            country_iso2 = self._default_country
        else:
            if not 'country' in self.data:
                # The user didn't even submit a country, but this error will
                # be handled by the clean_country function
                return data
            country_iso2 = self.data['country']
        country = Country.objects.get(iso2_code=country_iso2)
        if country.adminarea_set.filter(active=True).count() > 0:
            if not data or data == selection:
                raise forms.ValidationError(
                    self._local_only and _('This field is required.') \
                               or _('State is required for your country.'))
        return data

    def clean_ship_state(self):
        data = self.cleaned_data['ship_state']
        if self.cleaned_data['copy_address']:
            if 'state' in self.cleaned_data:
                self.cleaned_data['ship_state'] = self.cleaned_data['state']
            return self.cleaned_data['ship_state']

        if self._local_only:
            country_iso2 = self._default_country
        else:
            if not 'ship_country' in self.data:
                # This user didn't even submit a country, but this error will
                # be handled by the clean_ship_country function
                return data
            country_iso2 = self.data['ship_country']

        country = Country.objects.get(iso2_code=country_iso2)
        if country.adminarea_set.filter(active=True).count() > 0:
            if not data or data == selection:
                raise forms.ValidationError(
                    self._local_only and _('This field is required.') \
                               or _('State is required for your country.'))
        return data

    def clean_country(self):
        if self._local_only:
            return self._default_country
        else:
            if not self.cleaned_data['country']:
                raise forms.ValidationError(_('This field is required.'))
        return self.cleaned_data['country']
        
    def clean_ship_country(self):
        copy_address = self.cleaned_data['copy_address']
        if copy_address:
            return self.cleaned_data['country']
        if self._local_only:
            return self._default_country
        if not self.shippable:
            return self.cleaned_data['country']
        shipcountry = self.cleaned_data['ship_country']
        if not shipcountry:
            raise forms.ValidationError(_('This field is required.'))
        if config_value('PAYMENT', 'COUNTRY_MATCH'):
            country = self.cleaned_data['country']
            if shipcountry != country:
                raise forms.ValidationError(_('Shipping and Billing countries must match'))
        return shipcountry

    def ship_charfield_clean(self, field_name):
        if self.cleaned_data['copy_address']:
            if field_name in self.cleaned_data:
                self.cleaned_data['ship_' + field_name] = self.cleaned_data[field_name]
            return self.cleaned_data['ship_' + field_name]
        field = forms.CharField(max_length=30)
        return field.clean(self.cleaned_data['ship_' + field_name])

    def clean_ship_street1(self):
        return self.ship_charfield_clean('street1')

    def clean_ship_street2(self):
        if self.cleaned_data['copy_address']:
            if 'street2' in self.cleaned_data:
                self.cleaned_data['ship_street2'] = self.cleaned_data['street2']
        return self.cleaned_data['ship_street2']

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

        data = self.cleaned_data

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
            dispatcher.send(signal=satchmo_contact_location_changed, contact=contact)
        
        return customer.id

class DateTextInput(forms.TextInput):
    def render(self, name, value, attrs=None):
        if isinstance(value, datetime.date):
            value = value.strftime("%m.%d.%Y")
        return super(DateTextInput, self).render(name, value, attrs)

class ExtendedContactInfoForm(ContactInfoForm):
    """Contact form which includes birthday and newsletter."""
    dob = forms.DateField(required=False)
    newsletter = forms.BooleanField(label=_('Newsletter'), widget=forms.CheckboxInput(), required=False)
