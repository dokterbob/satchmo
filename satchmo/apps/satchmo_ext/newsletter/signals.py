"""Satchmo product signals
"""

import django.dispatch

#: Sent after a newsletter subscription has been updated.
#:
#: :param sender: The contact for which the subscription status is being updated.
#: :type sender: ``satchmo_store.models.Contact``
#:
#: :param old_state: A Boolean representing the old state of subscription.
#: :param new_state: A Boolean representing the new state of the subscription.
#:
#: :param contact: The contact for which the subscription status is being updated.
#: :type contact: ``satchmo_store.models.Contact``
#:
#: :param attributes: An empty dictionary. This argument is not currently used.
#:
#. .. Note:: *contact* is the same as *sender*.
newsletter_subscription_updated = django.dispatch.Signal()
