from django.utils.translation import ugettext_lazy as _

class CartAddProhibited(Exception):
    """Raised when a `signals.satchmo_cart_add_verify` listener vetoes adding an item to the cart.

    Params:
    - product: item which was being added
    - message: veto message
    """

    def __init__(self, product, message):
        self.product, self._message = product, message

    def _get_message(self):
        return self._message
    message = property(_get_message)

class OutOfStockError(CartAddProhibited):

    def __init__(self, product, have, need):
        if have == 0:
            msg = _("'%s' is out of stock.") % product.translated_name()
        else:
            msg = _("Only %(amount)i of '%(product)s' in stock.") % {
                'amount': have,
                'product': product.translated_name()
                }

        CartAddProhibited.__init__(self, product, msg)
        self.have = have
        self.need = need
