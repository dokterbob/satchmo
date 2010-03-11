from django.contrib import admin
from django.forms import models, ValidationError
from django.utils.translation import get_language, ugettext_lazy as _
from l10n.l10n_settings import get_l10n_setting
from livesettings import config_value
from product.models import Category, CategoryTranslation, CategoryImage, CategoryImageTranslation, \
                                   OptionGroup, OptionGroupTranslation, Option, OptionTranslation, Product, \
                                   CustomProduct, CustomTextField, CustomTextFieldTranslation, ConfigurableProduct, \
                                   DownloadableProduct, SubscriptionProduct, Trial, ProductVariation, ProductAttribute, \
                                   Price, ProductImage, ProductImageTranslation, default_weight_unit, \
                                   default_dimension_unit, ProductTranslation, Discount, TaxClass, AttributeOption
from satchmo_utils.thumbnail.field import ImageWithThumbnailField
from satchmo_utils.thumbnail.widgets import AdminImageWithThumbnailWidget
from django.http import HttpResponseRedirect
import re

class CategoryTranslation_Inline(admin.StackedInline):
    model = CategoryTranslation
    extra = 1

class CategoryImage_Inline(admin.TabularInline):
    model = CategoryImage
    extra = 3
    
    formfield_overrides = {
        ImageWithThumbnailField : {'widget' : AdminImageWithThumbnailWidget},
    }

class CategoryImageTranslation_Inline(admin.StackedInline):
    model = CategoryImageTranslation
    extra = 1

class DiscountOptions(admin.ModelAdmin):
    list_display=('site', 'description','active')
    list_display_links = ('description',)
    raw_id_fields = ('validProducts',)

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

class ProductAttributeForm(models.ModelForm):
    
    def clean_validation(self):
        validation = self.cleaned_data['validation']
        try:
            re.compile(validation)
        except:
            raise ValidationError(_("Invalid regular expression"))
        return validation
        

class ProductAttributeAdmin(admin.ModelAdmin):
    form = ProductAttributeForm
    prepopulated_fields = {"name": ("description",)}
    

class ProductAttributeInlineForm(models.ModelForm):
    
    def clean_value(self):
        value = self.cleaned_data['value']
        attribute = self.cleaned_data['option']
        product = self.cleaned_data['product']
        function_name = attribute.validation.split('.')[-1]
        import_name = '.'.join(attribute.validation.split('.')[:-1])
        import_module = __import__(import_name, fromlist=[function_name])
        validation_function = getattr(import_module, function_name)
        success, valid_value = validation_function(value, product)
        if not success:
            raise ValidationError(attribute.error_message)
        return valid_value

class ProductAttribute_Inline(admin.TabularInline):
    model = ProductAttribute
    extra = 2
    form = ProductAttributeInlineForm

class Price_Inline(admin.TabularInline):
    model = Price
    extra = 2

class ProductImage_Inline(admin.StackedInline):
    model = ProductImage
    extra = 3
    
    formfield_overrides = {
        ImageWithThumbnailField : {'widget' : AdminImageWithThumbnailWidget},
    }
 
class ProductTranslation_Inline(admin.TabularInline): 
    model = ProductTranslation 
    extra = 1    

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
    
    if config_value('SHOP','SHOW_SITE'):
        list_display = ('site',)
    else:
        list_display = ()
    
    list_display += ('name', '_parents_repr', 'is_active')
    list_display_links = ('name',)
    ordering = ['site', 'parent__id', 'ordering', 'name']
    inlines = [CategoryImage_Inline]
    if get_l10n_setting('show_translations'):
        inlines.append(CategoryTranslation_Inline)
    filter_horizontal = ('related_categories',)
    form = CategoryAdminForm

    actions = ('mark_active', 'mark_inactive')

    def mark_active(self, request, queryset):
        queryset.update(is_active=True)
        return HttpResponseRedirect('')

    def mark_inactive(self, request, queryset):
        queryset.update(is_active=False)
        return HttpResponseRedirect('')

class CategoryImageOptions(admin.ModelAdmin):
    inlines = [CategoryImageTranslation_Inline]

class OptionGroupOptions(admin.ModelAdmin):
    inlines = [Option_Inline]
    if get_l10n_setting('show_translations'):
        inlines.append(OptionGroupTranslation_Inline)
    if config_value('SHOP','SHOW_SITE'):
        list_display = ('site',)
    else:
        list_display = ()
    list_display += ('name',)

class OptionOptions(admin.ModelAdmin):
    inlines = []
    if get_l10n_setting('show_translations'):
        inlines.append(OptionTranslation_Inline)

class ProductOptions(admin.ModelAdmin):
    
    def make_active(self, request, queryset):
        rows_updated = queryset.update(active=True)
        if rows_updated == 1:
            message_bit = _("1 product was")
        else:
            message_bit = _("%s products were" % rows_updated)
        self.message_user(request, _("%s successfully marked as active") % message_bit)
        return HttpResponseRedirect('')
    make_active.short_description = _("Mark selected products as active")
    
    def make_inactive(self, request, queryset):
        rows_updated = queryset.update(active=False)
        if rows_updated == 1:
            message_bit = _("1 product was")
        else:
            message_bit = _("%s products were" % rows_updated)
        self.message_user(request, _("%s successfully marked as inactive") % message_bit)
        return HttpResponseRedirect('')
    make_inactive.short_description = _("Mark selected products as inactive")
    
    def make_featured(self, request, queryset):
        rows_updated = queryset.update(featured=True)
        if rows_updated == 1:
            message_bit = _("1 product was")
        else:
            message_bit = _("%s products were" % rows_updated)
        self.message_user(request, _("%s successfully marked as featured") % message_bit)
        return HttpResponseRedirect('')
    make_featured.short_description = _("Mark selected products as featured")
    
    def make_unfeatured(self, request, queryset):
        rows_updated = queryset.update(featured=False)
        if rows_updated == 1:
            message_bit = _("1 product was")
        else:
            message_bit = _("%s products were" % rows_updated)
        self.message_user(request, _("%s successfully marked as not featured") % message_bit)
        return HttpResponseRedirect('')
    make_unfeatured.short_description = _("Mark selected products as not featured")

    if config_value('SHOP','SHOW_SITE'):
        list_display = ('site',)
    else:
        list_display = ()

    list_display += ('slug', 'name', 'unit_price', 'items_in_stock', 'active','featured', 'get_subtypes')
    list_display_links = ('slug', 'name')
    list_filter = ('category', 'date_added','active','featured')
    actions = ('make_active', 'make_inactive', 'make_featured', 'make_unfeatured')
    fieldsets = (
    (None, {'fields': ('site', 'category', 'name', 'slug', 'sku', 'description', 'short_description', 'date_added', 
            'active', 'featured', 'items_in_stock','total_sold','ordering', 'shipclass')}), (_('Meta Data'), {'fields': ('meta',), 'classes': ('collapse',)}), 
            (_('Item Dimensions'), {'fields': (('length', 'length_units','width','width_units','height','height_units'),('weight','weight_units')), 'classes': ('collapse',)}), 
            (_('Tax'), {'fields':('taxable', 'taxClass'), 'classes': ('collapse',)}), 
            (_('Related Products'), {'fields':('related_items','also_purchased'),'classes':('collapse',)}), )
    search_fields = ['slug', 'sku', 'name']
    inlines = [ProductAttribute_Inline, Price_Inline, ProductImage_Inline]
    if get_l10n_setting('show_translations'):
        inlines.append(ProductTranslation_Inline)
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
    inlines = []
    if get_l10n_setting('show_translations'):
        inlines.append(CustomTextFieldTranslation_Inline)

class SubscriptionProductOptions(admin.ModelAdmin):
    inlines = [Trial_Inline]

class ProductVariationOptions(admin.ModelAdmin):
    filter_horizontal = ('options',)

class ProductImageOptions(admin.ModelAdmin):
    inlines = []
    if get_l10n_setting('show_translations'):
        inlines.append(ProductImageTranslation_Inline)

admin.site.register(Category, CategoryOptions)
#admin.site.register(CategoryImage, CategoryImageOptions)
admin.site.register(Discount, DiscountOptions)
admin.site.register(OptionGroup, OptionGroupOptions)
admin.site.register(Option, OptionOptions)
admin.site.register(Product, ProductOptions)
admin.site.register(CustomProduct, CustomProductOptions)
admin.site.register(CustomTextField, CustomTextFieldOptions)
admin.site.register(ConfigurableProduct)
admin.site.register(DownloadableProduct)
admin.site.register(SubscriptionProduct, SubscriptionProductOptions)
admin.site.register(ProductVariation, ProductVariationOptions)
admin.site.register(TaxClass)
admin.site.register(AttributeOption, ProductAttributeAdmin)
#admin.site.register(ProductImage, ProductImageOptions)

