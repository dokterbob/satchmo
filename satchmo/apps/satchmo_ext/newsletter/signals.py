"""Satchmo product signals

Signals:
 - `newsletter_subscription_updated`: Usage::
    
    Usage: newsletter_subscription_updated.send(sender, old_state=bool, new_state=bool, contact=contact) 
 
"""

import django.dispatch

newsletter_subscription_updated = django.dispatch.Signal()
