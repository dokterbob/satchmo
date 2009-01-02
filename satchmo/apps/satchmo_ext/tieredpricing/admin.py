from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from product.admin import ProductOptions
from product.models import Product
from satchmo_ext.tieredpricing.models import TieredPrice, PricingTier
from product.admin import Price_Inline

class TieredPriceInline(admin.TabularInline):
    model = TieredPrice
    extra = 2
    verbose_name = _("Tiered Price")
    verbose_name_plural = _("Tiered Prices")    


class PricingTierOptions(admin.ModelAdmin):
    pass

admin.site.register(PricingTier, PricingTierOptions)
admin.site.unregister(Product)
ix = 0
while ix < len(ProductOptions.inlines):
    if ProductOptions.inlines[ix] == Price_Inline:
        ProductOptions.inlines.insert(ix+1, TieredPriceInline)
    ix += 1
    
admin.site.register(Product, ProductOptions)
