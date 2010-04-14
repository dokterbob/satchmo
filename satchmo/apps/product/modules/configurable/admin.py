from django.contrib import admin
from product.modules.configurable.models import ConfigurableProduct, ProductVariation

class ProductVariationOptions(admin.ModelAdmin):
    filter_horizontal = ('options',)

admin.site.register(ConfigurableProduct)
admin.site.register(ProductVariation, ProductVariationOptions)


