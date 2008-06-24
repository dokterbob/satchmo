"""
Configuration items for the shop.
Also contains shopping cart and related classes.
"""
import datetime
try:
    from decimal import Decimal
except:
    from django.utils._decimal import Decimal

from logging import getLogger

from django.conf import settings
from django.contrib.sites.models import Site
from django.db import models
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext_lazy as _

from satchmo import tax
from satchmo.configuration import ConfigurationSettings, config_value
from satchmo.contact.models import Contact, Order
from satchmo.l10n.models import Country
from satchmo.product.models import Product
from satchmo.shop.utils import url_join

log = getLogger('satchmo.shop.models')

class NullConfig(object):
    """Standin for a real config when we don't have one yet."""

    def __init__(self):
        self.store_name = self.store_description = _("Test Store")
        self.store_email = self.street1 = self.street2 = self.city = self.state = self.postal_code = self.phone = ""
        self.site = self.country = None
        self.no_stock_checkout = False
        self.in_country_only = True
        self.sales_country = Country.objects.get(iso3_code__exact='USA')

    def _options(self):
        return ConfigurationSettings()

    options = property(fget=_options)

    def __str__(self):
        return "Test Store - no configured store exists!"

class Config(models.Model):
    """
    Used to store specific information about a store.  Also used to
    configure various store behaviors
    """
    site = models.OneToOneField(Site, verbose_name=_("Site"), primary_key=True)
    store_name = models.CharField(_("Store Name"),max_length=100, unique=True)
    store_description = models.TextField(_("Description"), blank=True, null=True)
    store_email = models.EmailField(_("Email"), blank=True, null=True)
    street1=models.CharField(_("Street"),max_length=50, blank=True, null=True)
    street2=models.CharField(_("Street"), max_length=50, blank=True, null=True)
    city=models.CharField(_("City"), max_length=50, blank=True, null=True)
    state=models.CharField(_("State"), max_length=30, blank=True, null=True)
    postal_code=models.CharField(_("Zip Code"), blank=True, null=True, max_length=9)
    country=models.ForeignKey(Country, blank=True, null=True, verbose_name=_('Country'))
    phone = models.CharField(_("Phone Number"), blank=True, null=True, max_length=12)
    no_stock_checkout = models.BooleanField(_("Purchase item not in stock?"), default=True)
    in_country_only = models.BooleanField(_("Only sell to in-country customers?"), default=True)
    sales_country = models.ForeignKey(Country, blank=True, null=True,
                                     related_name='sales_country',
                                     verbose_name=_("Default country for customers"))
    shipping_countries = models.ManyToManyField(Country, filter_interface=True, blank=True, verbose_name=_("Shipping Countries"), related_name="shop_configs")

    def _get_shop_config(cls):
        """Convenience method to get the current shop config"""
        try:
            shop_config = cls.objects.get(site=settings.SITE_ID)
        except Config.DoesNotExist:
            log.warning("No Shop Config found, using test shop config.")
            shop_config = NullConfig()

        return shop_config

    get_shop_config = classmethod(_get_shop_config)

    def _options(self):
        return ConfigurationSettings()

    options = property(fget=_options)

    def _base_url(self, secure=False):
        prefix = "http"
        if secure:
            prefix += "s"
        return prefix + "://" + url_join(settings.SHOP_BASE, self.site.domain)

    base_url = property(fget=_base_url)

    def __unicode__(self):
        return self.store_name

    class Admin:
        pass

    class Meta:
        verbose_name = _("Store Configuration")
        verbose_name_plural = _("Store Configurations")

class NullCart(object):
    """Standin for a real cart when we don't have one yet.  More convenient than testing for null all the time."""
    desc = None
    date_time_created = None
    customer = None
    total = Decimal("0")
    numItems = 0

    def add_item(self, *args, **kwargs):
        pass

    def remove_item(self, *args, **kwargs):
        pass

    def empty(self):
        pass

    def __str__(self):
        return "NullCart (empty)"

    def __iter__(self):
        return iter([])

    def __len__(self):
        return 0

class OrderCart(NullCart):
    """Allows us to fake a cart if we are reloading an order."""

    def __init__(self, order):
        self._order = order

    def _numItems(self):
        return self._order.orderitem_set.count()

    numItems = property(_numItems)

    def _cartitem_set(self):
        return self._order.orderitem_set

    cartitem_set = property(_cartitem_set)

    def _total(self):
        return self._order.balance

    total = property(_total)

    is_shippable = False

    def __str__(self):
        return "OrderCart (%i) = %i" % (self._order.id, len(self))

    def __len__(self):
        return self.numItems

class CartManager(models.Manager):

    def from_request(self, request, create=False, return_nullcart=True):
        """Get the current cart from the request"""
        cart = None
        try:
            contact = Contact.objects.from_request(request, create=False)
        except Contact.DoesNotExist:
            contact = None

        if 'cart' in request.session:
            cartid = request.session['cart']
            if cartid == "order":
                log.debug("Getting Order Cart from request")
                try:
                    order = Order.objects.from_request(request)
                    cart = OrderCart(order)
                except Order.DoesNotExist:
                    pass

            else:
                try:
                    cart = Cart.objects.get(id=cartid)
                except Cart.DoesNotExist:
                    log.debug('Removing invalid cart from session')
                    del request.session['cart']

        if isinstance(cart, NullCart) and not isinstance(cart, OrderCart) and contact is not None:
            carts = Cart.objects.filter(customer=contact)
            if carts.count() > 0:
                cart = carts[0]
                request.session['cart'] = cart.id

        if not cart:
            if create:
                if contact is None:
                    cart = Cart()
                else:
                    cart = Cart(customer=contact)
                cart.save()
                request.session['cart'] = cart.id

            elif return_nullcart:
                cart = NullCart()

            else:
                raise Cart.DoesNotExist()

        #log.debug("Cart: %s", cart)
        return cart


class Cart(models.Model):
    """
    Store items currently in a cart
    The desc isn't used but it is needed to make the admin interface work appropriately
    Could be used for debugging
    """
    desc = models.CharField(_("Description"), blank=True, null=True, max_length=10)
    date_time_created = models.DateTimeField(_("Creation Date"))
    customer = models.ForeignKey(Contact, blank=True, null=True, verbose_name=_('Customer'))

    objects = CartManager()

    def _get_count(self):
        itemCount = 0
        for item in self.cartitem_set.all():
            itemCount += item.quantity
        return (itemCount)
    numItems = property(_get_count)

    def _get_total(self):
        total = Decimal("0")
        for item in self.cartitem_set.all():
            total += item.line_total
        return(total)
    total = property(_get_total)

    def __iter__(self):
        return iter(self.cartitem_set.all())

    def __len__(self):
        return self.cartitem_set.count()

    def __unicode__(self):
        return u"Shopping Cart (%s)" % self.date_time_created

    def add_item(self, chosen_item, number_added, details={}):
        try:
            itemToModify =  self.cartitem_set.filter(product__id = chosen_item.id)[0]
            # Custom Products will not be added, they will each get their own line item
            #TODO: More sophisticated checks to make sure the options really are different
            if 'CustomProduct' in itemToModify.product.get_subtypes():
                itemToModify = CartItem(cart=self, product=chosen_item, quantity=0)
        except IndexError: #It doesn't exist so create a new one
            itemToModify = CartItem(cart=self, product=chosen_item, quantity=0)
        config=Config.get_shop_config()
        if config.no_stock_checkout == False:
            if chosen_item.items_in_stock < (itemToModify.quantity + number_added):
                return False

        itemToModify.quantity += number_added
        itemToModify.save()
        for data in details:
            itemToModify.add_detail(data)

        return True

    def remove_item(self, chosen_item_id, number_removed):
        itemToModify =  self.cartitem_set.get(id = chosen_item_id)
        itemToModify.quantity -= number_removed
        if itemToModify.quantity <= 0:
            itemToModify.delete()
        self.save()

    def empty(self):
        for item in self.cartitem_set.all():
            item.delete()
        self.save()

    def save(self):
        """Ensure we have a date_time_created before saving the first time."""
        if not self.pk:
            self.date_time_created = datetime.datetime.now()
        super(Cart, self).save()

    def _get_shippable(self):
        """Return whether the cart contains shippable items."""
        for cartitem in self.cartitem_set.all():
            if cartitem.product.is_shippable:
                return True
        return False
    is_shippable = property(_get_shippable)
    
    def get_shipment_list(self):
        """Return a list of shippable products, where each item is split into 
        multiple elements, one for each quantity."""
        items = []
        for cartitem in self.cartitem_set.all():
            p = cartitem.product
            if p.is_shippable:
                for single in range(0,cartitem.quantity):
                    items.append(p)
        return items

    class Admin:
        list_display = ('date_time_created','numItems','total')

    class Meta:
        verbose_name = _("Shopping Cart")
        verbose_name_plural = _("Shopping Carts")

class CartItem(models.Model):
    """
    An individual item in the cart
    """
    cart = models.ForeignKey(Cart, edit_inline=models.TABULAR, num_in_admin=3, verbose_name=_('Cart'))
    product = models.ForeignKey(Product, verbose_name=_('Product'))
    quantity = models.IntegerField(_("Quantity"), core=True)

    def _get_line_unitprice(self):
        # Get the qty discount price as the unit price for the line.
        line_price_delta = Decimal("0")
        qty_price = self.product.get_qty_price(self.quantity)
        if self.has_details:
            for detail in self.details.all():
                if detail.price_change and detail.value:
                    line_price_delta += detail.price_change
        return (qty_price + line_price_delta)
    unit_price = property(_get_line_unitprice)

    def _get_line_total(self):
        return self.unit_price * self.quantity
    line_total = property(_get_line_total)

    def _get_description(self):
        return self.product.translated_name()
    description = property(_get_description)

    def add_detail(self, data):
        detl = CartItemDetails(cartitem=self, name=data['name'], value=data['value'], sort_order=data['sort_order'], price_change=data['price_change'])
        detl.save()
        #self.details.add(detl)

    def _has_details(self):
        """
        Determine if this specific item has more detail
        """
        return (self.details.count() > 0)

    has_details = property(_has_details)

    def __unicode__(self):
        currency = config_value('SHOP', 'CURRENCY')
        currency = currency.replace("_", " ")
        return u'%s - %s %s%s' % (self.quantity, self.product.name,
            force_unicode(currency), self.line_total)

    class Admin:
        pass

    class Meta:
        verbose_name = _("Cart Item")
        verbose_name_plural = _("Cart Items")

class CartItemDetails(models.Model):
    """
    An arbitrary detail about a cart item.
    """
    cartitem = models.ForeignKey(CartItem, related_name='details', edit_inline=True, core=True)
    value = models.TextField(_('detail'))
    name = models.CharField(_('name'), max_length=100)
    price_change = models.DecimalField(_("Item Detail Price Change"), max_digits=6, decimal_places=2, blank=True, null=True)
    sort_order = models.IntegerField(_("Sort Order"),
        help_text=_("The display order for this group."))

    class Meta:
        ordering = ('sort_order',)
        verbose_name = _("Cart Item Detail")
        verbose_name_plural = _("Cart Item Details")
