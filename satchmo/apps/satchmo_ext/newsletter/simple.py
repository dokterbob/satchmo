""" Just tracks subscriptions, nothing more. """

from satchmo_ext.newsletter.models import Subscription
from django.utils.translation import ugettext as _
import logging

log = logging.getLogger('simple newsletter')

def is_subscribed(contact):
    return Subscription.email_is_subscribed(contact.email)

def update_contact(contact, subscribe, attributes={}):
    email = contact.email
    current = Subscription.email_is_subscribed(email)
    attributesChanged = False
    sub = None
    
    if attributes:
        sub, created = Subscription.objects.get_or_create(email=email)
        if created:
            attributesChanged = True
        else:
            oldAttr = [(a.name,a.value) for a in sub.attributes.all()]
            oldAttr.sort()
        sub.update_attributes(attributes)
        newAttr = [(a.name,a.value) for a in sub.attributes.all()]
        newAttr.sort()
        
        if not created:
            attributesChanged = oldAttr != newAttr
    
    if current == subscribe:
        if subscribe:
            if attributesChanged:
                result = _("Updated subscription for %(email)s.")
            else:
                result = _("Already subscribed %(email)s.")
                
        else:
            result = _("Already removed %(email)s.")
        
    else:
        if not sub:
            sub, created = Subscription.objects.get_or_create(email=email)
        sub.subscribed = subscribe
        sub.save()
        log.debug("Subscription now: %s" % sub)

        if subscribe:
            result = _("Subscribed: %(email)s")
        else:
            result = _("Unsubscribed: %(email)s")

    return result % { 'email' : email }
