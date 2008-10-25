from satchmo.payment.modules.purchaseorder.models import PurchaseOrder
from django.contrib import admin

class PurchaseOrderOptions(admin.ModelAdmin):
    pass

admin.site.register(PurchaseOrder, PurchaseOrderOptions)


