from satchmo_store.contact.supplier.models import RawItem, SupplierOrder, SupplierOrderItem, SupplierOrderStatus
from django.contrib import admin
from django.utils.translation import get_language, ugettext_lazy as _


class SupplierOrderItem_Inline(admin.TabularInline):
    model = SupplierOrderItem
    extra = 3

class SupplierOrderStatus_Inline(admin.StackedInline):
    model = SupplierOrderStatus
    extra = 1

class RawItemOptions(admin.ModelAdmin):
    list_display = ('supplier','description','supplier_num','inventory',)
    list_filter = ('supplier',)

class SupplierOrderOptions(admin.ModelAdmin):
    list_display = ('supplier','date_created', 'order_total','status')
    list_filter = ('date_created','supplier',)
    date_hierarchy = 'date_created'
    inlines = [SupplierOrderItem_Inline, SupplierOrderStatus_Inline]

admin.site.register(RawItem, RawItemOptions)
admin.site.register(SupplierOrder, SupplierOrderOptions)

