from django.contrib import admin
from product.modules.downloadable.models import DownloadableProduct, DownloadLink

admin.site.register(DownloadableProduct)
admin.site.register(DownloadLink)

