"""
Signals for contacts.

Signals:

 - `satchmo_contact_view`: called like so::

    signals.satchmo_contact_view.send(sender, contact=user_data, contact_dict=contact_dict)

 - `satchmo_contact_location_changed`

 - `form_save`: called from a form::

    signals.form_save.send(ContactInfoForm, object=customer, formdata=data, form=self)

 - `form_init`: called when a contact info form is
   initialized::

    signals.form_init.send(ContactInfoForm, form=self)

"""

import django.dispatch

form_init = django.dispatch.Signal()
form_save = django.dispatch.Signal()
satchmo_contact_location_changed = django.dispatch.Signal()
satchmo_contact_view = django.dispatch.Signal()
validate_postcode = django.dispatch.Signal()

