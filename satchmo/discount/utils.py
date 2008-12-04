try:
    from decimal import Decimal
except:
    from django.utils._decimal import Decimal

import datetime
import logging
import types
from satchmo.discount.models import Discount, NullDiscount

log = logging.getLogger('discount.utils')

def calc_by_percentage(price, percentage):
    if percentage > 1:
        log.warn("Correcting discount percentage, should be less than 1, is %s", percentage)
        percentage = percentage/100

    work = price * (1-percentage)
    cents = Decimal("0.01")
    return work.quantize(cents)

def find_discount_for_code(code, raises=False):
    discount = None

    if code:
        try:
            discount = Discount.objects.get(code=code, active=True)

        except Discount.DoesNotExist:
            pass

    
    if not discount:
        if raises:
            raise Discount.DoesNotExist()
        discount = NullDiscount()

    return discount

def find_auto_discounts(product):
    if not type(product) in (types.ListType, types.TupleType):
        product = (product,)
    today = datetime.date.today()
    discs = Discount.objects.filter(automatic=True, active=True, startDate__lte=today, endDate__gt=today)
    return discs.filter(validProducts__in=product).order_by('-percentage')

def find_best_auto_discount(product):
    discs = find_auto_discounts(product)
    if len(discs) > 0:
        return discs[0]
    else:
        return None
