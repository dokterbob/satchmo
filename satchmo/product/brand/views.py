from django.contrib.sites.models import Site
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from models import Brand, BrandCategory
from satchmo.discount.utils import find_best_auto_discount
from satchmo.product.models import Product
import logging

log = logging.getLogger("satchmo_brand.views")

def brand_list(request):
    ctx = RequestContext(request, {
        'brands' : Brand.objects.active(),
    })
    return render_to_response('product/brand/index.html', ctx)

def brand_page(request, brandname):
    try:
        brand = Brand.objects.by_slug(brandname)
        
    except Brand.DoesNotExist:
        raise Http404(_('Brand "%s" does not exist') % brandname)
        
    products = list(brand.active_products())
    sale = find_best_auto_discount(products)
    
    ctx = RequestContext(request, {
        'brand' : brand,
        'sale' : sale,
    })
    return render_to_response('product/brand/view_brand.html', ctx)


def brand_category_page(request, brandname, catname):
    try:
        cat = BrandCategory.objects.by_slug(brandname, catname)
        
    except Brand.DoesNotExist:
        raise Http404(_('Brand "%s" does not exist') % brandname)
        
    except BrandCategory.DoesNotExist:
        raise Http404(_('No category "%s" in brand "%s"') % (catname, brandname))
        
    products = list(cat.active_products())
    sale = find_best_auto_discount(products)
    
    ctx = RequestContext(request, {
        'brand' : cat,
        'sale' : sale,
    })
    return render_to_response('product/brand/view_brand.html', ctx)
