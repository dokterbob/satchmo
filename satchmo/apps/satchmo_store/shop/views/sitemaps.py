from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.core import urlresolvers
from product.models import Category, Product
from satchmo_store.shop import get_satchmo_setting


class CategorySitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.6

    def items(self):
        return Category.objects.by_site()

class ProductSitemap(Sitemap):
    changefreq = 'weekly'

    def items(self):
        return Product.objects.active_by_site(variations=False)

class MainSitemap(Sitemap):
    urls = []

    def items(self):
        return self.urls

    def add_url(self, location, priority=0.5, changefreq='weekly'):
        self.urls.append({
            'location': location,
            'priority': priority,
            'changefreq': changefreq,
        })

    def location(self, obj):
        return obj['location']

    def priority(self, obj):
        return obj['priority']

    def changefreq(self, obj):
        return obj['changefreq']

def satchmo_main():
    base = get_satchmo_setting('SHOP_BASE')
    rv = urlresolvers.reverse
    urls = (
        (base + '/', 1.0, 'hourly'),
        (rv('satchmo_contact'), 1.0, 'monthly'),
        (rv('satchmo_cart'), 0.5, 'monthly'),
        (rv('auth_login'), 0.8, 'monthly'),
        (rv('registration_register'), 0.8, 'monthly'),
        (rv('auth_password_reset'), 0.8, 'monthly'),
    )
    sitemap = MainSitemap()
    for url in urls:
        sitemap.add_url(*url)
    return sitemap

sitemaps = {
    'satchmo_main': satchmo_main,
    'category': CategorySitemap,
    'products': ProductSitemap,
}
