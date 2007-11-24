r"""
>>> from django.db import models
>>> from satchmo.shipping.modules.flat.shipper import Shipper as flat
>>> from satchmo.shipping.modules.per.shipper import Shipper as per
>>> from satchmo.product.models import *
>>> from satchmo.shop.models import *

>>> product1 = Product.objects.create(slug='p1', name='p1')
>>> cart1 = Cart.objects.create()
>>> cartitem1 = CartItem.objects.create(product=product1, cart=cart1,
...     quantity=3)

# Product.is_shippable should be True unless the Product has a subtype
# where is_shippable == False
>>> subtype1 = ConfigurableProduct.objects.create(product=product1)
>>> getattr(subtype1, 'is_shippable', True)
True
>>> product1.is_shippable
True
>>> cart1.is_shippable
True
>>> flat(cart1, None).cost()
Decimal("4.00")
>>> per(cart1, None).cost()
Decimal("12.00")

# TODO: Enable this test when DownloadableProduct is enabled
#>>> subtype2 = DownloadableProduct.objects.create(product=product1)
#>>> product1.get_subtypes()
#('ConfigurableProduct', 'DownloadableProduct')
#>>> subtype2.is_shippable
#False
#>>> product1.is_shippable
#False
#>>> cart1.is_shippable
#False
#>>> flat(cart1, None).cost()
#Decimal("0.00")
#>>> per(cart1, None).cost()
#Decimal("0.00")
"""

if __name__ == "__main__":
    import doctest
    doctest.testmod()

