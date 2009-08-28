"""Pluggable newsletter handling."""

from django import forms
from django.utils.translation import ugettext_lazy as _
from livesettings import config_value
from satchmo_store.accounts.signals import satchmo_registration
from satchmo_store.contact.signals import satchmo_contact_view
from satchmo_utils import load_module
from signals_ahoy.signals import form_initialdata
import logging
import signals

log = logging.getLogger('newsletter')

def get_newsletter_module():
    try:
        modulename = config_value('NEWSLETTER', 'MODULE')
    except AttributeError:
        modulename = 'satchmo_ext.newsletter.ignore'
        
    return load_module(modulename)

def is_subscribed(contact):
    if not contact:
        return False
    return get_newsletter_module().is_subscribed(contact)

def update_subscription(contact, subscribed, attributes={}):
    current = is_subscribed(contact)
    log.debug("Updating subscription status from %s to %s for %s", current, subscribed, contact)
    result = get_newsletter_module().update_contact(contact, subscribed, attributes=attributes)
    signals.newsletter_subscription_updated.send(contact, 
        old_state=current, new_state=subscribed, contact=contact, attributes=attributes)
    return result

def update_subscription_listener(contact=None, subscribed=False, **kwargs):
    if contact:
        update_subscription(contact, subscribed)

def populate_form_initialdata_listener(contact=None, initial = {}, **kwargs):
    if contact:
        current_subscriber = is_subscribed(contact)
    else:
        current_subscriber = False

    initial['newsletter'] = current_subscriber

def view_user_data_listener(contact=None, contact_dict=None, **kwargs):
    module = config_value('NEWSLETTER', 'MODULE')
    if module not in ('', 'satchmo_ext.newsletter.ignore'):
        contact_dict['show_newsletter'] = True
        contact_dict['newsletter'] = is_subscribed(contact)
    else:
        contact_dict['show_newsletter'] = False

satchmo_contact_view.connect(view_user_data_listener, sender=None)
satchmo_registration.connect(update_subscription_listener, sender=None)
form_initialdata.connect(populate_form_initialdata_listener, sender='RegistrationForm')
