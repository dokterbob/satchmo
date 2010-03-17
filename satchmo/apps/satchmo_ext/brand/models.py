from django.conf import settings
from django.contrib.sites.models import Site
from django.db import models
from django.utils.translation import ugettext_lazy as _
from l10n.mixins import TranslatedObjectMixin
import product
from product.models import Product
from satchmo_utils.thumbnail.field import ImageWithThumbnailField
from signals_ahoy.signals import collect_urls
import logging

log = logging.getLogger('brand.models')

class BrandManager(models.Manager):
    
    def active(self, site=None):
        if not site:
            site = Site.objects.get_current()
        return self.filter(site=site, active=True)
    
    def by_slug(self, slug):
        site = Site.objects.get_current()
        return self.get(slug=slug, site=site)

class Brand(models.Model, TranslatedObjectMixin):
    """A product brand"""
    site = models.ForeignKey(Site)
    slug = models.SlugField(_("Slug"), unique=True,
    help_text=_("Used for URLs"))
    products = models.ManyToManyField(Product, blank=True, verbose_name=_("Products"), through='BrandProduct')
    ordering = models.IntegerField(_("Ordering"))
    active = models.BooleanField(default=True)
    
    objects = BrandManager()
    
    def _active_categories(self):
        return [cat for cat in self.categories.all() if cat.has_content()]
    
    active_categories = property(fget=_active_categories)
    
    def _translation(self):
        return self._find_translation()
    translation = property(fget=_translation)

    def _get_absolute_url(self):
        return ('satchmo_brand_view', None, {'brandname' : self.slug})
        
    get_absolute_url = models.permalink(_get_absolute_url)
        
    def active_products(self):
        return self.products.filter(site=self.site, active=True)        

    def has_categories(self):
        return self.active_categories().count() > 0

    def has_content(self):
        return self.has_products() or self.has_categories()

    def has_products(self):
        return self.active_products().count() > 0
            
    def __unicode__(self):
        return u"%s" % self.slug
            
    class Meta:
        ordering=('ordering', 'slug')
        verbose_name = _('Brand')
        verbose_name_plural = _('Brands')

class BrandProduct(models.Model):
    brand = models.ForeignKey(Brand)
    product = models.ForeignKey(Product)
    
    class Meta:
        verbose_name=_("Brand Product")
        verbose_name_plural=_("Brand Products")

class BrandTranslation(models.Model):
    brand = models.ForeignKey(Brand, related_name="translations")
    languagecode = models.CharField(_('language'), max_length=10, choices=settings.LANGUAGES)
    name = models.CharField(_('title'), max_length=100, blank=False)
    short_description = models.CharField(_('Short Description'), blank=True, max_length=200)
    description = models.TextField(_('Full Description'), blank=True)
    picture = ImageWithThumbnailField(verbose_name=_('Picture'),
        upload_to="__DYNAMIC__",
        name_field="_filename",
        null=True, blank=True,
        max_length=200) #Media root is automatically prepended
    
    def _get_filename(self):
        if self.brand:
            return '%s-%s' % (self.brand.slug, self.id)
        else:
            return 'default'
    _filename = property(_get_filename)

    class Meta:
        ordering=('languagecode', )      
        verbose_name = _('Brand Translation')
        verbose_name_plural = _('Brand Translations')  

class BrandCategoryManager(models.Manager):
    def by_slug(self, brandname, slug):
        brand = Brand.objects.by_slug(brandname)
        return brand.categories.get(slug=slug)

class BrandCategory(models.Model, TranslatedObjectMixin):
    """A category within a brand"""
    slug = models.SlugField(_("Slug"),
        help_text=_("Used for URLs"))
    brand = models.ForeignKey(Brand, related_name="categories")
    products = models.ManyToManyField(Product, blank=True, verbose_name=_("Products"), through='BrandCategoryProduct')
    ordering = models.IntegerField(_("Ordering"))
    active = models.BooleanField(default=True)

    objects = BrandCategoryManager()

    def _translation(self):
        return self._find_translation()
    translation = property(fget=_translation)

    def _get_absolute_url(self):
        return ('satchmo_brand_category_view', None, {'brandname' : self.brand.slug, 'catname' : self.slug})
    
    get_absolute_url = models.permalink(_get_absolute_url)
        
    def active_products(self):
        return self.products.filter(site=self.brand.site).filter(active=True)                
        
    def has_categories(self):
        return False    
    
    def has_content(self):
        return self.active_products()

    def has_products(self):
        return self.active_products().count > 0

    def __unicode__(self):
        return u"%s: %s" % (self.brand.slug, self.slug)

    class Meta:
        ordering=('ordering', 'slug')
        verbose_name = _('Brand Category')
        verbose_name_plural = _('Categories')

class BrandCategoryProduct(models.Model):
    brandcategory = models.ForeignKey(BrandCategory)
    product = models.ForeignKey(Product)
    
    class Meta:
        verbose_name = _('Brand Category Product')
        verbose_name_plural = _('Brand Category Products')

class BrandCategoryTranslation(models.Model):

    brandcategory = models.ForeignKey(BrandCategory, related_name="translations")
    languagecode = models.CharField(_('language'), max_length=10, choices=settings.LANGUAGES)
    name = models.CharField(_('title'), max_length=100, blank=False)
    short_description = models.CharField(_('Short Description'), blank=True, max_length=200)
    description = models.TextField(_('Description'), blank=True)
    picture = ImageWithThumbnailField(verbose_name=_('Picture'),
        upload_to="__DYNAMIC__",
        name_field="_filename",
        null=True, blank=True,
        max_length=200) #Media root is automatically prepended
    
    def _get_filename(self):
        if self.brandcategory:
            return '%s-%s' % (self.brandcategory.brand.slug, self.id)
        else:
            return 'default'
    _filename = property(_get_filename)
    
    class Meta:
        ordering=('languagecode', )
        verbose_name_plural = _('Brand Category Translations')

#import config        
from urls import add_brand_urls
collect_urls.connect(add_brand_urls, sender=product)
