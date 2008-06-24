from django.db import models
from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _
from satchmo.contact.models import Contact
from satchmo.product.models import Product
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

    def save(self):
        """Ensure we have a create_date before saving the first time."""
        if not self.pk:
            self.create_date = datetime.date.today()
        super(ProductWish, self).save()

    class Admin:
        list_display = ('contact', 'product', 'create_date')
        ordering = ('contact', '-create_date', 'product')
        
    class Meta:
        verbose_name = _('Product Wish')
        verbose_name_plural = _('Product Wishes')
    