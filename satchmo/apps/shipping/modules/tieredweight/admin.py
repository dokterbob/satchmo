from django.contrib import admin
from shipping.modules.tieredweight.models import Carrier, WeightTier, Zone, ZoneTranslation
from shipping.modules.tieredweight.forms import CarrierAdminForm, ZoneAdminForm


class WeightTierInline(admin.TabularInline):
    model = WeightTier


class ZoneTranslationInline(admin.TabularInline):
    model = ZoneTranslation


class CarrierOptions(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('name', 'default_zone')
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('active', 'ordering')
        }),
    )
    list_display = ['name', 'active', 'default_zone']
    form = CarrierAdminForm


class ZoneOptions(admin.ModelAdmin):
    list_filter = ['carrier',]
    list_display = ['carrier', 'name']
    filter_horizontal = ('countries',)
    inlines = [WeightTierInline, ZoneTranslationInline]
    form = ZoneAdminForm


admin.site.register(Carrier, CarrierOptions)
admin.site.register(Zone, ZoneOptions)