from django.shortcuts import render_to_response
from django.template import RequestContext
from livesettings import config_value
from satchmo_ext.productratings.queries import highest_rated

def display_bestratings(request, count=0, template='product/best_ratings.html'):
    """Display a list of the products with the best ratings in comments"""
    if count is None:
        count = config_value('PRODUCT','NUM_DISPLAY')
    
    ctx = RequestContext(request, {
        'products' : highest_rated(),
    })
    return render_to_response(template, context_instance=ctx)
