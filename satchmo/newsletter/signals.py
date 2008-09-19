"""Satchmo product signals

Signals:
 - `newsletter_subscription_updated`: Usage::
    
    Usage: satchmo_price_query.send(sender, old_state=bool, new_state=bool, contact=contact) 
 
"""

import django.dispatch

newsletter_subscription_updated = django.dispatch.Signal()
