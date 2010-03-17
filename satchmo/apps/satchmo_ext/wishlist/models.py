from django.db import models
try:
    from django.utils import simplejson
except ImportError:
    import simplejson
from django.utils.translation import ugettext_lazy as _
from listeners import wishlist_cart_add_listener
from satchmo_store import shop
from satchmo_store.contact.models import Contact
from product.models import Product
from satchmo_store.shop.signals import cart_add_view
from signals_ahoy.signals import collect_urls
import datetime

class ProductWishManager(models.Manager):
    def create_if_new(self, product, contact, details):
        encoded = simplejson.dumps(details)

        products = ProductWish.objects.filter(product=product, contact=contact, _details=encoded)
        if products and len(products) > 0:
            wish = products[0]
            if len(products) > 1:
                for p in products[1:]:
                    p.delete()
        else:
            wish = ProductWish(product=product, contact=contact)
            wish.details = details
            wish.save()
            
        return wish        

class ProductWish(models.Model):
    contact = models.ForeignKey(Contact, verbose_name=_("Contact"), related_name="contacts")
    product = models.ForeignKey(Product, verbose_name=_("Product"), related_name="products")
    _details = models.TextField(_('Details'), null=True, blank=True)
    create_date = models.DateTimeField(_("Creation Date"))
    
    objects = ProductWishManager()

    def set_details(self, raw):
        """Set the details from a raw list"""
        if raw:
            self._details = simplejson.dumps(raw)
    
    def get_details(self):
        """Convert the pickled details into a list"""
        if self._details:
            return simplejson.loads(self._details)
        else:
            return []

    details = property(fget=get_details, fset=set_details)

    def save(self, **kwargs):
        """Ensure we have a create_date before saving the first time."""
        if not self.pk:
            self.create_date = datetime.date.today()
        super(ProductWish, self).save(**kwargs)
        
    class Meta:
        verbose_name = _('Product Wish')
        verbose_name_plural = _('Product Wishes')

cart_add_view.connect(wishlist_cart_add_listener)

import config
from urls import add_wishlist_urls
collect_urls.connect(add_wishlist_urls, sender=shop)
