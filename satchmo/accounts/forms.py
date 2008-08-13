from django import forms
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.dispatch import dispatcher
from django.utils.translation import ugettext_lazy as _, ugettext
from satchmo.accounts.mail import send_welcome_email
from satchmo.configuration import config_value
from satchmo.contact.models import Contact
from satchmo.utils.unique_id import generate_id

import logging
import signals

log = logging.getLogger('newsletter.forms')

class RegistrationForm(forms.Form):
    """The basic account registration form."""
    email = forms.EmailField(label=_('Email address'),
        max_length=30, required=True)
    password2 = forms.CharField(label=_('Password (again)'),
        max_length=30, widget=forms.PasswordInput(), required=True)
    password1 = forms.CharField(label=_('Password'),
        max_length=30, widget=forms.PasswordInput(), required=True)
    first_name = forms.CharField(label=_('First name'),
        max_length=30, required=True)
    last_name = forms.CharField(label=_('Last name'),
        max_length=30, required=True)

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
        if email and User.objects.filter(email=email).count() > 0:
            raise forms.ValidationError(
                ugettext("That email address is already in use."))

        return email

    def save(self, request):
        """Create the contact and user described on the form.  Returns the
        `contact`.
        """

        data = self.cleaned_data
        password = data['password1']
        email = data['email']
        first_name = data['first_name']
        last_name = data['last_name']
        username = generate_id(first_name, last_name)

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
        contact.role = 'Customer'
        contact.save()

        if 'newsletter' not in data:
            subscribed = False
        else:
            subscribed = data['newsletter']

        dispatcher.send(signal=signals.satchmo_registration, contact=contact, subscribed=subscribed, data=data)

        if not verify:
            user = authenticate(username=username, password=password)
            login(request, user)
            send_welcome_email(email, first_name, last_name)
            dispatcher.send(signal=signals.satchmo_registration_verified, contact=contact)

        return contact

