from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from product.admin import ProductOptions
from satchmo_ext.brand.models import Brand, BrandTranslation, BrandCategory, BrandCategoryTranslation, BrandProduct, BrandCategoryProduct
from product.models import Product
from satchmo_utils.thumbnail.field import ImageWithThumbnailField
from satchmo_utils.thumbnail.widgets import AdminImageWithThumbnailWidget

class BrandTranslation_Inline(admin.StackedInline):
    model = BrandTranslation
    extra = 1
    verbose_name = _("Translation")
    verbose_name_plural = _("Translations")
    
    formfield_overrides = {
        ImageWithThumbnailField : {'widget' : AdminImageWithThumbnailWidget},
    }
    

class BrandCategoryTranslation_Inline(admin.StackedInline):
    model = BrandCategoryTranslation
    extra = 1
    verbose_name = _("Translation")
    verbose_name_plural = _("Translations")

    formfield_overrides = {
        ImageWithThumbnailField : {'widget' : AdminImageWithThumbnailWidget},
    }

class BrandCategoryTranslationOptions(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields' : ('brandcategory', 'languagecode', 'name', 'description', 'picture')}),
    )

class BrandOptions(admin.ModelAdmin):
    inlines = [BrandTranslation_Inline]

    
class BrandProductInline(admin.TabularInline):
    model = BrandProduct
    max_num = 1
    verbose_name = _("Brand")
    verbose_name_plural = _("Brands")
    

class BrandTranslationOptions(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields' : ('brand', 'languagecode', 'name', 'description', 'picture')}),
    )

class BrandCategoryOptions(admin.ModelAdmin):
    inlines = [BrandCategoryTranslation_Inline]


class BrandCategoryInline(admin.TabularInline):
    model = BrandCategoryProduct
    extra = 1
    verbose_name = _("Brand Category")
    verbose_name_plural = _("Brand Categories")

admin.site.register(Brand, BrandOptions)
admin.site.register(BrandCategory, BrandCategoryOptions)
admin.site.unregister(Product)
ProductOptions.inlines.append(BrandProductInline)
ProductOptions.inlines.append(BrandCategoryInline)
admin.site.register(Product, ProductOptions)
