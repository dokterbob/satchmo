from django.shortcuts import render_to_response
from django.template import RequestContext
from product.models import Product
from satchmo_store.shop import signals
from signals_ahoy.signals import application_search

def search_view(request, template="shop/search.html"):
    """Perform a search based on keywords and categories in the form submission"""
    if request.method=="GET":
        data = request.GET
    else:
        data = request.POST

    keywords = data.get('keywords', '').split(' ')
    category = data.get('category', None)

    keywords = filter(None, keywords)

    results = {}
    
    # this signal will usually call listeners.default_product_search_listener
    application_search.send(Product, request=request, 
        category=category, keywords=keywords, results=results)

    context = RequestContext(request, {
            'results': results,
            'category' : category,
            'keywords' : keywords})
    return render_to_response(template, context_instance=context)
