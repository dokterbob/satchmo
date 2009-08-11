from decimal import Decimal
from livesettings import config_value

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
        if orderitem.product.taxable:
            price = orderitem.sub_total
            return self.by_price(orderitem.product.taxClass, price)
        else:
            return Decimal("0.00")
        
    def by_price(self, taxclass, price):
        percent = config_value('TAX','PERCENT')
        p = price * (percent/100)
        return p
        
    def by_product(self, product, quantity=Decimal('1')):
        price = product.get_qty_price(quantity)
        taxclass = product.taxClass
        return self.by_price(taxclass, price)
        
    def get_percent(self, *args, **kwargs):
        return Decimal(config_value('TAX','PERCENT'))
    
    def get_rate(self, *args, **kwargs):
        return self.get_rate_percent/100
        
    def shipping(self, subtotal=None):
        if subtotal is None and self.order:
            subtotal = self.order.shipping_sub_total

        if subtotal:
            subtotal = self.order.shipping_sub_total
            if config_value('TAX','TAX_SHIPPING'):
                percent = config_value('TAX','PERCENT')
                t = subtotal * (percent/100)
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

        sub_total = Decimal("0.00")
        for item in order.orderitem_set.filter(product__taxable=True):
            sub_total += item.sub_total
        
        itemtax = sub_total * (percent/100)
        taxrates = {'%i%%' % percent :  itemtax}
        
        if config_value('TAX','TAX_SHIPPING'):
            shipping = order.shipping_sub_total
            sub_total += shipping
            ship_tax = shipping * (percent/100)
            taxrates['Shipping'] = ship_tax
        
        tax = sub_total * (percent/100)
        return tax, taxrates
