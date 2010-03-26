from django import template
import decimal

register = template.Library()

@register.filter
def flatten_discounts(items):
    flat_items = []
    for item in items:
        if item.unit_price != 0:
            f = item.discount / item.unit_price
        else:
            f = decimal.Decimal('0')
        free_qty = f.quantize(decimal.Decimal('1'), rounding=decimal.ROUND_FLOOR)
        partial_qty = int(not (f % decimal.Decimal('1')) == decimal.Decimal('0')) # bool to int
        full_qty = item.quantity - (free_qty + partial_qty)
        if free_qty:
            flat_items.append({'orderitem': item, 'price': 0, 'quantity': free_qty})
        if partial_qty:
            partial_price = item.unit_price - item.discount + item.unit_price * free_qty
            flat_items.append({'orderitem': item, 'price': partial_price, 'quantity': partial_qty})
        if full_qty:
            flat_items.append({'orderitem': item, 'price': item.unit_price, 'quantity': full_qty})
    return flat_items
