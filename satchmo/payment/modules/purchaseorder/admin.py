from satchmo.payment.modules.purchaseorder.models import PurchaseOrder
from django.contrib import admin

class PurchaseOrderOptions(admin.ModelAdmin):
    list_display = ('po_number', 'order_link')

admin.site.register(PurchaseOrder, PurchaseOrderOptions)


