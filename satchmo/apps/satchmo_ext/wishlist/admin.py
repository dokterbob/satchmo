from satchmo_ext.wishlist.models import ProductWish
from django.contrib import admin
from django.utils.translation import get_language, ugettext_lazy as _


class ProductWishOptions(admin.ModelAdmin):
    list_display = ('contact', 'product', 'create_date')
    ordering = ('contact', '-create_date', 'product')

admin.site.register(ProductWish, ProductWishOptions)

