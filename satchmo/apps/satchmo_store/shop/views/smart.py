"""Provides the ability to overload forms to provide multiple possible 
responses to a form.

For example, the product add form.  You can add to the cart, or to the 
wishlist.  The view here just looks in the formdata to determine whether
 to send the request to the cart_add or the wishlist_add view.
"""
from satchmo_store.shop.models import Cart
from satchmo_store.shop.signals import cart_add_view
from satchmo_store.shop.views import cart

def smart_add(request):
    """Redirect the request to cart_add (default) or whatever gets returned by
    the cart_add_view signal."""
    
    method={'view': cart.add}
    cart_add_view.send(Cart, request=request, method=method)
    
    return method['view'](request)
    
