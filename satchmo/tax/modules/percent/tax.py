from decimal import Decimal
from satchmo.configuration import config_value

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
        return self.by_price(price)
        
    def by_price(self, taxclass, price):
        percent = config_value('TAX','PERCENT')
        p = price * (percent/100)
        return round_cents(p)
        
    def by_product(self, product, quantity=1):
        price = product.get_qty_price(quantity)
        taxclass = product.taxClass
        return self.by_price(taxclass, price)
        
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
                
        return t
            
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


def round_cents(x):
    return x.quantize(Decimal('0.01'))