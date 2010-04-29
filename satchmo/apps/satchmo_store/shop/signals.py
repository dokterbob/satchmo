import django.dispatch

#
# Signals sent by Orders
#

#: Sent when an order is about to be cancelled and asks listeners if they allow
#: to do so.
#:
#: By default, orders in states 'Shipped', 'Completed' and 'Cancelled' are not
#: allowed to be cancelled. The default verdict is stored in
#: ``order.is_cancellable`` flag. Listeners can modify this flag, according to
#: their needs.
#:
#: :param sender: The order about to be cancelled.
#: :type sender: ``satchmo_store.shop.models.Order``
#:
#: :param order: The order about to be cancelled.
#: :type order: ``satchmo_store.shop.models.Order``
#:
#: .. Note:: *order* argument is the same as *sender*.
order_cancel_query = django.dispatch.Signal()

#: Sent when an order has been cancelled; it's status already reflects it and
#: has been saved to the database (e.g. payment gateway cancels payment).
#:
#: :param sender: The order that was cancelled.
#: :type sender: ``satchmo_store.shop.models.Order``
#:
#: :param order: The order that was cancelled.
#: :type order: ``satchmo_store.shop.models.Order``
#:
#: .. Note:: *order* argument is the same as *sender*.
order_cancelled = django.dispatch.Signal()

#: Sent when an order is complete and the balance goes to zero during a save.
#:
#: :param sender: The order that was successful.
#: :type sender: ``satchmo_store.shop.models.Order``
#: :param order: The order that was successful.
#: :type order: ``satchmo_store.shop.models.Order``
#:
#: .. Note:: *order* argument is the same as *sender*.
order_success = django.dispatch.Signal()

#: Sent by the order when its status has changed.
#satchmo_order_status_changed.send(self.order, oldstatus=oldstatus, newstatus=status, order=order)
satchmo_order_status_changed=django.dispatch.Signal()

#
# Signals sent by the Cart system
#

#: Sent by 'views.smart_add` to allow listeners to optionally change the
#: responding function.
#:
#: :param sender: The cart model
#: :type sender: ``satchmo_store.shop.models.Cart``
#:
#: :param request: The request used by the view
#: :type request: ``django.http.HttpRequest``
#:
#: :param method: A dictionary containing a single key ``view`` to be updated
#:   with the function to be called by smart_add. For example::
#:
#:       method = {'view': cart.add }
#:
#: .. Note:: *sender* is not a class instance.
cart_add_view = django.dispatch.Signal()

#: Sent after an item has been successfully added to the cart.
#:
#: :param sender: The cart the cart item was added to.
#: :type sender: ``satchmo_store.shop.models.Cart``
#:
#: :param cart: The cart the cart item was added to.
#: :type cart: ``satchmo_store.shop.models.Cart``
#:
#: :param cartitem: The cart item that was added to the cart.
#: :type cartitem: ``satchmo_store.shop.models.CartItem``
#:
#: :param product: The product that was added to the cart.
#: :type product: ``product.models.Product``
#:
#: :param form: The POST data for the form used to add the item to the cart.
#:
#: :param request: The request that used in the view to add the item to the
#:   cart.
#: :type request: ``django.http.HttpRequest``
#:
#: .. Note:: *cart* is the same as *sender*.
satchmo_cart_add_complete=django.dispatch.Signal()

#: Sent before an item is added to the cart.
#:
#: :param sender: The cart the cart item is being added to.
#: :type sender: ``satchmo_store.shop.models.Cart``
#:
#: :param cart: The cart the cart item is being added to.
#: :type cart: ``satchmo_store.shop.models.Cart``
#:
#: :param cartitem: The cart item that is being added to the cart.
#: :type cartitem: ``satchmo_store.shop.models.CartItem``
#:
#: :param added_quantity: The number of ``satchmo_store.shop.models.CartItem``
#:   instances items being added to the cart.
#: :type added_quantity: ``decimal.Decimal``
#:
#: :param details: A list of dictionaries containing additional details about the
#:   item if the item is a custom product or a gift certificate product. Each
#:   dictionary has the following entries:
#:
#:   :name: The name of the detail
#:   :value: The value of the detail
#:   :value: The value of the detail
#:   :sort_order: The order the detail should be listed in displays
#:   :price_change: The price change of the detail
#:
#:     :default: zero
#:
#: .. Note:: *cart* is the same as *sender*.
satchmo_cart_add_verify=django.dispatch.Signal()

#: Sent whenever the status of the cart has changed. For example, when an item
#: is added, removed, or had it's quantity updated.
#:
#: :param sender: The cart that was changed.
#: :type sender: ``satchmo_store.shop.models.Cart``
#:
#: :param cart: The cart that was changed.
#: :type cart: ``satchmo_store.shop.models.Cart``
#:
#: :param request: The request that used in the view to add the item to the
#:   cart.
#: :type request: ``django.http.HttpRequest``
#:
#: .. Note:: *cart* is the same as *sender*.
satchmo_cart_changed=django.dispatch.Signal()

#: Sent by the pricing system to allow price overrides when displaying line item
#: prices.
#:
#: :param sender: The cart item being queried for price overrides.
#: :type sender: ``satchmo_store.shop.models.CartItem``
#:
#: :param cartitem: The cart item being queried for price overrides.
#: :type cartitem: ``satchmo_store.shop.models.CartItem``
#:
#: .. Note:: *cartitem* is the same as *sender*.
satchmo_cartitem_price_query=django.dispatch.Signal()

#: Sent before an item is added to the cart so that listeners can update product
#: details.
#:
#: :param sender: The cart the cart item is being added to.
#: :type sender: ``satchmo_store.shop.models.Cart``
#:
#: :param product: The product that is being added to the cart.
#: :type product: ``product.models.Product`` or
#:   ``product.models.ConfigurableProduct``
#:
#: :param quantity: The number of ``satchmo_store.shop.models.CartItem``
#:    instances items being added to the cart.
#: :type quantity: ``decimal.Decimal``
#:
#: :param details: A list of dictionaries containing additional details about the
#:   item if the item is a custom product or a gift certificate product. Each
#:   dictionary has the following entries:
#:
#:   :name: The name of the detail
#:   :value: The value of the detail
#:   :value: The value of the detail
#:   :sort_order: The order the detail should be listed in displays
#:   :price_change: The price change of the detail
#:
#: :param form: The POST data for the form used to add the item to the cart.
#:
#: :param request: The request that used in the view to add the item to the
#:   cart.
#: :type request: ``django.http.HttpRequest``
#:
#: .. Note:: *cart* is the same as *sender*.
satchmo_cart_details_query=django.dispatch.Signal()

#
# Miscellaneous Signals
#

#: Sent when ``satchmo_store.shop.context_processors.settings()`` is invoked,
#: before the context is returned. This signal can be used to modify the context
#: returned by the context processor.
#:
#: :param sender: The current store configuration
#: :type sender: ``satchmo_store.shop.models.Config``
#:
#: :param context: A dictionary containing the context to be returned by the
#:   context processor. The dictionary contains:
#:
#:   :shop_base: The base URL for the store
#:   :shop: An instance of ``satchmo_store.shop.models.Config`` representing the
#:     current store configuration
#:   :shop_name: The shop name
#:   :media_url: The current media url, taking into account SSL
#:   :cart_count: The number of items in the cart
#:   :cart: An instance of ``satchmo_store.shop.models.Cart`` representing the
#:     current cart
#:   :categories: A ``QuerySet`` of all the ``product.models.Category`` objects
#:     for the current site.
#:   :is_secure: A boolean representing weather or not SSL is enabled
#:   :request: The ``HttpRequest`` object passed into the context processor
#:   :login_url: The login url defined in ``settings.LOGIN_URL``
#:   :logout_url: The logout url defined in ``settings.LOGOUT_URL``
#:   :sale: An instance of ``product.models.Discount`` if there is a current
#:     sale, or ``None``
satchmo_context = django.dispatch.Signal()

#: Sent after each item from the cart is copied into an order.
#:
#: :param sender: The cart the cart items are being copied into.
#: :type sender: ``satchmo_store.shop.models.Cart``
#:
#: :param cartitem: The cart item being copied into an order.
#: :type cartitem: ``satchmo_store.shop.models.CartItem``
#:
#: :param order: The order having items copied into it.
#: :type order: ``satchmo_store.shop.models.Order``
#:
#: :param orderitem: The order item being added to the order.
#: :type orderitem: ``satchmo_store.shop.models.OrderItem``
satchmo_post_copy_item_to_order=django.dispatch.Signal()

#: Sent by the order during the calculation of the total.
#satchmo_shipping_price_query.send(order, adjustment=shipadjust)
satchmo_shipping_price_query = django.dispatch.Signal()

#: Sent to determine where to redirect a user for a ``DownloadableProduct``.
#:
#: :param sender: ``None``
#: :type sender: ``None``
#:
#: :param file: The ``'file'`` field of the ``DownloadableProduct``.
#: :type file: ``django.db.models.fields.files.FileField``
#:
#: :param product: The product which is being downloaded.
#: :type product: ``product.models.DownloadableProduct``
#:
#: :param url_dict: A dictionary containing a single entry, ``'url'``, the URL
#:   which the user will be redirected to. Listeners should modify this value
#:   to change the redirect URL.
#:
#: .. Warning::
#:    For a sane ``filename`` parameter in the ``Content-Disposition`` header,
#:    users are cautioned against appending a trailing slash(``'/'``) to the
#:    URL.
sendfile_url_for_file = django.dispatch.Signal()

#
# Signals sent by email system
#

#: Sent by ``satchmo_store.mail.send_store_mail()`` before the message body is
#: rendered.
#:
#: Takes the same arguments as :data:`sending_store_mail`.
#:
#: .. Note::
#:   :ref:`send_mail_args <send_mail_args>` does not contain the ``'subject'``
#:   entry.
#:
#: .. Note::
#:   If the ``'message'`` entry is set in :ref:`send_mail_args <send_mail_args>`
#:   by a listener, it will be used instead of the rendered result in
#:   ``send_store_mail()``.
rendering_store_mail = django.dispatch.Signal()

#: Sent by ``satchmo_store.mail.send_store_mail()`` just before ``send_mail()``
#: is invoked.
#:
#: Listeners may raise ``satchmo_store.mail.ShouldNotSendMail``.
#:
#: If they choose to invoke ``django.mail.EmailMessage.send()``, any errors
#: raised will be handled by ``send_store_mail()``; they should consequently
#: raise ``ShouldNotSendMail`` to avoid re-sending the email.
#:
#: :param sender: Defaults to ``None``, unless the sender argument to
#:   ``send_store_mail()`` is specified; see below.
#:
#: .. _send_mail_args:
#:
#: :param send_mail_args: A dictionary containing the keyword arguments passed
#:   to ``send_mail()``:
#:
#:   - subject
#:   - message
#:   - from_email
#:   - recipient_list
#:   - fail_silently
#:
#: :param context: The context used to render the message body; by default, it
#:   contains the 'shop_name' key, but may contain other keys, depending on the
#:   `context` argument to ``send_store_mail()``.
#:
#: :param `**kwargs`: Additional keyword arguments received by
#:   ``send_store_mail()``.
#:
#: .. Note::
#:
#:    If the *context* argument to ``send_store_mail()`` contains the entry
#:    `send_mail_args`, it will not be available in the listener's *context*
#:    dictionary.
#:
#: Example::
#:
#:   from satchmo_store.shop.signals import order_notice_sender
#:
#:   def modify_subject(sender, send_mail_args={}, context={}, **kwargs):
#:     if not ('shop_name' in context and 'order' in context):
#:       return
#:
#:     send_mail_args['subject'] = '[%s] Woohoo! You got a *new* order! (ID: #%d)' % \
#:         (context['shop_name'], context['order'].id)
#:
#:   sending_store_mail.connect(modify_subject, sender=order_notice_sender)
#:
sending_store_mail = django.dispatch.Signal()

#
# Email senders.
#

# satchmo_store.notification
order_confirmation_sender = object()
order_notice_sender = object()
ship_notice_sender = object()

# satchmo_store.shop.views.contact
contact_sender = object()

# satchmo_store.registration
registration_sender = object()
