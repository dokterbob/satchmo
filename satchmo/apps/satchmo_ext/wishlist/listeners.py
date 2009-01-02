import logging

log = logging.getLogger('wishlist.listener')

def wishlist_cart_add_listener(sender, request=None, method={}, **kwargs):
    """Listens for cart_add_view signal and checks to see if it is a wishlist add request.
    If so, returns the wishlist add view method.
    """

    if request and request.method == "POST":
        if request.POST.get('addwish', '') != '' or request.POST.get('addwish.x', '') != '':
            log.debug("Found addwish in post, returning the wishlist add view")
            from satchmo_ext.wishlist.views import wishlist_add
            method['view'] = wishlist_add
    