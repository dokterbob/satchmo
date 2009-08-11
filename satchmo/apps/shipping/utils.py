from decimal import Decimal
from shipping.config import shipping_method_by_key

def update_shipping(order, shipping, contact, cart):
    """Set the shipping for this order"""
    # Set a default for when no shipping module is used
    order.shipping_cost = Decimal("0.00")

    # Save the shipping info
    shipper = shipping_method_by_key(shipping)
    shipper.calculate(cart, contact)
    order.shipping_description = shipper.description().encode("utf-8")
    order.shipping_method = shipper.method()
    order.shipping_cost = shipper.cost()
    order.shipping_model = shipping
