from shipping.modules.productshipping.models import Carrier, CarrierTranslation, ProductShippingPrice
from product.models import Product
from product.admin import ProductOptions
from django.contrib import admin
from django.utils.translation import get_language, ugettext_lazy as _

class CarrierTranslation_Inline(admin.TabularInline):
    model = CarrierTranslation
    ordering = ('carrier',)
    extra = 1

class CarrierOptions(admin.ModelAdmin):
    ordering = ('key',)
    inlines = [CarrierTranslation_Inline]

class ProductShippingPriceInline(admin.TabularInline):
    model = ProductShippingPrice

admin.site.register(Carrier, CarrierOptions)
admin.site.unregister(Product)
ProductOptions.inlines.append(ProductShippingPriceInline)
admin.site.register(Product, ProductOptions)

