from decimal import Decimal

class Processor(object):
    
    def __init__(self, order):
        """
        Any preprocessing steps should go here
        For instance, copying the shipping and billing areas
        """
        pass
        
    def process(self):
        """
        Calculate the tax and return it
        """
        return Decimal("0.0")
