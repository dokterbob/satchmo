from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _
from satchmo.discount.utils import find_best_auto_discount
from satchmo.product.models import Category
from satchmo.shop.views.utils import bad_or_missing

def display(request, slug, parent_slugs=''):
    """Display the category, its child categories, and its products.
    
    Parameters:
     - slug: slug of category
     - parent_slugs: ignored    
    """
    try:
        category = Category.objects.get(slug=slug)
        products = list(category.active_products())
        sale = find_best_auto_discount(products)
            
    except Category.DoesNotExist:
        return bad_or_missing(request, _('The category you have requested does not exist.'))

    child_categories = category.get_all_children()
    ctx = RequestContext(request, {
        'category': category, 
        'child_categories': child_categories,
        'sale' : sale,
        'products' : products,
        })
    return render_to_response('base_category.html', ctx)
