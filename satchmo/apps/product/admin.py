from django.contrib import admin
from django.forms import models, ValidationError
from django.utils.translation import ugettext_lazy as _
from l10n.l10n_settings import get_l10n_setting
from livesettings import config_value
from product.models import Category, CategoryTranslation, CategoryImage, CategoryImageTranslation, \
                                   OptionGroup, OptionGroupTranslation, Option, OptionTranslation, Product, \
                                   ProductAttribute, \
                                   Price, ProductImage, ProductImageTranslation, default_weight_unit, \
                                   default_dimension_unit, ProductTranslation, Discount, TaxClass, AttributeOption, \
                                   CategoryAttribute
from product.utils import import_validator, validate_attribute_value
from satchmo_utils.thumbnail.field import ImageWithThumbnailField
from satchmo_utils.thumbnail.widgets import AdminImageWithThumbnailWidget
from django.http import HttpResponseRedirect
import re

def clean_attribute_value(cleaned_data, obj):
    value = cleaned_data['value']
    attribute = cleaned_data['option']
    success, valid_value = validate_attribute_value(attribute, value, obj)
    if not success:
        raise ValidationError(attribute.error_message)
    return valid_value

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
    raw_id_fields = ('valid_products',)

class OptionGroupTranslation_Inline(admin.StackedInline):
    model = OptionGroupTranslation
    extra = 1

class Option_Inline(admin.TabularInline):
    model = Option
    extra = 5

class OptionTranslation_Inline(admin.StackedInline):
    model = OptionTranslation
    extra = 1

class AttributeOptionForm(models.ModelForm):

    def clean_validation(self):
        validation = self.cleaned_data['validation']
        try:
            import_validator(validation)
        except ImportError:
            raise ValidationError(_("Invalid validation function specifed!"))
        return validation


class AttributeOptionAdmin(admin.ModelAdmin):
    form = AttributeOptionForm
    prepopulated_fields = {"name": ("description",)}

class ProductAttributeInlineForm(models.ModelForm):

    def clean_value(self):
        return clean_attribute_value(self.cleaned_data, self.cleaned_data['product'])

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

class CategoryAttributeInlineForm(models.ModelForm):

    def clean_value(self):
        return clean_attribute_value(self.cleaned_data, self.cleaned_data['category'])

class CategoryAttributeInline(admin.TabularInline):
    model = CategoryAttribute
    extra = 2
    form = CategoryAttributeInlineForm

class CategoryAdminForm(models.ModelForm):

    def clean_parent(self):
        parent = self.cleaned_data.get('parent', None)
        slug = self.cleaned_data.get('slug', None)
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
    inlines = [CategoryAttributeInline, CategoryImage_Inline]
    if get_l10n_setting('show_admin_translations'):
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
    if get_l10n_setting('show_admin_translations'):
        inlines.append(OptionGroupTranslation_Inline)
    if config_value('SHOP','SHOW_SITE'):
        list_display = ('site',)
    else:
        list_display = ()
    list_display += ('name',)

class OptionOptions(admin.ModelAdmin):
    inlines = []
    if get_l10n_setting('show_admin_translations'):
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
    if get_l10n_setting('show_admin_translations'):
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

admin.site.register(Category, CategoryOptions)
#admin.site.register(CategoryImage, CategoryImageOptions)
admin.site.register(Discount, DiscountOptions)
admin.site.register(OptionGroup, OptionGroupOptions)
admin.site.register(Option, OptionOptions)
admin.site.register(Product, ProductOptions)
admin.site.register(TaxClass)
admin.site.register(AttributeOption, AttributeOptionAdmin)
#admin.site.register(ProductImage, ProductImageOptions)

