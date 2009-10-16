from django import forms
from django.contrib.auth.models import User
from django.db.models import Q
from django.forms.extras.widgets import SelectDateWidget
from django.utils.translation import ugettext_lazy as _, ugettext
from l10n.models import Country
from livesettings import config_value, config_get_group, SettingNotSet
from satchmo_store.contact.models import Contact, AddressBook, PhoneNumber, Organization, ContactRole
from satchmo_store.shop.models import Config
from signals_ahoy.signals import form_init, form_initialdata, form_postsave
import datetime
import logging
import signals

log = logging.getLogger('satchmo_store.contact.forms')

selection = ''

class ProxyContactForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self._contact = kwargs.pop('contact', None)
        super(ProxyContactForm, self).__init__(*args, **kwargs)

class ContactInfoForm(ProxyContactForm):
    email = forms.EmailField(max_length=75, label=_('Email'), required=False)
    title = forms.CharField(max_length=30, label=_('Title'), required=False)
    first_name = forms.CharField(max_length=30, label=_('First Name'), required=False)
    last_name = forms.CharField(max_length=30, label=_('Last Name'), required=False)
    phone = forms.CharField(max_length=30, label=_('Phone'), required=False)
    addressee = forms.CharField(max_length=61, label=_('Addressee'), required=False)
    organization = forms.CharField(max_length=50, label=_('Organization'), required=False)
    street1 = forms.CharField(max_length=30, label=_('Street'), required=False)
    street2 = forms.CharField(max_length=30, required=False)
    city = forms.CharField(max_length=30, label=_('City'), required=False)
    state = forms.CharField(max_length=30, label=_('State'), required=False)
    postal_code = forms.CharField(max_length=10, label=_('ZIP code/Postcode'), required=False)
    copy_address = forms.BooleanField(label=_('Shipping same as billing?'), required=False)
    ship_addressee = forms.CharField(max_length=61, label=_('Addressee'), required=False)
    ship_street1 = forms.CharField(max_length=30, label=_('Street'), required=False)
    ship_street2 = forms.CharField(max_length=30, required=False)
    ship_city = forms.CharField(max_length=30, label=_('City'), required=False)
    ship_state = forms.CharField(max_length=30, label=_('State'), required=False)
    ship_postal_code = forms.CharField(max_length=10, label=_('ZIP code/Postcode'), required=False)
    next = forms.CharField(max_length=40, widget=forms.HiddenInput(), required=False)

    def __init__(self, *args, **kwargs):
        initial = kwargs.get('initial', {})
        form_initialdata.send(self.__class__, form=self, initial=initial, contact = kwargs.get('contact', None))
        kwargs['initial'] = initial
        
        shop = kwargs.pop('shop', None)
        shippable = kwargs.pop('shippable', True)
        super(ContactInfoForm, self).__init__(*args, **kwargs)
        if not shop:
            shop = Config.objects.get_current()
        self._shop = shop
        self._shippable = shippable

        self.required_billing_data = config_value('SHOP', 'REQUIRED_BILLING_DATA')
        self._local_only = shop.in_country_only
        areas = shop.areas()
        self.enforce_state = config_value('SHOP','ENFORCE_STATE')

        if shop.in_country_only and areas and areas.count()>0:
            areas = [(area.abbrev or area.name, area.name) for area in areas]
            areas.insert(0,('',_("---Please Select---")))
            billing_state = (self._contact and getattr(self._contact.billing_address, 'state', None)) or selection
            shipping_state = (self._contact and getattr(self._contact.shipping_address, 'state', None)) or selection
            if self.enforce_state:
                self.fields['state'] = forms.ChoiceField(choices=areas, initial=billing_state, label=_('State'))
                self.fields['ship_state'] = forms.ChoiceField(choices=areas, initial=shipping_state, required=False, label=_('State'))
        
        self._default_country = shop.sales_country
        billing_country = (self._contact and getattr(self._contact.billing_address, 'country', None)) or self._default_country
        shipping_country = (self._contact and getattr(self._contact.shipping_address, 'country', None)) or self._default_country
        self.fields['country'] = forms.ModelChoiceField(shop.countries(), required=False, label=_('Country'), empty_label=None, initial=billing_country.pk)
        self.fields['ship_country'] = forms.ModelChoiceField(shop.countries(), required=False, label=_('Country'), empty_label=None, initial=shipping_country.pk)
        
        for fname in self.required_billing_data:
            if fname == 'country' and self._local_only:
                continue
            self.fields[fname].required = True
                
        # slap a star on the required fields
        for f in self.fields:
            fld = self.fields[f]
            if fld.required:
                fld.label = (fld.label or f) + '*'
        log.info('Sending form_init signal: %s', self.__class__)
        form_init.send(self.__class__, form=self)

    def _check_state(self, data, country):
        if country and self.enforce_state and country.adminarea_set.filter(active=True).count() > 0:
            if not data or data == selection:
                raise forms.ValidationError(
                    self._local_only and _('This field is required.') \
                               or _('State is required for your country.'))
            if (country.adminarea_set
                        .filter(active=True)
                        .filter(Q(name__iexact=data)|Q(abbrev__iexact=data))
                        .count() != 1):
                raise forms.ValidationError(_('Invalid state or province.'))
        return data

                
    def clean_email(self):
        """Prevent account hijacking by disallowing duplicate emails."""
        email = self.cleaned_data.get('email', None)
        if self._contact:
            if self._contact.email and self._contact.email == email:
                return email
            users_with_email = Contact.objects.filter(email=email)
            if len(users_with_email) == 0:
                return email
            if len(users_with_email) > 1 or users_with_email[0].id != self._contact.id:
                raise forms.ValidationError(
                    ugettext("That email address is already in use."))
        return email
    
    def clean_postal_code(self):
        postcode = self.cleaned_data.get('postal_code')
        if not postcode and 'postal_code' not in self.required_billing_data:
            return postcode
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
        if not self._shippable:
            return self.cleaned_data.get('country')
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
        else:
            val = self.fields['ship_' + field_name].clean(self.data.get('ship_' + field_name))
            if (not val) and field_name in ('street1', 'city', 'state', 'postal_code'):
                raise forms.ValidationError(_('This field is required.'))
            return val

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
        if not self._shippable:
            return code

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
    
    def save(self, **kwargs):
        if not kwargs.has_key('contact'):
            kwargs['contact'] = None
        return self.save_info(**kwargs)
    
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

        organization_name = data.pop('organization', None)
        if organization_name:
            org = Organization.objects.by_name(organization_name, create=True)
            customer.organization = org
        else:
            # in case customer wants to remove organization name from their profile
            customer.organization = None

        for field in customer.__dict__.keys():
            try:
                setattr(customer, field, data[field])
            except KeyError:
                pass

        if not customer.role:
            customer.role = ContactRole.objects.get(pk='Customer')

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
            if (not changed_location) and field in ('state', 'country_id', 'city'):
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
                ship_field = 'ship_' + field
                if (not changed_location) and field in ('state', 'country_id', 'city'):
                    if getattr(ship_address, field) != data[ship_field]:
                        changed_location = True
                try:
                    setattr(ship_address, field, data[ship_field])
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
        
        form_postsave.send(ContactInfoForm, object=customer, formdata=data, form=self)
        
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
