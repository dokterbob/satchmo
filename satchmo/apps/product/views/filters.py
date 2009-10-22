from django import http
from django.core.paginator import Paginator, InvalidPage
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from livesettings import config_value
from product.models import Product
from product.queries import bestsellers
import logging
        
log = logging.getLogger('product.views.filters')
    
def display_bestsellers(request, count=0, template='product/best_sellers.html'):
    """Display a list of the products which have sold the most"""
    if count == 0:
        count = config_value('PRODUCT','NUM_PAGINATED')
    
    ctx = RequestContext(request, {
        'products' : bestsellers(count),
    })
    return render_to_response(template, context_instance=ctx)
        
def display_recent(request, page=0, count=0, template='product/recently_added.html'):
    """Display a list of recently added products."""
    if count == 0:
        count = config_value('PRODUCT','NUM_PAGINATED')

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
    return render_to_response(template, context_instance=ctx)
