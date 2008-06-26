from django.dispatch import dispatcher
from satchmo.shop.signals import satchmo_cart_add_complete
import views

dispatcher.connect(views.cart_add_listener, signal=satchmo_cart_add_complete)