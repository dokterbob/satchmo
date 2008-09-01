from satchmo.product.models import Category, CategoryTranslation, CategoryImage, CategoryImageTranslation, OptionGroup, OptionGroupTranslation, Option, OptionTranslation, Product, CustomProduct, CustomTextField, CustomTextFieldTranslation, ConfigurableProduct, DownloadableProduct, SubscriptionProduct, Trial, ProductVariation, ProductAttribute, Price, ProductImage, ProductImageTranslation, default_weight_unit, default_dimension_unit
from django.contrib import admin
from django.forms import models, ValidationError
from django.utils.translation import get_language, ugettext_lazy as _
from satchmo.thumbnail.field import ImageWithThumbnailField
from satchmo.thumbnail.widgets import AdminImageWithThumbnailWidget

class CategoryTranslation_Inline(admin.StackedInline):
    model = CategoryTranslation
    extra = 1

class CategoryImage_Inline(admin.TabularInline):
    model = CategoryImage
    extra = 3
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        # This method will turn all TextFields into giant TextFields
        if isinstance(db_field, ImageWithThumbnailField):
            kwargs['widget'] = AdminImageWithThumbnailWidget
            return db_field.formfield(**kwargs)
            
        return super(CategoryImage_Inline, self).formfield_for_dbfield(db_field, **kwargs)
    

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
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        # This method will turn all TextFields into giant TextFields
        if isinstance(db_field, ImageWithThumbnailField):
            kwargs['widget'] = AdminImageWithThumbnailWidget
            return db_field.formfield(**kwargs)
            
        return super(ProductImage_Inline, self).formfield_for_dbfield(db_field, **kwargs)
    

class ProductImageTranslation_Inline(admin.StackedInline):
    model = ProductImageTranslation
    extra = 1

class CategoryAdminForm(models.ModelForm):
    
    def clean_parent(self):
        parent = self.cleaned_data['parent']
        slug = self.cleaned_data['slug']
        if parent and slug:
            if parent.slug == slug:
                raise ValidationError(_("You must not save a category in itself!"))

            for p in parent._recurse_for_parents(parent):
                if slug == p.slug:
                    raise ValidationError(_("You must not save a category in itself!"))
                    
        return parent

class CategoryOptions(admin.ModelAdmin):
    list_display = ('site','name', '_parents_repr')
    list_display_links = ('name',)
    ordering = ['site', 'parent__id', 'ordering', 'name']
    inlines = [CategoryTranslation_Inline, CategoryImage_Inline]
    
    form = CategoryAdminForm    

class CategoryImageOptions(admin.ModelAdmin):
    inlines = [CategoryImageTranslation_Inline]

class OptionGroupOptions(admin.ModelAdmin):
    inlines = [OptionGroupTranslation_Inline, Option_Inline]
    list_display = ['site', 'name']

class OptionOptions(admin.ModelAdmin):
    inlines = [OptionTranslation_Inline]

class ProductOptions(admin.ModelAdmin):
    list_display = ('site', 'slug', 'sku', 'name', 'unit_price', 'items_in_stock', 'get_subtypes')
    list_display_links = ('slug', 'name')
    list_filter = ('category', 'date_added')
    fieldsets = (
    (None, {'fields': ('site', 'category', 'name', 'slug', 'sku', 'description', 'short_description', 'date_added', 'active', 'featured', 'items_in_stock','total_sold','ordering')}), (_('Meta Data'), {'fields': ('meta',), 'classes': ('collapse',)}), (_('Item Dimensions'), {'fields': (('length', 'length_units','width','width_units','height','height_units'),('weight','weight_units')), 'classes': ('collapse',)}), (_('Tax'), {'fields':('taxable', 'taxClass'), 'classes': ('collapse',)}), (_('Related Products'), {'fields':('related_items','also_purchased'),'classes':'collapse'}), )
    search_fields = ['slug', 'sku', 'name']
    inlines = [ProductAttribute_Inline, Price_Inline, ProductImage_Inline]
    filter_horizontal = ('category',)
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        field = super(ProductOptions, self).formfield_for_dbfield(db_field, **kwargs)
        fieldname = db_field.name
        if fieldname in ("length_units", "width_units", "height_units"): 
            field.initial = default_dimension_unit()
        elif fieldname == "weight_units":
            field.initial = default_weight_unit()
        return field

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

