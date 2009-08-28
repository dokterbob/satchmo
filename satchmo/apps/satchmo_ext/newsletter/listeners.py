from satchmo_ext.newsletter import update_subscription
from satchmo_store.contact.forms import ContactInfoForm
from signals_ahoy.signals import collect_urls, form_postsave
import logging

log = logging.getLogger('newsletter.listeners')

def contact_form_listener(sender, object=None, formdata=None, form=None, **kwargs):
    if 'newsletter' not in formdata:
        subscribed = False
    else:
        subscribed = formdata['newsletter']
    
    log.debug('Updating newletter subscription for %s to %s', object, subscribed)
    update_subscription(object, subscribed)
    
def start_listening():
    from urls import add_newsletter_urls
    from satchmo_store import shop
    
    form_postsave.connect(contact_form_listener, sender=ContactInfoForm)
    collect_urls.connect(add_newsletter_urls, sender=shop)

