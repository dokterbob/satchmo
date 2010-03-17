from django.db import models
from django.utils.translation import ugettext_lazy as _
from satchmo_store.contact.models import Contact
import datetime
import logging

log = logging.getLogger('newsletter.models')

_NOTSET = object()

class NullContact(object):
    """Simple object emulating a Contact, so that we can add users who aren't Satchmo Contacts.

    Note, this is *not* a Django object, and is not saved to the DB, only to the subscription lists.
    """

    def __init__(self, full_name, email):
        if not full_name:
            full_name = email.split('@')[0]

        self.full_name = full_name
        self.email = email

def get_contact_or_fake(full_name, email):
    """Get a `Contact` by email or if it doesn't exist, then a `NullContact`"""
    try:
        contact = Contact.objects.get(email=email)

    except Contact.DoesNotExist:
        contact = NullContact(full_name, email)

    return contact

class Subscription(models.Model):
    """A newsletter subscription."""

    subscribed = models.BooleanField(_('Subscribed'), default=True)
    email = models.EmailField(_('Email'), max_length=75)
    create_date = models.DateField(_("Creation Date"))
    update_date = models.DateField(_("Update Date"))

    def email_is_subscribed(cls, email):
        try:
            sub = cls.objects.get(email=email)
            return sub.subscribed
        except cls.DoesNotExist:
            return False

    email_is_subscribed = classmethod(email_is_subscribed)

    def __unicode__(self):
        if self.subscribed:
            flag="Y"
        else:
            flag="N"
        return u"[%s] %s" % (flag, self.email)

    def __repr__(self):
        return "<Subscription: %s>" % str(self)

    def attribute_value(self, name, value=_NOTSET):
        """Get a value from an attribute."""
        try:
            att = self.attributes.get(name=name)
            value = att.value
        except SubscriptionAttribute.DoesNotExist:
            if value != _NOTSET:
                raise

        return value

    def save(self, **kwargs):
        if not self.pk:
            self.create_date = datetime.date.today()

        self.update_date = datetime.date.today()

        super(Subscription, self).save(**kwargs)
                
    def update_attribute(self, name, value):
        """Update or create a `SubscriptionAttribute` object with the passed `name` and `value`."""
        value = str(value)
        try:
            att = self.attributes.get(name=name)
            att.value = value
        except SubscriptionAttribute.DoesNotExist:
            att = SubscriptionAttribute(subscription=self, name=name, value=value)
        
        att.save()
        return att

    def update_attributes(self, attributes):
        """Update `SubscriptionAttribute` objects from a dictionary of name val mappings."""
        return [self.update_attribute(name, value) for name, value in attributes.items()]

        
class SubscriptionAttribute(models.Model):
    """
    Allows arbitrary name/value pairs (as strings) to be attached to a subscription.
    """
    subscription = models.ForeignKey(Subscription, related_name="attributes")
    name = models.SlugField(_("Attribute Name"), max_length=100, )
    value = models.CharField(_("Value"), max_length=255)

    class Meta:
        verbose_name = _("Subscription Attribute")
        verbose_name_plural = _("Subscription Attributes")

import config
import listeners
listeners.start_listening()
