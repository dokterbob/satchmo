"""Pluggable newsletter handling."""

from satchmo.configuration import config_value
from satchmo.shop.utils import load_module

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
