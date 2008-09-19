"""Pluggable newsletter handling."""

from django import forms
from django.utils.translation import ugettext_lazy as _
from satchmo.accounts.signals import satchmo_registration, satchmo_registration_initialdata
from satchmo.configuration import config_value
from satchmo.contact.signals import satchmo_contact_view
from satchmo.utils import load_module
import logging
import signals

log = logging.getLogger('newsletter')

def get_newsletter_module():
    try:
        modulename = config_value('NEWSLETTER', 'MODULE')
    except AttributeError:
        modulename = 'satchmo.newsletter.ignore'
        
    return load_module(modulename)

def is_subscribed(contact):
    if not contact:
        return False
    return get_newsletter_module().is_subscribed(contact)

def update_subscription(contact, subscribed):
    current = is_subscribed(contact)
    log.debug("Updating subscription status from %s to %s for %s", current, subscribed, contact)
    result = get_newsletter_module().update_contact(contact, subscribed)
    signals.newsletter_subscription_updated.send(contact, old_state=current, new_state=subscribed, contact=contact)
    return result

def update_subscription_listener(contact=None, subscribed=False, **kwargs):
    if contact:
        update_subscription(contact, subscribed)

def populate_form_initialdata_listener(contact=None, initial_data = {}, **kwargs):
    if contact:
        current_subscriber = is_subscribed(contact)
    else:
        current_subscriber = False

    initial_data['newsletter'] = current_subscriber

def view_user_data_listener(contact=None, contact_dict=None, **kwargs):
    module = config_value('NEWSLETTER', 'MODULE')
    if module not in ('', 'satchmo.newsletter.ignore'):
        contact_dict['show_newsletter'] = True
        contact_dict['newsletter'] = is_subscribed(contact)
    else:
        contact_dict['show_newsletter'] = False

satchmo_contact_view.connect(view_user_data_listener, sender=None)
satchmo_registration.connect(update_subscription_listener, sender=None)
satchmo_registration_initialdata.connect(populate_form_initialdata_listener, sender=None)
