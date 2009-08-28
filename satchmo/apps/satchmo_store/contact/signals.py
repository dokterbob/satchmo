"""
Signals for contacts.

Signals:

 - `satchmo_contact_view`: called like so::

    signals.satchmo_contact_view.send(sender, contact=user_data, contact_dict=contact_dict)

 - `satchmo_contact_location_changed`
"""

import django.dispatch

satchmo_contact_location_changed = django.dispatch.Signal()
satchmo_contact_view = django.dispatch.Signal()
validate_postcode = django.dispatch.Signal()

