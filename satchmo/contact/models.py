"""
Stores customer, organization, and order information.
"""
from decimal import Decimal
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core import urlresolvers
from django.db import models
from django.dispatch import dispatcher
from django.utils.translation import ugettext_lazy as _
from satchmo import tax
from satchmo.configuration import config_choice_values, config_value, SettingNotSet
from satchmo.discount.models import Discount, find_discount_for_code
from satchmo.payment.config import payment_choices
from satchmo.product.models import Product, DownloadableProduct
from satchmo.shop.signals import satchmo_cart_changed
from satchmo.shop.templatetags.satchmo_currency import moneyfmt
from satchmo.shop.utils import load_module
from signals import order_success, satchmo_contact_location_changed
import config
import datetime
import logging
import operator
import satchmo.shipping.config
import sys

try:
    from django.utils.safestring import mark_safe
except ImportError:
    mark_safe = lambda s:s

log = logging.getLogger('contact.views')

CONTACT_CHOICES = (
    ('Customer', _('Customer')),
    ('Supplier', _('Supplier')),
    ('Distributor', _('Distributor')),
)

ORGANIZATION_CHOICES = (
    ('Company', _('Company')),
    ('Government', _('Government')),
    ('Non-profit', _('Non-profit')),
)

ORGANIZATION_ROLE_CHOICES = (
    ('Supplier', _('Supplier')),
    ('Distributor', _('Distributor')),
    ('Manufacturer', _('Manufacturer')),
)

class Organization(models.Model):
    """
    An organization can be a company, government or any kind of group.
    """
    name = models.CharField(_("Name"), max_length=50, core=True)
    type = models.CharField(_("Type"), max_length=30,
        choices=ORGANIZATION_CHOICES)
    role = models.CharField(_("Role"), max_length=30,
        choices=ORGANIZATION_ROLE_CHOICES)
    create_date = models.DateField(_("Creation Date"))
    notes = models.TextField(_("Notes"), max_length=200, blank=True, null=True)

    def __unicode__(self):
        return self.name

    def save(self):
        """Ensure we have a create_date before saving the first time."""
        if not self.id:
            self.create_date = datetime.date.today()
        super(Organization, self).save()

    class Admin:
        list_filter = ['type', 'role']
        list_display = ['name', 'type', 'role']

    class Meta:
        verbose_name = _("Organization")
        verbose_name_plural = _("Organizations")

class ContactManager(models.Manager):

    def from_request(self, request, create=False):
        """Get the contact from the session, else look up using the logged-in
        user. Create an unsaved new contact if `create` is true.

        Returns:
        - Contact object or None
        """
        contact = None
        if request.session.get('custID'):
            try:
                contact = Contact.objects.get(id=request.session['custID'])
            except Contact.DoesNotExist:
                del request.session['custID']

        if contact is None and request.user.is_authenticated():
            try:
                contact = Contact.objects.get(user=request.user.id)
                request.session['custID'] = contact.id
            except Contact.DoesNotExist:
                pass
        else:
            # Don't create a Contact if the user isn't authenticated.
            create = False

        if contact is None:
            if create:
                contact = Contact(user=request.user)

            else:
                raise Contact.DoesNotExist()

        return contact


class Contact(models.Model):
    """
    A customer, supplier or any individual that a store owner might interact
    with.
    """
    first_name = models.CharField(_("First name"), max_length=30, core=True)
    last_name = models.CharField(_("Last name"), max_length=30, core=True)
    user = models.ForeignKey(User, unique=True, blank=True, null=True,
        edit_inline=models.TABULAR, num_in_admin=1, min_num_in_admin=1,
        max_num_in_admin=1, num_extra_on_change=0)
    role = models.CharField(_("Role"), max_length=20, blank=True, null=True,
        choices=CONTACT_CHOICES)
    organization = models.ForeignKey(Organization, verbose_name=_("Organization"), blank=True, null=True)
    dob = models.DateField(_("Date of birth"), blank=True, null=True)
    email = models.EmailField(_("Email"), blank=True)
    notes = models.TextField(_("Notes"), max_length=500, blank=True)
    create_date = models.DateField(_("Creation date"))

    objects = ContactManager()

    def _get_full_name(self):
        """Return the person's full name."""
        return u'%s %s' % (self.first_name, self.last_name)
    full_name = property(_get_full_name)

    def _shipping_address(self):
        """Return the default shipping address or None."""
        try:
            return self.addressbook_set.get(is_default_shipping=True)
        except AddressBook.DoesNotExist:
            return None
    shipping_address = property(_shipping_address)

    def _billing_address(self):
        """Return the default billing address or None."""
        try:
            return self.addressbook_set.get(is_default_billing=True)
        except AddressBook.DoesNotExist:
            return None
    billing_address = property(_billing_address)

    def _primary_phone(self):
        """Return the default phone number or None."""
        try:
            return self.phonenumber_set.get(primary=True)
        except PhoneNumber.DoesNotExist:
            return None
    primary_phone = property(_primary_phone)

    def __unicode__(self):
        return self.full_name

    def save(self):
        """Ensure we have a create_date before saving the first time."""
        if not self.id:
            self.create_date = datetime.date.today()
        # Validate the email is in synch between 
        if self.user and self.user.email != self.email:
            self.user.email = self.email
            self.user.save()
        super(Contact, self).save()

    class Admin:
        list_display = ('last_name', 'first_name', 'organization', 'role')
        list_filter = ['create_date', 'role', 'organization']
        ordering = ['last_name']

    class Meta:
        verbose_name = _("Contact")
        verbose_name_plural = _("Contacts")

PHONE_CHOICES = (
    ('Work', _('Work')),
    ('Home', _('Home')),
    ('Fax', _('Fax')),
    ('Mobile', _('Mobile')),
)

INTERACTION_CHOICES = (
    ('Email', _('Email')),
    ('Phone', _('Phone')),
    ('In Person', _('In Person')),
)

class Interaction(models.Model):
    """
    A type of activity with the customer.  Useful to track emails, phone calls,
    or in-person interactions.
    """
    contact = models.ForeignKey(Contact, verbose_name=_("Contact"))
    type = models.CharField(_("Type"), max_length=30,choices=INTERACTION_CHOICES)
    date_time = models.DateTimeField(_("Date and Time"), core=True)
    description = models.TextField(_("Description"), max_length=200)

    def __unicode__(self):
        return u'%s - %s' % (self.contact.full_name, self.type)

    class Admin:
        list_filter = ['type', 'date_time']

    class Meta:
        verbose_name = _("Interaction")
        verbose_name_plural = _("Interactions")

class PhoneNumber(models.Model):
    """
    Phone number associated with a contact.
    """
    contact = models.ForeignKey(Contact, edit_inline=models.TABULAR,
        num_in_admin=1)
    type = models.CharField(_("Description"), choices=PHONE_CHOICES,
        max_length=20, blank=True)
    phone = models.CharField(_("Phone Number"), blank=True, max_length=30,
        core=True)
    primary = models.BooleanField(_("Primary"), default=False)

    def __unicode__(self):
        return u'%s - %s' % (self.type, self.phone)

    def save(self):
        """
        If this number is the default, then make sure that it is the only
        primary phone number. If there is no existing default, then make
        this number the default.
        """
        existing_number = self.contact.primary_phone
        if existing_number:
            if self.primary:
                existing_number.primary = False
                super(PhoneNumber, existing_number).save()
        else:
            self.primary = True
        super(PhoneNumber, self).save()

    class Meta:
        ordering = ['-primary']
        verbose_name = _("Phone Number")
        verbose_name_plural = _("Phone Numbers")

class AddressBook(models.Model):
    """
    Address information associated with a contact.
    """
    contact = models.ForeignKey(Contact,
        edit_inline=models.STACKED, num_in_admin=1)
    description = models.CharField(_("Description"), max_length=20, blank=True,
        help_text=_('Description of address - Home, Office, Warehouse, etc.',))
    street1 = models.CharField(_("Street"), core=True, max_length=50)
    street2 = models.CharField(_("Street"), max_length=50, blank=True)
    state = models.CharField(_("State"), max_length=50, blank=True)
    city = models.CharField(_("City"), max_length=50)
    postal_code = models.CharField(_("Zip Code"), max_length=10)
    country = models.CharField(_("Country"), max_length=50, blank=True)
    is_default_shipping = models.BooleanField(_("Default Shipping Address"),
        default=False)
    is_default_billing = models.BooleanField(_("Default Billing Address"),
        default=False)

    def __unicode__(self):
       return u'%s - %s' % (self.contact.full_name, self.description)

    def save(self):
        """
        If this address is the default billing or shipping address, then
        remove the old address's default status. If there is no existing
        default, then make this address the default.
        """
        existing_billing = self.contact.billing_address
        if existing_billing:
            if self.is_default_billing:
                existing_billing.is_default_billing = False
                super(AddressBook, existing_billing).save()
        else:
            self.is_default_billing = True

        existing_shipping = self.contact.shipping_address
        if existing_shipping:
            if self.is_default_shipping:
                existing_shipping.is_default_shipping = False
                super(AddressBook, existing_shipping).save()
        else:
            self.is_default_shipping = True

        super(AddressBook, self).save()

    class Meta:
        verbose_name = _("Address Book")
        verbose_name_plural = _("Address Books")

ORDER_CHOICES = (
    ('Online', _('Online')),
    ('In Person', _('In Person')),
    ('Show', _('Show')),
)

ORDER_STATUS = (
    ('Temp', _('Temp')),
    ('Pending', _('Pending')),
    ('In Process', _('In Process')),
    ('Billed', _('Billed')),
    ('Shipped', _('Shipped')),
)

class OrderManager(models.Manager):
    def from_request(self, request):
        """Get the order from the session

        Returns:
        - Order object or None
        """
        order = None
        if 'orderID' in request.session:
            try:
                order = Order.objects.get(id=request.session['orderID'])
                # TODO: Validate against logged-in user.
            except Order.DoesNotExist:
                pass

            if not order:
                del request.session['orderID']

        if not order:
            raise Order.DoesNotExist()

        return order
        
    def remove_partial_order(self, request):
        """Delete cart from request if it exists and is incomplete (has no status)"""
        try:
            order = Order.objects.from_request(request)
            if not order.status:
                del request.session['orderID']
                log.info("Deleting incomplete order #%i from database", order.id)
                order.delete()
                return True
        except Order.DoesNotExist:
            pass
        return False

class Order(models.Model):
    """
    Orders contain a copy of all the information at the time the order was
    placed.
    """
    contact = models.ForeignKey(Contact, verbose_name=_('Contact'))
    ship_street1 = models.CharField(_("Street"), max_length=50, blank=True)
    ship_street2 = models.CharField(_("Street"), max_length=50, blank=True)
    ship_city = models.CharField(_("City"), max_length=50, blank=True)
    ship_state = models.CharField(_("State"), max_length=50, blank=True)
    ship_postal_code = models.CharField(_("Zip Code"), max_length=10, blank=True)
    ship_country = models.CharField(_("Country"), max_length=50, blank=True)
    bill_street1 = models.CharField(_("Street"), max_length=50, blank=True)
    bill_street2 = models.CharField(_("Street"), max_length=50, blank=True)
    bill_city = models.CharField(_("City"), max_length=50, blank=True)
    bill_state = models.CharField(_("State"), max_length=50, blank=True)
    bill_postal_code = models.CharField(_("Zip Code"), max_length=10, blank=True)
    bill_country = models.CharField(_("Country"), max_length=50, blank=True)
    notes = models.TextField(_("Notes"), max_length=100, blank=True, null=True)
    sub_total = models.DecimalField(_("Subtotal"),
        max_digits=18, decimal_places=10, blank=True, null=True)
    total = models.DecimalField(_("Total"),
        max_digits=18, decimal_places=10, blank=True, null=True)
    discount_code = models.CharField(_("Discount Code"), max_length=20, blank=True, null=True,
        help_text=_("Coupon Code"))
    discount = models.DecimalField(_("Discount amount"),
        max_digits=18, decimal_places=10, blank=True, null=True)
    method = models.CharField(_("Order method"),
        choices=ORDER_CHOICES, max_length=50, blank=True)
    shipping_description = models.CharField(_("Shipping Description"),
        max_length=50, blank=True, null=True)
    shipping_method = models.CharField(_("Shipping Method"),
        max_length=50, blank=True, null=True)
    shipping_model = models.CharField(_("Shipping Models"),
        choices=config_choice_values('SHIPPING','MODULES'), max_length=30, blank=True, null=True)
    shipping_cost = models.DecimalField(_("Shipping Cost"),
        max_digits=18, decimal_places=10, blank=True, null=True)
    shipping_discount = models.DecimalField(_("Shipping Discount"),
        max_digits=18, decimal_places=10, blank=True, null=True)
    tax = models.DecimalField(_("Tax"),
        max_digits=18, decimal_places=10, blank=True, null=True)
    timestamp = models.DateTimeField(_("Timestamp"), blank=True, null=True)
    status = models.CharField(_("Status"), max_length=20, choices=ORDER_STATUS,
        core=True, blank=True, help_text=_("This is set automatically."))

    objects = OrderManager()

    def __unicode__(self):
        return "Order #%s: %s" % (self.id, self.contact.full_name)

    def add_status(self, status=None, notes=None):
        orderstatus = OrderStatus()
        if not status:
            if self.orderstatus_set.count() > 0:
                curr_status = self.orderstatus_set.all().order_by('-timestamp')[0]
                status = curr_status.status
            else:
                status = 'Pending'

        orderstatus.status = status
        orderstatus.notes = notes
        orderstatus.timestamp = datetime.datetime.now()
        orderstatus.order = self
        orderstatus.save()

    def add_variable(self, key, value):
        """Add an OrderVariable, used for misc stuff that is just too small to get its own field"""
        try:
            v = self.variables.get(key__exact=key)
            v.value = value
        except OrderVariable.DoesNotExist:
            v = OrderVariable(order=self, key=key, value=value)
        v.save()

    def get_variable(self, key, default=None):
        qry = self.variables.filter(key__exact=key)
        ct = qry.count()
        if ct == 0:
            return default
        else:
            return qry[0]

    def copy_addresses(self):
        """
        Copy the addresses so we know what the information was at time of order.
        """
        shipaddress = self.contact.shipping_address
        billaddress = self.contact.billing_address
        self.ship_street1 = shipaddress.street1
        self.ship_street2 = shipaddress.street2
        self.ship_city = shipaddress.city
        self.ship_state = shipaddress.state
        self.ship_postal_code = shipaddress.postal_code
        self.ship_country = shipaddress.country
        self.bill_street1 = billaddress.street1
        self.bill_street2 = billaddress.street2
        self.bill_city = billaddress.city
        self.bill_state = billaddress.state
        self.bill_postal_code = billaddress.postal_code
        self.bill_country = billaddress.country

    def remove_all_items(self):
        """Delete all items belonging to this order."""
        for item in self.orderitem_set.all():
            item.delete()
        self.save()

    def _balance(self):
        return self.total-self.balance_paid

    balance = property(fget=_balance)

    def balance_forward(self):
        return moneyfmt(self.balance)

    balance_forward = property(fget=balance_forward)

    def _balance_paid(self):
        payments = [p.amount for p in self.payments.all()]
        if payments:
            return reduce(operator.add, payments)
        else:
            return Decimal("0.0000000000")

    balance_paid = property(_balance_paid)

    def _credit_card(self):
        """Return the credit card associated with this payment."""
        for payment in self.payments.order_by('-timestamp'):
            try:
                if payment.creditcards.count() > 0:
                    return payment.creditcards.get()
            except payments.creditcards.model.DoesNotExist:
                pass
        return None
    credit_card = property(_credit_card)


    def _full_bill_street(self, delim="<br/>"):
        """Return both billing street entries separated by delim."""
        if self.bill_street2:
            return self.bill_street1 + delim + self.bill_street2
        else:
            return self.bill_street1
    full_bill_street = property(_full_bill_street)

    def _full_ship_street(self, delim="<br/>"):
        """Return both shipping street entries separated by delim."""
        if self.ship_street2:
            return self.ship_street1 + delim + self.ship_street2
        else:
            return self.ship_street1
    full_ship_street = property(_full_ship_street)

    def _get_balance_remaining_url(self):
        return ('satchmo_balance_remaining_order', None, {'order_id' : self.id})
    get_balance_remaining_url = models.permalink(_get_balance_remaining_url)

    def _partially_paid(self):
        return self.balance_paid > Decimal("0.0000000000")

    partially_paid = property(_partially_paid)

    def payments_completed(self):
        q = self.payments.exclude(transaction_id__isnull = False, transaction_id = "PENDING")
        return q.exclude(amount=Decimal("0.0000000000"))

    def save(self):
        """
        Copy addresses from contact. If the order has just been created, set
        the create_date.
        """
        if not self.id:
            self.timestamp = datetime.datetime.now()

        self.copy_addresses()
        super(Order, self).save() # Call the "real" save() method.

    def invoice(self):
        return mark_safe('<a href="/admin/print/invoice/%s/">View</a>' % self.id)
    invoice.allow_tags = True

    def _item_discount(self):
        """Get the discount of just the items, less the shipping discount."""
        return self.discount-self.shipping_discount
    item_discount = property(_item_discount)

    def packingslip(self):
        return mark_safe('<a href="/admin/print/packingslip/%s/">View</a>' % self.id)
    packingslip.allow_tags = True

    def recalculate_total(self, save=True):
        """Calculates sub_total, taxes and total."""
        zero = Decimal("0.0000000000")
        discount = find_discount_for_code(self.discount_code)
        discount.calc(self)
        self.discount = discount.total
        discounts = discount.item_discounts
        itemprices = []
        fullprices = []
        for lineitem in self.orderitem_set.all():
            lid = lineitem.id
            if lid in discounts:
                lineitem.discount = discounts[lid]
            else:
                lineitem.discount = zero
            if save:
                lineitem.save()

            itemprices.append(lineitem.sub_total)
            fullprices.append(lineitem.line_item_price)

        if 'Shipping' in discounts:
            self.shipping_discount = discounts['Shipping']
        else:
            self.shipping_discount = zero

        if itemprices:
            item_sub_total = reduce(operator.add, itemprices)
        else:
            item_sub_total = zero

        if fullprices:
            full_sub_total = reduce(operator.add, fullprices)
        else:
            full_sub_total = zero


        self.sub_total = full_sub_total

        taxProcessor = tax.get_processor(self)
        totaltax, taxrates = taxProcessor.process()
        self.tax = totaltax

        # clear old taxes
        for taxdetl in self.taxes.all():
            taxdetl.delete()

        for taxdesc, taxamt in taxrates.items():
            taxdetl = OrderTaxDetail(order=self, tax=taxamt, description=taxdesc, method=taxProcessor.method)
            taxdetl.save()

        log.debug("recalc: sub_total=%s, shipping=%s, discount=%s, tax=%s",
                item_sub_total, self.shipping_sub_total, self.discount, self.tax)

        self.total = item_sub_total + self.shipping_sub_total + self.tax

        if save:
            self.save()

    def shippinglabel(self):
        return mark_safe('<a href="/admin/print/shippinglabel/%s/">View</a>' % self.id)
    shippinglabel.allow_tags = True

    def _order_total(self):
        #Needed for the admin list display
        return moneyfmt(self.total)
    order_total = property(_order_total)

    def order_success(self):
        """Run each item's order_success method."""
        log.debug("Order success: %s", self)
        for orderitem in self.orderitem_set.all():
            subtype = orderitem.product.get_subtype_with_attr('order_success')
            if subtype:
                subtype.order_success(self, orderitem)
        dispatcher.send(signal=order_success, sender=self.__class__, instance=self)


    def _paid_in_full(self):
        """True if total has been paid"""
        return self.balance <= 0
    paid_in_full = property(fget=_paid_in_full)

    def _has_downloads(self):
        """Determine if there are any downloadable products on this order"""
        if self.downloadlink_set.count() > 0:
            return True
        return False
    has_downloads = property(_has_downloads)

    def _is_shippable(self):
        """Determine if we will be shipping any items on this order """
        for orderitem in self.orderitem_set.all():
            if orderitem.product.is_shippable:
                return True
        return False
    is_shippable = property(_is_shippable)

    def _shipping_sub_total(self):
        return self.shipping_cost-self.shipping_discount
    shipping_sub_total = property(_shipping_sub_total)
    
    def _shipping_tax(self):
        rates = self.taxes.filter(description__iexact = 'shipping')
        if rates.count()>0:
            tax = reduce(operator.add, [t.tax for t in rates])
        else:
            tax = Decimal("0.0000000000")
        return tax
    shipping_tax = property(_shipping_tax)

    def _shipping_with_tax(self):
        return self.shipping_sub_total + self.shipping_tax
    shipping_with_tax = property(_shipping_with_tax)

    def sub_total_with_tax(self):
        return reduce(operator.add, [o.total_with_tax for o in self.orderitem_set.all()])

    def validate(self, request):
        """
        Return whether the order is valid.
        Not guaranteed to be side-effect free.
        """
        valid = True
        for orderitem in self.orderitem_set.all():
            for subtype_name in orderitem.product.get_subtypes():
                subtype = getattr(orderitem.product, subtype_name.lower())
                validate_method = getattr(subtype, 'validate_order', None)
                if validate_method:
                    valid = valid and validate_method(request, self, orderitem)
        return valid

    class Admin:
        fields = (
            (None, {'fields': ('contact', 'method', 'status', 'notes')}),
            (_('Shipping Method'), {'fields':
                ('shipping_method', 'shipping_description')}),
            (_('Shipping Address'), {'classes': 'collapse', 'fields':
                ('ship_street1', 'ship_street2', 'ship_city', 'ship_state',
                'ship_postal_code', 'ship_country')}),
            (_('Billing Address'), {'classes': 'collapse', 'fields':
                ('bill_street1', 'bill_street2', 'bill_city', 'bill_state',
                'bill_postal_code', 'bill_country')}),
            (_('Totals'), {'fields':
                ('sub_total', 'shipping_cost', 'shipping_discount', 'tax', 'discount', 'total',
                'timestamp')}))
        list_display = ('contact', 'timestamp', 'order_total', 'balance_forward', 'status',
            'invoice', 'packingslip', 'shippinglabel')
        list_filter = ['timestamp', 'contact']
        date_hierarchy = 'timestamp'

    class Meta:
        verbose_name = _("Product Order")
        verbose_name_plural = _("Product Orders")

class OrderItem(models.Model):
    """
    A line item on an order.
    """
    order = models.ForeignKey(Order, verbose_name=_("Order"), edit_inline=models.TABULAR, num_in_admin=3)
    product = models.ForeignKey(Product, verbose_name=_("Product"))
    quantity = models.IntegerField(_("Quantity"), core=True)
    unit_price = models.DecimalField(_("Unit price"),
        max_digits=18, decimal_places=10)
    unit_tax = models.DecimalField(_("Unit tax"),
        max_digits=18, decimal_places=10, null=True)
    line_item_price = models.DecimalField(_("Line item price"),
        max_digits=18, decimal_places=10)
    tax = models.DecimalField(_("Line item tax"),
        max_digits=18, decimal_places=10, null=True)
    discount = models.DecimalField(_("Line item discount"),
        max_digits=18, decimal_places=10, blank=True, null=True)
        
    def __init__(self, *args, **kwargs):
        super(OrderItem, self).__init__(*args, **kwargs)
        self.update_tax()

    def __unicode__(self):
        return self.product.translated_name()

    def _get_category(self):
        return(self.product.get_category.translated_name())
    category = property(_get_category)

    def _sub_total(self):
        if self.discount:
            return self.line_item_price-self.discount
        else:
            return self.line_item_price
    sub_total = property(_sub_total)

    def _total_with_tax(self):
        return self.sub_total + self.tax
    total_with_tax = property(_total_with_tax)

    def _unit_price_with_tax(self):
        return self.unit_price + self.unit_tax
    unit_price_with_tax = property(_unit_price_with_tax)

    def update_tax(self):
        taxclass = self.product.taxClass
        processor = tax.get_processor(order=self.order)
        self.unit_tax = processor.by_price(taxclass, self.unit_price)
        self.tax = processor.by_orderitem(self)

    class Meta:
        verbose_name = _("Order Line Item")
        verbose_name_plural = _("Order Line Items")

class OrderItemDetail(models.Model):
    """
    Name, value pair and price delta associated with a specific item in an order
    """
    item = models.ForeignKey(OrderItem, verbose_name=_("Order Item"), edit_inline=models.TABULAR, core=True, num_in_admin=3)
    name = models.CharField(_('Name'), max_length=100)
    value = models.CharField(_('Value'), max_length=255)
    price_change = models.DecimalField(_("Price Change"), max_digits=18, decimal_places=10, blank=True, null=True)
    sort_order = models.IntegerField(_("Sort Order"),
        help_text=_("The display order for this group."))

    def __unicode__(self):
        return u"%s - %s,%s" % (self.item, self.name, self.value)

    class Meta:
        verbose_name = _("Order Item Detail")
        verbose_name_plural = _("Order Item Details")
        ordering = ('sort_order',)

class DownloadLink(models.Model):
    downloadable_product = models.OneToOneField(DownloadableProduct, verbose_name=_('Downloadable product'))
    order = models.ForeignKey(Order, verbose_name=_('Order'))
    key = models.CharField(_('Key'), max_length=40)
    num_attempts = models.IntegerField(_('Number of attempts'), )
    time_stamp = models.DateTimeField(_('Time stamp'), )
    active = models.BooleanField(_('Active'), default=True)

    def is_valid(self):
        # Check num attempts and expire_minutes
        if not self.downloadable_product.active:
            return (False, _("This download is no longer active"))
        if self.num_attempts > self.downloadable_product.num_allowed_downloads:
            return (False, _("You have exceeded the number of allowed downloads."))
        expire_time = datetime.timedelta(minutes=self.downloadable_product.expire_minutes) + self.time_stamp
        if datetime.datetime.now() > expire_time:
            return (False, _("This download link has expired."))
        return (True, "")

    def get_absolute_url(self):
        return('satchmo.shop.views.download.process', (), { 'download_key': self.key})
    get_absolute_url = models.permalink(get_absolute_url)

    def get_full_url(self):
        url = urlresolvers.reverse('satchmo_download_process', kwargs= {'download_key': self.key})
        return('http://%s%s' % (Site.objects.get_current(), url))

    def save(self):
        """
       Set the initial time stamp
        """
        if self.time_stamp is None:
            self.time_stamp = datetime.datetime.now()
        super(DownloadLink, self).save()

    def __unicode__(self):
        return u"%s - %s" % (self.downloadable_product.product.slug, self.time_stamp)

    def _product_name(self):
        return u"%s" % (self.downloadable_product.product.translated_name)
    product_name=property(_product_name)

    class Admin:
        pass

    class Meta:
        verbose_name = _("Download Link")
        verbose_name_plural = _("Download Links")

class OrderStatus(models.Model):
    """
    An order will have multiple statuses as it moves its way through processing.
    """
    order = models.ForeignKey(Order, verbose_name=_("Order"), edit_inline=models.STACKED, num_in_admin=1)
    status = models.CharField(_("Status"),
        max_length=20, choices=ORDER_STATUS, core=True, blank=True)
    notes = models.CharField(_("Notes"), max_length=100, blank=True)
    timestamp = models.DateTimeField(_("Timestamp"))

    def __unicode__(self):
        return self.status

    def save(self):
        super(OrderStatus, self).save()
        self.order.status = self.status
        self.order.save()

    class Meta:
        verbose_name = _("Order Status")
        verbose_name_plural = _("Order Statuses")

class OrderPayment(models.Model):
    order = models.ForeignKey(Order, related_name="payments")
    payment = models.CharField(_("Payment Method"),
        choices=payment_choices(), max_length=25, blank=True)
    amount = models.DecimalField(_("amount"), core=True,
        max_digits=18, decimal_places=10, blank=True, null=True)
    timestamp = models.DateTimeField(_("timestamp"), blank=True, null=True)
    transaction_id = models.CharField(_("Transaction ID"), max_length=25, blank=True, null=True)

    def _credit_card(self):
        """Return the credit card associated with this payment."""
        try:
            return self.creditcards.get()
        except self.creditcards.model.DoesNotExist:
            return None
    credit_card = property(_credit_card)

    def _amount_total(self):
        return moneyfmt(self.amount)

    amount_total = property(fget=_amount_total)

    def __unicode__(self):
        if self.id is not None:
            return u"Order payment #%i" % self.id
        else:
            return u"Order payment (unsaved)"

    def save(self):
        if not self.id:
            self.timestamp = datetime.datetime.now()

        super(OrderPayment, self).save()

    class Admin:
        list_filter = ['order', 'payment']
        list_display = ['id', 'order', 'payment', 'amount_total', 'timestamp']
        fields = (
            (None, {'fields': ('order', 'payment', 'amount', 'timestamp')}),
            )

    class Meta:
        verbose_name = _("Order Payment")
        verbose_name_plural = _("Order Payments")

class OrderVariable(models.Model):
    order = models.ForeignKey(Order, edit_inline=models.TABULAR, num_in_admin=1, related_name="variables")
    key = models.SlugField(_('key'), core=True)
    value = models.CharField(_('value'), core=True, max_length=100)

    class Meta:
        ordering=('key',)
        verbose_name = _("Order variable")
        verbose_name_plural = _("Order variables")

    def __unicode__(self):
        if len(self.value)>10:
            v = self.value[:10] + '...'
        else:
            v = self.value
        return u"OrderVariable: %s=%s" % (self.key, v)

class OrderTaxDetail(models.Model):
    """A tax line item"""
    order = models.ForeignKey(Order, edit_inline=models.TABULAR, num_in_admin=1, related_name="taxes")
    method = models.CharField(_("Model"), max_length=50, core=True)
    description = models.CharField(_("Description"), max_length=50, blank=True)
    tax = models.DecimalField(_("Tax"), core=True,
        max_digits=18, decimal_places=10, blank=True, null=True)

    def __unicode__(self):
        if self.description:
            return u"Tax: %s %s" % (self.description, self.tax)
        else:
            return u"Tax: %s" % self.tax

    class Meta:
        verbose_name = _('Order tax detail')
        verbose_name_plural = _('Order tax details')

def _remove_order_on_cart_update(request=None, cart=None):
    if request:
        log.debug("caught cart changed signal - remove_order_on_cart_update")
        Order.objects.remove_partial_order(request)
        
def _recalc_total_on_contact_change(contact=None):
    #TODO: pull just the current order once we start using threadlocal middleware
    log.debug("Recalculating all contact orders not in process")
    orders = Order.objects.filter(contact=contact, status="")
    log.debug("Found %i orders to recalc", orders.count())
    for order in orders:
        order.copy_addresses()
        order.recalculate_total()
    
dispatcher.connect(_remove_order_on_cart_update, signal=satchmo_cart_changed)
dispatcher.connect(_recalc_total_on_contact_change, signal=satchmo_contact_location_changed)
