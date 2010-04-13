from django.contrib import admin
from l10n.l10n_settings import get_l10n_setting
from product.modules.custom.models import CustomProduct, CustomTextField, CustomTextFieldTranslation

class CustomTextField_Inline(admin.TabularInline):
    model = CustomTextField
    extra = 3

class CustomTextFieldTranslation_Inline(admin.StackedInline):
    model = CustomTextFieldTranslation
    extra = 1

class CustomProductOptions(admin.ModelAdmin):
    inlines = [CustomTextField_Inline]

class CustomTextFieldOptions(admin.ModelAdmin):
    inlines = []
    if get_l10n_setting('show_admin_translations'):
        inlines.append(CustomTextFieldTranslation_Inline)

admin.site.register(CustomProduct, CustomProductOptions)
admin.site.register(CustomTextField, CustomTextFieldOptions)

