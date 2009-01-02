from satchmo_ext.newsletter import update_subscription
import logging

log = logging.getLogger('newsletter.listeners')

def contact_form_listener(sender, object=None, formdata=None, form=None, **kwargs):
    if 'newsletter' not in formdata:
        subscribed = False
    else:
        subscribed = formdata['newsletter']
    
    log.debug('Updating newletter subscription for %s to %s', object, subscribed)
    update_subscription(object, subscribed)
