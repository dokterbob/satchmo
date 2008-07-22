from satchmo.contact.models import Organization, Contact, Interaction, PhoneNumber, AddressBook, Order, OrderItem, OrderItemDetail, DownloadLink, OrderStatus, OrderPayment, OrderVariable, OrderTaxDetail
from django.contrib import admin
from django.utils.translation import get_language, ugettext_lazy as _

class Contact_Inline(admin.TabularInline):
    model = Contact
    extra = 1

class PhoneNumber_Inline(admin.TabularInline):
    model = PhoneNumber
    extra = 1

class AddressBook_Inline(admin.StackedInline):
    model = AddressBook
    extra = 1

class OrderItem_Inline(admin.TabularInline):
    model = OrderItem
    extra = 3

class OrderItemDetail_Inline(admin.TabularInline):
    model = OrderItemDetail
    extra = 3

class OrderStatus_Inline(admin.StackedInline):
    model = OrderStatus
    extra = 1

class OrderVariable_Inline(admin.TabularInline):
    model = OrderVariable
    extra = 1

class OrderTaxDetail_Inline(admin.TabularInline):
    model = OrderTaxDetail
    extra = 1

class OrganizationOptions(admin.ModelAdmin):
    list_filter = ['type', 'role']
    list_display = ['name', 'type', 'role']

class ContactOptions(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'organization', 'role')
    list_filter = ['create_date', 'role', 'organization']
    ordering = ['last_name']
    inlines = [PhoneNumber_Inline, AddressBook_Inline]

class InteractionOptions(admin.ModelAdmin):
    list_filter = ['type', 'date_time']

class OrderOptions(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('contact', 'method', 'status', 'discount_code', 'notes')}), (_('Shipping Method'), {'fields':
            ('shipping_method', 'shipping_description')}), (_('Shipping Address'), {'classes': ('collapse',), 'fields':
            ('ship_street1', 'ship_street2', 'ship_city', 'ship_state', 'ship_postal_code', 'ship_country')}), (_('Billing Address'), {'classes': ('collapse',), 'fields':
            ('bill_street1', 'bill_street2', 'bill_city', 'bill_state', 'bill_postal_code', 'bill_country')}), (_('Totals'), {'fields':
            ('sub_total', 'shipping_cost', 'shipping_discount', 'tax', 'discount', 'total', 'timestamp')}))
    list_display = ('contact', 'timestamp', 'order_total', 'balance_forward', 'status', 'invoice', 'packingslip', 'shippinglabel')
    list_filter = ['timestamp', 'contact', 'status']
    date_hierarchy = 'timestamp'
    inlines = [OrderItem_Inline, OrderStatus_Inline, OrderVariable_Inline, OrderTaxDetail_Inline]

class OrderItemOptions(admin.ModelAdmin):
    inlines = [OrderItemDetail_Inline]

class OrderPaymentOptions(admin.ModelAdmin):
    list_filter = ['order', 'payment']
    list_display = ['id', 'order', 'payment', 'amount_total', 'timestamp']
    fieldsets = (
        (None, {'fields': ('order', 'payment', 'amount', 'timestamp')}), )

admin.site.register(Organization, OrganizationOptions)
admin.site.register(Contact, ContactOptions)
admin.site.register(Interaction, InteractionOptions)
admin.site.register(Order, OrderOptions)
admin.site.register(OrderItem, OrderItemOptions)
admin.site.register(DownloadLink)
admin.site.register(OrderPayment, OrderPaymentOptions)

