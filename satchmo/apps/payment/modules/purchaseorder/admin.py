from payment.modules.purchaseorder.models import PurchaseOrder
from django.contrib import admin

class PurchaseOrderOptions(admin.ModelAdmin):
    list_display = ('po_number', 'balance_due', 'order_link')

admin.site.register(PurchaseOrder, PurchaseOrderOptions)


