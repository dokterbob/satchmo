"""Pluggable newsletter handling."""

from django import forms
from django.dispatch import dispatcher
from django.utils.translation import ugettext_lazy as _
from satchmo.accounts.signals import satchmo_registration, satchmo_registration_initialdata
from satchmo.configuration import config_value
from satchmo.utils import load_module
import logging

log = logging.getLogger('newsletter')

def get_newsletter_module():
    try:
        modulename = config_value('NEWSLETTER', 'MODULE')
    except AttributeError:
        modulename = 'satchmo.newsletter.ignore'
        
    return load_module(modulename)

def is_subscribed(contact):
    return get_newsletter_module().is_subscribed(contact)

def update_subscription(contact, subscribed):
    return get_newsletter_module().update_contact(contact, subscribed)

def update_subscription_from_signal(contact=None, subscribed=False, **kwargs):
    if contact:
        update_subscription(contact, subscribed)

def populate_form_initialdata(contact=None, initial_data = {}, **kwargs):
    if contact:
        current_subscriber = is_subscribed(contact)
    else:
        current_subscriber = False

    initial_data['newsletter'] = current_subscriber

dispatcher.connect(update_subscription_from_signal, signal=satchmo_registration)
dispatcher.connect(populate_form_initialdata, signal=satchmo_registration_initialdata)
