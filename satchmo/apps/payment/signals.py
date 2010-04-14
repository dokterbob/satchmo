import django.dispatch

#: Sent after ensuring that the cart and order are valid.
#:
#: :param sender: The controller which performed the sanity check.
#: :type sender: ``payment.views.confirm.ConfirmController``
#:
#: :param controller: The controller which performed the sanity check.
#: :type controller: ``payment.views.confirm.ConfirmController``
#:
#: .. Note:: *sender* is the same as *controller*.
confirm_sanity_check = django.dispatch.Signal()

#: Sent after a list of payment choices is compiled, allows the editing of
#: payment choices.
#:
#: :param sender: Always ``None``
#:
#: :param methods: A list of 2-element tuples containing the name and label for
#:   each active payment module.
payment_choices = django.dispatch.Signal()

#: Sent when a ``payment.forms.PaymentMethodForm`` is initialized. Receivers
#: have cart/order passed in variables to check the contents and modify methods
#: list if neccessary.
#:
#: :param sender: The form that is being initialized.
#: :type sender: ``payment.forms.PaymentMethodForm``
#:
#: :param methods: A list of 2-element tuples containing the name and label for
#:   each active payment module.
#:
#: :param cart: The cart.
#: :type cart: ``satchmo_store.shop.models.Cart``
#:
#: :param order: The current order.
#: :type order: ``satchmo_store.shop.models.Order``
#:
#: :param contact: The contact representing the current customer if
#:   authenticated; it is None otherwise.
#: :type contact: ``satchmo_store.contact.models.Contact``
#:
#: The following example shows how to conditionally modify the payment choices 
#: presented to a customer::
#:
#:  def adjust_payment_choices(sender, contact, methods, **kwargs):
#:      if should_reduce: # whatever your condition is
#:          for method in methods:
#:              if method[0] == 'PAYMENT_PMTKEY':
#:                  methods.remove(method)

payment_methods_query = django.dispatch.Signal()
