from django import forms
from django.contrib.auth.models import User
from django.db.models import Q
from django.forms.extras.widgets import SelectDateWidget
from django.utils.translation import ugettext_lazy as _, ugettext
from l10n.models import Country
from livesettings import config_value, config_get_group, SettingNotSet
from satchmo_store.contact.models import Contact, AddressBook, PhoneNumber, Organization
from satchmo_store.shop.models import Config
import datetime
import logging
import signals

log = logging.getLogger('satchmo_store.contact.forms')

selection = ''

class ContactInfoForm(forms.Form):
    email = forms.EmailField(max_length=75, label=_('Email'))
    title = forms.CharField(max_length=30, label=_('Title'), required=False)
    first_name = forms.CharField(max_length=30, label=_('First Name'))
    last_name = forms.CharField(max_length=30, label=_('Last Name'))
    phone = forms.CharField(max_length=30, label=_('Phone'))
    addressee = forms.CharField(max_length=61, required=False, label=_('Addressee'))
    company = forms.CharField(max_length=50, required=False, label=_('Company'))
    street1 = forms.CharField(max_length=30, label=_('Street'))
    street2 = forms.CharField(max_length=30, required=False)
    city = forms.CharField(max_length=30, label=_('City'))
    state = forms.CharField(max_length=30, required=False, label=_('State'))
    postal_code = forms.CharField(max_length=10, label=_('ZIP code/Postcode'))
    copy_address = forms.BooleanField(required=False, label=_('Shipping same as billing?'))
    ship_addressee = forms.CharField(max_length=61, required=False, label=_('Addressee'))
    ship_street1 = forms.CharField(max_length=30, required=False, label=_('Street'))
    ship_street2 = forms.CharField(max_length=30, required=False)
    ship_city = forms.CharField(max_length=30, required=False, label=_('City'))
    ship_state = forms.CharField(max_length=30, required=False, label=_('State'))
    ship_postal_code = forms.CharField(max_length=10, required=False, label=_('ZIP code/Postcode'))
    next = forms.CharField(max_length=40, required=False, widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        
        if kwargs:
            data = kwargs.copy()
        else:
            data = {}

        shop = data.pop('shop', None)
        contact = data.pop('contact', None)
        self.shippable = data.pop('shippable', True)
        
        if not shop:
            shop = Config.objects.get_current()            

        super(ContactInfoForm, self).__init__(*args, **data)   

        self._billing_data_optional = config_value('SHOP', 'BILLING_DATA_OPTIONAL')
        
        self._local_only = shop.in_country_only
        areas = shop.areas()
        if shop.in_country_only and areas and areas.count()>0:
            areas = [(area.abbrev or area.name, area.name) for area in areas]
            areas.insert(0,(_("---Please Select---"),_("---Please Select---")))
            billing_state = (contact and getattr(contact.billing_address, 'state', None)) or selection
            shipping_state = (contact and getattr(contact.shipping_address, 'state', None)) or selection
            if config_value('SHOP','ENFORCE_STATE'):
                self.fields['state'] = forms.ChoiceField(choices=areas, initial=billing_state, label=_('State'))
                self.fields['ship_state'] = forms.ChoiceField(choices=areas, initial=shipping_state, required=False, label=_('State'))
        
        self._default_country = shop.sales_country
        billing_country = (contact and getattr(contact.billing_address, 'country', None)) or self._default_country
        shipping_country = (contact and getattr(contact.shipping_address, 'country', None)) or self._default_country
        self.fields['country'] = forms.ModelChoiceField(shop.countries(), required=False, label=_('Country'), empty_label=None, initial=billing_country.pk)
        self.fields['ship_country'] = forms.ModelChoiceField(shop.countries(), required=False, label=_('Country'), empty_label=None, initial=shipping_country.pk)
        
        self.contact = contact
        if self._billing_data_optional:
            for fname in ('phone', 'street1', 'street2', 'city', 'state', 'country', 'postal_code', 'title'):
                self.fields[fname].required = False
                
        # slap a star on the required fields
        for f in self.fields:
            fld = self.fields[f]
            if fld.required:
                fld.label = (fld.label or f) + '*'

    def _check_state(self, data, country):
        if country and config_value('SHOP','ENFORCE_STATE') and country.adminarea_set.filter(active=True).count() > 0:
            if not data or data == selection:
                raise forms.ValidationError(
                    self._local_only and _('This field is required.') \
                               or _('State is required for your country.'))
            if (country.adminarea_set
                    .filter(active=True)
                    .filter(Q(name=data)
                        |Q(abbrev=data)
                        |Q(name=data.capitalize())
                        |Q(abbrev=data.upper())).count() != 1):
                raise forms.ValidationError(_('Invalid state or province.'))
        
                
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
        postcode = self.cleaned_data.get('postal_code')
        country = None
        
        if self._local_only:
            shop_config = Config.objects.get_current()
            country = shop_config.sales_country
        else:
            country = self.fields['country'].clean(self.data.get('country'))

        if not country:
            # Either the store is misconfigured, or the country was
            # not supplied, so the country validation will fail and
            # we can defer the postcode validation until that's fixed.
            return postcode
        
        return self.validate_postcode_by_country(postcode, country)
    
    def clean_state(self):
        data = self.cleaned_data.get('state')
        if self._local_only:
            country = self._default_country
        else:
            country = self.fields['country'].clean(self.data.get('country'))
            if country == None:
                raise forms.ValidationError(_('This field is required.'))
        self._check_state(data, country)
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
                log.error("No country! Got '%s'" % self.cleaned_data.get('country'))
                raise forms.ValidationError(_('This field is required.'))
        return self.cleaned_data['country']
        
    def clean_ship_country(self):
        copy_address = self.fields['copy_address'].clean(self.data.get('copy_address'))
        if copy_address:
            return self.cleaned_data.get('country')
        if self._local_only:
            return self._default_country
        if not self.shippable:
            return self.cleaned_data.get['country']
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
            self.cleaned_data['ship_' + field_name] = self.fields[field_name].clean(self.data.get(field_name))
            return self.cleaned_data['ship_' + field_name]
        return self.fields['ship_' + field_name].clean(self.data.get('ship_' + field_name))

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
        code = self.ship_charfield_clean('postal_code')

        country = None
        
        if self._local_only:
            shop_config = Config.objects.get_current()
            country = shop_config.sales_country
        else:
            country = self.ship_charfield_clean('country')
        
        if not country:
            # Either the store is misconfigured, or the country was
            # not supplied, so the country validation will fail and
            # we can defer the postcode validation until that's fixed.
            return code
        
        return self.validate_postcode_by_country(code, country)
        
    def clean_ship_state(self):
        data = self.cleaned_data.get('ship_state')
        
        if self.cleaned_data.get('copy_address'):
            if 'state' in self.cleaned_data:
                self.cleaned_data['ship_state'] = self.cleaned_data['state']
            return self.cleaned_data['ship_state']

        if self._local_only:
            country = self._default_country
        else:
            country = self.ship_charfield_clean('country')

        self._check_state(data, country)
        return data
    
    def save(self, contact=None, **kwargs):
        return self.save_info(contact=contact, **kwargs)
    
    def save_info(self, contact=None, **kwargs):
        """Save the contact info into the database.
        Checks to see if contact exists. If not, creates a contact
        and copies in the address and phone number."""
        
        if not contact:
            customer = Contact()
            log.debug('creating new contact')
        else:
            customer = contact
            log.debug('Saving contact info for %s', contact)

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
        
        companyname = data.pop('company', None)
        if companyname:
            org = Organization.objects.by_name(companyname, create=True)            
            customer.organization = org
        
        for field in customer.__dict__.keys():
            try:
                setattr(customer, field, data[field])
            except KeyError:
                pass

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
        
        signals.form_save.send(ContactInfoForm, object=customer, formdata=data, form=self)
        
        if changed_location:
            signals.satchmo_contact_location_changed.send(self, contact=customer)
        
        return customer.id
        
    def validate_postcode_by_country(self, postcode, country):
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
    years_to_display = range(datetime.datetime.now().year-100,datetime.datetime.now().year+1) 
    dob = forms.DateField(widget=SelectDateWidget(years=years_to_display), required=False)
    newsletter = forms.BooleanField(label=_('Newsletter'), widget=forms.CheckboxInput(), required=False)
