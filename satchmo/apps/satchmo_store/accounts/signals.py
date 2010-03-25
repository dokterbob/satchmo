import django.dispatch

#: Sent after a user has registered an account with the store.
#:
#: :param sender: The form which was submitted.
#: :type sender: ``satchmo_store.accounts.forms.RegistrationForm``
#:
#: :param contact: The contact that was saved to the database.
#: :type contact: ``satchmo_store.contact.models.Contact``
#:
#: :param subscribed: A boolean reflecting whether or not the user subscribed
#:   to a newsletter
#:
#:   :default: False
#:
#: :param data: The ``cleaned_data`` dictionary of the submitted form.
satchmo_registration = django.dispatch.Signal()

#: Sent after a user account has been verified. This signal is also sent right
#: after an account is created if account verification is disabled.
#:
#: :param sender: An instance of ``satchmo_store.models.Contact`` if the account
#:   was verified via email (Note: this is the same argument as ``contact``), or
#:   an instance of ``satchmo_store.accounts.forms.RegistrationForm`` if account
#:   verification is disabled.
#:
#: :param contact: The contact that was registered.
#: :type contact: ``satchmo_store.models.Contact``
satchmo_registration_verified = django.dispatch.Signal()
