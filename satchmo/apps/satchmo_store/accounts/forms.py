from django import forms
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _, ugettext
from satchmo_store.accounts.mail import send_welcome_email
from livesettings import config_value
from satchmo_store.contact.forms import ContactInfoForm
from satchmo_store.contact.models import AddressBook, PhoneNumber, Contact, ContactRole
from l10n.models import Country
from satchmo_utils.unique_id import generate_id
from signals_ahoy.signals import form_init, form_initialdata

import logging
import signals

log = logging.getLogger('accounts.forms')

class EmailAuthenticationForm(AuthenticationForm):
    """Authentication form with a longer username field."""
    
    def __init__(self, *args, **kwargs):
        
        super(EmailAuthenticationForm, self).__init__(*args, **kwargs)
        username = self.fields['username']
        username.max_length = 75
        username.widget.attrs['maxlength'] = 75

class RegistrationForm(forms.Form):
    """The basic account registration form."""
    title = forms.CharField(max_length=30, label=_('Title'), required=False)
    email = forms.EmailField(label=_('Email address'),
        max_length=75, required=True)
    password2 = forms.CharField(label=_('Password (again)'),
        max_length=30, widget=forms.PasswordInput(), required=True)
    password1 = forms.CharField(label=_('Password'),
        max_length=30, widget=forms.PasswordInput(), required=True)
    first_name = forms.CharField(label=_('First name'),
        max_length=30, required=True)
    last_name = forms.CharField(label=_('Last name'),
        max_length=30, required=True)
    next = forms.CharField(max_length=100, required=False, widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        contact = kwargs.get('contact', None)
        initial = kwargs.get('initial', {})
        self.contact = contact
        form_initialdata.send(self.__class__,
            form=self,
            contact=contact,
            initial=initial)
        
        kwargs['initial'] = initial
        super(RegistrationForm, self).__init__(*args, **kwargs)
        form_init.send(self.__class__,
            form=self,
            contact=contact)

    newsletter = forms.BooleanField(label=_('Newsletter'),
        widget=forms.CheckboxInput(), required=False)

    def clean_password1(self):
        """Enforce that password and password2 are the same."""
        p1 = self.cleaned_data.get('password1')
        p2 = self.cleaned_data.get('password2')
        if not (p1 and p2 and p1 == p2):
            raise forms.ValidationError(
                ugettext("The two passwords do not match."))

        # note, here is where we'd put some kind of custom
        # validator to enforce "hard" passwords.
        return p1

    def clean_email(self):
        """Prevent account hijacking by disallowing duplicate emails."""
        email = self.cleaned_data.get('email', None)
        if email and User.objects.filter(email__iexact=email).count() > 0:
            raise forms.ValidationError(
                ugettext("That email address is already in use."))

        return email

    def save(self, request=None, **kwargs):
        """Create the contact and user described on the form.  Returns the
        `contact`.
        """
        if self.contact:
            log.debug('skipping save, already done')
        else:
            self.save_contact(request)
        return self.contact

    def save_contact(self, request):
        log.debug("Saving contact")
        data = self.cleaned_data
        password = data['password1']
        email = data['email']
        first_name = data['first_name']
        last_name = data['last_name']
        username = generate_id(first_name, last_name, email)

        verify = (config_value('SHOP', 'ACCOUNT_VERIFICATION') == 'EMAIL')

        if verify:
            from registration.models import RegistrationProfile
            user = RegistrationProfile.objects.create_inactive_user(
                username, password, email, send_email=True)
        else:
            user = User.objects.create_user(username, email, password)

        user.first_name = first_name
        user.last_name = last_name
        user.save()

        # If the user already has a contact, retrieve it.
        # Otherwise, create a new one.
        try:
            contact = Contact.objects.from_request(request, create=False)

        except Contact.DoesNotExist:
            contact = Contact()

        contact.user = user
        contact.first_name = first_name
        contact.last_name = last_name
        contact.email = email
        contact.role = ContactRole.objects.get(pk='Customer')
        contact.title = data.get('title', '')
        contact.save()

        if 'newsletter' not in data:
            subscribed = False
        else:
            subscribed = data['newsletter']

        signals.satchmo_registration.send(self, contact=contact, subscribed=subscribed, data=data)

        if not verify:
            user = authenticate(username=username, password=password)
            login(request, user)
            send_welcome_email(email, first_name, last_name)
            signals.satchmo_registration_verified.send(self, contact=contact)

        self.contact = contact

        return contact

class RegistrationAddressForm(RegistrationForm, ContactInfoForm):
    """Registration form which also requires address information."""
    
    def __init__(self, *args, **kwargs):
        super(RegistrationAddressForm, self).__init__(*args, **kwargs)

    def save(self, request=None, **kwargs):
        contact = self.save_contact(request)
        kwargs['contact'] = contact
        
        log.debug('Saving address for %s', contact)
        self.save_info(**kwargs)
                
        return contact
