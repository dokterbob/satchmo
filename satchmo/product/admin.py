from satchmo.product.models import Category, CategoryTranslation, CategoryImage, CategoryImageTranslation, OptionGroup, OptionGroupTranslation, Option, OptionTranslation, Product, CustomProduct, CustomTextField, CustomTextFieldTranslation, ConfigurableProduct, DownloadableProduct, SubscriptionProduct, Trial, ProductVariation, ProductAttribute, Price, ProductImage, ProductImageTranslation
from django.contrib import admin
from django.utils.translation import get_language, ugettext_lazy as _


class CategoryTranslation_Inline(admin.StackedInline):
    model = CategoryTranslation
    extra = 1

class CategoryImage_Inline(admin.TabularInline):
    model = CategoryImage
    extra = 3

class CategoryImageTranslation_Inline(admin.StackedInline):
    model = CategoryImageTranslation
    extra = 1

class OptionGroupTranslation_Inline(admin.StackedInline):
    model = OptionGroupTranslation
    extra = 1

class Option_Inline(admin.TabularInline):
    model = Option
    extra = 5

class OptionTranslation_Inline(admin.StackedInline):
    model = OptionTranslation
    extra = 1

class CustomTextField_Inline(admin.TabularInline):
    model = CustomTextField
    extra = 3

class CustomTextFieldTranslation_Inline(admin.StackedInline):
    model = CustomTextFieldTranslation
    extra = 1

class Trial_Inline(admin.StackedInline):
    model = Trial
    extra = 2

class ProductAttribute_Inline(admin.TabularInline):
    model = ProductAttribute
    extra = 1

class Price_Inline(admin.TabularInline):
    model = Price
    extra = 2

class ProductImage_Inline(admin.StackedInline):
    model = ProductImage
    extra = 3

class ProductImageTranslation_Inline(admin.StackedInline):
    model = ProductImageTranslation
    extra = 1

class CategoryOptions(admin.ModelAdmin):
    list_display = ('name', '_parents_repr')
    ordering = ['parent__id', 'ordering', 'name']
    inlines = [CategoryTranslation_Inline, CategoryImage_Inline]

class CategoryImageOptions(admin.ModelAdmin):
    inlines = [CategoryImageTranslation_Inline]

class OptionGroupOptions(admin.ModelAdmin):
    inlines = [OptionGroupTranslation_Inline, Option_Inline]

class OptionOptions(admin.ModelAdmin):
    inlines = [OptionTranslation_Inline]

class ProductOptions(admin.ModelAdmin):
    list_display = ('slug', 'sku', 'name', 'unit_price', 'items_in_stock', 'get_subtypes')
    list_filter = ('category', 'date_added')
    fieldsets = (
    (None, {'fields': ('category', 'name', 'slug', 'sku', 'description', 'short_description', 'date_added', 'active', 'featured', 'items_in_stock','total_sold','ordering')}), (_('Meta Data'), {'fields': ('meta',), 'classes': ('collapse',)}), (_('Item Dimensions'), {'fields': (('length', 'length_units','width','width_units','height','height_units'),('weight','weight_units')), 'classes': ('collapse',)}), (_('Tax'), {'fields':('taxable', 'taxClass'), 'classes': ('collapse',)}), (_('Related Products'), {'fields':('related_items','also_purchased'),'classes':'collapse'}), )
    search_fields = ['slug', 'sku', 'name']
    inlines = [ProductAttribute_Inline, Price_Inline, ProductImage_Inline]
    filter_horizontal = ('category',)

class CustomProductOptions(admin.ModelAdmin):
    inlines = [CustomTextField_Inline]

class CustomTextFieldOptions(admin.ModelAdmin):
    inlines = [CustomTextFieldTranslation_Inline]

class SubscriptionProductOptions(admin.ModelAdmin):
    inlines = [Trial_Inline]

class ProductVariationOptions(admin.ModelAdmin):
    filter_horizontal = ('options',)

class ProductImageOptions(admin.ModelAdmin):
    inlines = [ProductImageTranslation_Inline]

admin.site.register(Category, CategoryOptions)
admin.site.register(CategoryImage, CategoryImageOptions)
admin.site.register(OptionGroup, OptionGroupOptions)
admin.site.register(Option, OptionOptions)
admin.site.register(Product, ProductOptions)
admin.site.register(CustomProduct, CustomProductOptions)
admin.site.register(CustomTextField, CustomTextFieldOptions)
admin.site.register(ConfigurableProduct)
admin.site.register(DownloadableProduct)
admin.site.register(SubscriptionProduct, SubscriptionProductOptions)
admin.site.register(ProductVariation, ProductVariationOptions)
admin.site.register(ProductImage, ProductImageOptions)

