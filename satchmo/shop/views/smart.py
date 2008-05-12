"""Provides the ability to overload forms to provide multiple possible 
responses to a form.

For example, the product add form.  You can add to the cart, or to the 
wishlist.  The view here just looks in the formdata to determine whether
 to send the request to the cart_add or the wishlist_add view.
"""
from satchmo.shop.utils import app_enabled
from satchmo.shop.views import cart
import logging
if app_enabled("wishlist"):
    from satchmo.wishlist.views import wishlist_add
    use_wishlist = True
else:
    wishlist_add = lambda x:x
    use_wishlist = False

log = logging.getLogger('shop.views.smart')

def smart_add(request):
    """Redirect the request to cart_add (default) or satchmo_wishlist_add 
    (overridden) view"""
    
    if use_wishlist:
        if request.POST.get('addwish', '') != '' or request.POST.get('addwish.x', '') != '':
            log.debug("Found addwish in post, returning the wishlist add view")
            from satchmo.wishlist.views import wishlist_add
            return wishlist_add(request)
    
    return cart.add(request)
