""" Just tracks subscriptions, nothing more. """

from satchmo.newsletter.models import Subscription
from django.utils.translation import ugettext as _
import logging

log = logging.getLogger('simple newsletter')

def is_subscribed(contact):
    return Subscription.email_is_subscribed(contact.email)

def update_contact(contact, subscribe, attributes={}):
    email = contact.email
    current = Subscription.email_is_subscribed(email)
    
    if current == subscribe:
        if subscribe:
            result = _("Already subscribed %(email)s.")
        else:
            result = _("Already removed %(email)s.")
        
    else:
        sub, created = Subscription.objects.get_or_create(email=email)
        sub.subscribed = subscribe
        sub.save()
        log.debug("Subscription now: %s" % sub)

        if subscribe:
            result = _("Subscribed: %(email)s")
        else:
            result = _("Unsubscribed: %(email)s")

    if attributes:
        sub, created = Subscription.objects.get_or_create(email=email)
        sub.update_attributes(attributes)    

    return result % { 'email' : email }
