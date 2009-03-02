from payment import signals, listeners, forms

signals.payment_form_init.connect(listeners.shipping_hide_if_one, sender=forms.SimplePayShipForm)