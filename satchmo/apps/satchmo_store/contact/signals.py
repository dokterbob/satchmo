import django.dispatch

"""
Signals for Contacts
"""

#: Sent after a user changes their location in their profile.
#:
#: :param sender: The form which was responsible for the location change.
#: :type sender: ``satchmo_store.contact.forms.ContactInfoForm``
#:
#: :param contact: The contact which was updated with a new location.
#: :type contact: ``satchmo_store.contact.models.Contact``
satchmo_contact_location_changed = django.dispatch.Signal()

#: Sent when contact information is viewed or updated before a template is
#: rendered. Allows you to override the contact information and context passed
#: to the templates used.
#:
#: :param sender: The contact representing the contact information being viewed,
#:   or None if the information cannot be found.
#: :type sender: ``satchmo_store.contact.models.Contact``
#:
#: :param contact: The contact representing the contact information being
#:   viewed, or None if the information cannot be found.
#: :type contact: ``satchmo_store.contact.models.Contact``
#:
#: :param contact_dict: A dictionary containing the intitial data for the
#:   instance of ``satchmo_store.contact.forms.ExtendedContactInfoForm``
#:   instance that will be rendered to the user.
#:
#: .. Note:: *contact* is the same as *sender*.
satchmo_contact_view = django.dispatch.Signal()

#: Sent when a form that contains postal codes (shipping and billing forms)
#: needs to validate. This signal can be used to custom validate postal postal
#: codes. Any listener should return the validated postal code or raise an
#: exception for an invalid postal code.
#:
#: :param sender: The form which is validating its postal codes.
#: :type sender: ``satchmo_store.contact.forms.ContactInfoForm``
#:
#: :param postcode: The postal code as a string being validated.
#:
#: :param country: The country that was selected in the form (or specified in
#:   the configuration if local sales are only allowed).
#: :type country: ``l10n.models.Country``
validate_postcode = django.dispatch.Signal()
