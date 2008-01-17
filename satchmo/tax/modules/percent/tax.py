from decimal import Decimal
from satchmo.configuration import config_value
from satchmo.tax import round_cents

class Processor(object):
    
    method="percent"
    
    def __init__(self, order=None, user=None):
        """
        Any preprocessing steps should go here
        For instance, copying the shipping and billing areas
        """
        self.order = order
        self.user = user

    def by_orderitem(self, orderitem):
        price = orderitem.sub_total
        return self.by_price(orderitem.product.taxClass, price)
        
    def by_price(self, taxclass, price):
        percent = config_value('TAX','PERCENT')
        p = price * (percent/100)
        return round_cents(p)
        
    def by_product(self, product, quantity=1):
        price = product.get_qty_price(quantity)
        taxclass = product.taxClass
        return self.by_price(taxclass, price)
        
    def get_percent(self, *args, **kwargs):
        return Decimal(config_value('TAX','PERCENT'))
    
    def get_rate(self, *args, **kwargs):
        return self.get_rate_percent/100
        
    def shipping(self):
        if self.order:
            s = self.order.shipping_sub_total
            if config_value('TAX','TAX_SHIPPING'):
                percent = config_value('TAX','PERCENT')
                t = s * (percent/100)
            else:
                t = Decimal("0.00")
        else:
            t = Decimal("0.00")
                
        return round_cents(t)
            
    def process(self, order=None):
        """
        Calculate the tax and return it
        """
        if order:
            self.order = order
        else:
            order = self.order

        percent = config_value('TAX','PERCENT')    
        sub_total = order.sub_total-order.item_discount
        
        itemtax = sub_total * (percent/100)
        taxrates = {'%i%%' % percent :  round_cents(itemtax)}
        
        if config_value('TAX','TAX_SHIPPING'):
            shipping = order.shipping_sub_total
            sub_total += shipping
            ship_tax = shipping * (percent/100)
            taxrates['Shipping'] = round_cents(ship_tax)
        
        tax = sub_total * (percent/100)
        return round_cents(tax), taxrates
