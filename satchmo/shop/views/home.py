from django.core.paginator import Paginator, EmptyPage
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _
from satchmo.configuration import config_value
from satchmo.product.views import display_featured

def home(request, template="base_index.html"):
    # Display the category, its child categories, and its products.
    
    if request.method == "GET":
        currpage = request.GET.get('page', 1)
        
    featured = display_featured()
    
    count = config_value('SHOP','NUM_PAGINATED')
    
    paginator = Paginator(featured, count)
    
    is_paged = False
    page = None
    
    try:
        paginator.validate_number(currpage)
    except EmptyPage:
        return bad_or_missing(request, _("Invalid page number"))
            
    is_paged = paginator.num_pages > 1
    page = paginator.page(currpage)
        
    ctx = RequestContext(request, {
        'all_products_list' : page.object_list,        
        'is_paginated' : is_paged,
        'page_obj' : page,
        'paginator' : paginator
    })
    
    return render_to_response(template, ctx)
    
