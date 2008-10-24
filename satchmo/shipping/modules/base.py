class BaseShipper(object):
    def __init__(self, cart=None, contact=None):
        self._calculated = False
        self.cart = cart
        self.contact = contact 
        self._calculated = False
        
        if cart or contact:
            self.calculate(cart, contact)
        
    def calculate(self, cart, contact):
        """
        Perform shipping calculations, separated from __init__ so that the object can be 
        used for keys and labels more easily.
        """
        self.cart = cart
        self.contact = contact
        self._calculated = True