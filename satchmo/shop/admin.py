from satchmo.shop.models import Config, Cart, CartItem, CartItemDetails
from django.contrib import admin
from django.utils.translation import get_language, ugettext_lazy as _


class CartItem_Inline(admin.TabularInline):
    model = CartItem
    extra = 3

class CartItemDetails_Inline(admin.StackedInline):
    model = CartItemDetails
    extra = 1

class ConfigOptions(admin.ModelAdmin):
    filter_horizontal = ('shipping_countries',)

class CartOptions(admin.ModelAdmin):
    list_display = ('date_time_created','numItems','total')
    inlines = [CartItem_Inline]

class CartItemOptions(admin.ModelAdmin):
    inlines = [CartItemDetails_Inline]

admin.site.register(Config, ConfigOptions)
admin.site.register(Cart, CartOptions)
admin.site.register(CartItem, CartItemOptions)

