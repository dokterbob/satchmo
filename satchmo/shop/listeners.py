from django.conf import settings
from django.utils.translation import gettext_lazy as _
from satchmo.shop.exceptions import OutOfStockError

def veto_out_of_stock(sender, cartitem=None, added_quantity=0, **kwargs):
    """Listener which vetoes adding products to the cart which are out of stock."""
    from satchmo.shop.models import Config
    config=Config.objects.get_current()

    if config.no_stock_checkout == False:
        product = cartitem.product
        need_qty = cartitem.quantity + added_quantity
        if product.items_in_stock < need_qty:
            raise OutOfStockError(product, product.items_in_stock, need_qty)
