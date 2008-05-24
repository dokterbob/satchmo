try:
    from decimal import Decimal, getcontext
except:
    from django.utils._decimal import Decimal, getcontext
from datetime import date
from models import Discount, NullDiscount
import types

def calc_by_percentage(price, percentage):
    if percentage > 1:
        log.warn("Correcting discount percentage, should be less than 1, is %s", percentage)
        percentage = percentage/100
        
    work = price * percentage
    cents = Decimal("0.01")
    return work.quantize(cents)

def find_discount_for_code(code):
    discount = None
    
    if code:
        try:
            discount = Discount.objects.get(code=code)
            
        except Discount.DoesNotExist:
            pass
            
    if not discount:
        discount = NullDiscount()
        
    return discount
    
def find_auto_discounts(product):
    if not type(product) in (types.ListType, types.TupleType):
        product = (product,)
    today = date.today()
    discs = Discount.objects.filter(automatic=True, startDate__gte=today, endDate__gt=today) 
    return discs.filter(validProducts__in=product).order_by('-percentage')

def find_best_auto_discount(product):
    discs = find_auto_discounts(product)
    if len(discs) > 0:
        return discs[0]
    else:
        return None