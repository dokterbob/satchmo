from decimal import Decimal
from satchmo.configuration import config_value

class Processor(object):
    
    def __init__(self, order):
        """
        Any preprocessing steps should go here
        For instance, copying the shipping and billing areas
        """
        self.order = order
        
    def process(self):
        """
        Calculate the tax and return it
        """
        subtotal = self.order.sub_total - self.order.discount
        
        if config_value('TAX','TAX_SHIPPING'):
            subtotal += self.order.shipping_cost
        
        percent = config_value('TAX','PERCENT')
        return subtotal * (percent/100)
