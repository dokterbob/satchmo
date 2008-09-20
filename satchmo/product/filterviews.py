from django import http
from django.core.paginator import Paginator, InvalidPage
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from satchmo.configuration import config_value
from satchmo.product.models import Product
from satchmo.productratings.queries import highest_rated
from satchmo.product.queries import bestsellers
import logging
        
log = logging.getLogger('product.filterviews')

def display_bestratings(request, count=0, template='product/best_ratings.html'):
    """Display a list of the products with the best ratings in comments"""
    if count is None:
        count = config_value('SHOP', 'NUM_DISPLAY')
    
    ctx = RequestContext(request, {
        'products' : highest_rated(),
    })
    return render_to_response(template, ctx)
    
def display_bestsellers(request, count=0, template='product/best_sellers.html'):
    """Display a list of the products which have sold the most"""
    if count == 0:
        count = config_value('SHOP', 'NUM_PAGINATED')
    
    ctx = RequestContext(request, {
        'products' : bestsellers(count),
    })
    return render_to_response(template, ctx)
        
def display_recent(request, page=0, count=0, template='product/recently_added.html'):
    """Display a list of recently added products."""
    if count == 0:
        count = config_value('SHOP', 'NUM_PAGINATED')

    if page == 0:
        if request.method == 'GET':
            page = request.GET.get('page', 1)
        else:
            page = 1
     
    query = Product.objects.recent_by_site()
    paginator = Paginator(query, count)
    try:
        currentpage = paginator.page(page)
    except InvalidPage:
        currentpage = None
    
    ctx = RequestContext(request, {
        'page' : currentpage,
        'paginator' : paginator,
    })
    return render_to_response(template, ctx)
