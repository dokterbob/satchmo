from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _
from satchmo.product.models import Category
from satchmo.shop.views.utils import bad_or_missing

def display(request, slug, parent_slugs=''):
    # Display the category, its child categories, and its products.
    try:
        category = Category.objects.get(slug=slug)
    except Category.DoesNotExist:
        return bad_or_missing(request, _('The category you have requested does not exist.'))

    child_categories = category.get_all_children()
    return render_to_response('base_category.html',
        {'category': category, 'child_categories': child_categories},
        RequestContext(request))
