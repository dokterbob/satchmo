class CartAddProhibited(Exception):
    """Raised when a `signals.satchmo_cart_add_verify` listener vetoes adding an item to the cart.
    
    Params:
    - product: item which was being added
    - message: veto message
    """
    
    def __init__(self, product, message):
        self.product, self.message = product, message

class OutOfStockError(CartAddProhibited):

    def __init__(self, product, have, need):
        if have == 0:
            msg = _("'%s' is out of stock.") % product.translated_name()
        else:
            msg = _("Only %(amount)i of '%(product)s' in stock.") % {
                'amount': have, 
                'product': product.translated_name()
                }
        
        super(OutOfStockError, self).__init__(self, product, msg)
        self.have = have
        self.need = need