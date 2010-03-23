"""Satchmo product signals
"""

import django.dispatch

#newsletter_subscription_updated.send(sender, old_state=bool, new_state=bool, contact=contact)
newsletter_subscription_updated = django.dispatch.Signal()
