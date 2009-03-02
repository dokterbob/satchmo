from payment import signals, listeners

signals.payment_form_init.connect(listeners.shipping_hide_if_one, sender=None)