"""Base forms for use in newsletter subscribing"""

from django import forms
from django.utils.translation import ugettext_lazy as _
from satchmo_ext.newsletter import update_subscription
from satchmo_ext.newsletter.models import get_contact_or_fake

_NOTSET = object()

class OptionalBoolean(forms.BooleanField):
    def __init__(self, *args, **kwargs):
        forms.BooleanField.__init__(self, *args, **kwargs)
        self.required = False

class NewsletterForm(forms.Form):
    full_name = forms.CharField(label=_('Full Name'), max_length=100, required=False)
    email = forms.EmailField(label=_('Email address'), max_length=75, required=True)
    subscribed = OptionalBoolean(label=_('Subscribe'), required=False, initial=True)

    def get_contact(self):
        data = self.cleaned_data
        email = data['email']
        full_name = data['full_name']
        
        return get_contact_or_fake(full_name, email)
    
    def save(self, state=_NOTSET, attributes={}):
        contact = self.get_contact()
        if state == _NOTSET:
            state = self.cleaned_data['subscribed']
        return update_subscription(contact, state, attributes=attributes)
