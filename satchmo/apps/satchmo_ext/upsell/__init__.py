from satchmo_store.shop.signals import satchmo_cart_add_complete
import views

satchmo_cart_add_complete.connect(views.cart_add_listener, sender=None)
