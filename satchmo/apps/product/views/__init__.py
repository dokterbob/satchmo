from decimal import Decimal
from django import http
from django.core.xheaders import populate_xheaders
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.template.loader import select_template
from django.utils.translation import ugettext as _
from l10n.utils import moneyfmt
from livesettings import config_value
from product import signals
from product.models import Category, Product, ConfigurableProduct, sorted_tuple
from product.signals import index_prerender
from product.utils import find_best_auto_discount
from satchmo_utils.json import json_encode
from satchmo_utils.numbers import  RoundedDecimalError, round_decimal
from satchmo_utils.views import bad_or_missing
import datetime
import logging
import random

log = logging.getLogger('product.views')

NOTSET = object()

# ---- Helpers ----

def find_product_template(product, producttypes=None):
    """Searches for the correct override template given a product."""
    if producttypes is None:
        producttypes = product.get_subtypes()

    templates = ["product/detail_%s.html" % x.lower() for x in producttypes]
    templates.append('product/product.html')
    log.debug("finding product template: %s", templates)
    return select_template(templates)
    
def optionids_from_post(configurableproduct, POST):
    """Reads through the POST dictionary and tries to match keys to possible `OptionGroup` ids
    from the passed `ConfigurableProduct`"""
    chosen_options = []
    for opt_grp in configurableproduct.option_group.all():
        if POST.has_key(str(opt_grp.id)):
            chosen_options.append('%s-%s' % (opt_grp.id, POST[str(opt_grp.id)]))
    return sorted_tuple(chosen_options)

# ---- Views ----
def category_index(request, template="product/category_index.html", root_only=True):
    """Display all categories.
    
    Parameters:
    - root_only: If true, then only show root categories.
    """
    cats = Category.objects.root_categories()
    ctx = {
        'categorylist' : cats,
    }
    return render_to_response(template, context_instance=RequestContext(request, ctx))

def category_view(request, slug, parent_slugs='', template='product/category.html'):
    """Display the category, its child categories, and its products.

    Parameters:
     - slug: slug of category
     - parent_slugs: ignored    
    """
    try:
        category =  Category.objects.get_by_site(slug=slug)
        products = list(category.active_products())
        sale = find_best_auto_discount(products)

    except Category.DoesNotExist:
        return bad_or_missing(request, _('The category you have requested does not exist.'))

    child_categories = category.get_all_children()

    ctx = {
        'category': category, 
        'child_categories': child_categories,
        'sale' : sale,
        'products' : products,
    }
    index_prerender.send(Product, request=request, context=ctx, category=category, object_list=products)
    return render_to_response(template, context_instance=RequestContext(request, ctx))


def display_featured(num_to_display=NOTSET, random_display=NOTSET):
    """
    Used by the index generic view to choose how the featured products are displayed.
    Items can be displayed randomly or all in order
    """
    if num_to_display == NOTSET:
        num_to_display = config_value('PRODUCT','NUM_DISPLAY')
    if random_display == NOTSET:
        random_display = config_value('PRODUCT','RANDOM_FEATURED')
        
    q = Product.objects.featured_by_site()
    if not random_display:
        return q[:num_to_display]
    else:
        return q.order_by('?')[:num_to_display]

def get_configurable_product_options(request, id):
    """Used by admin views"""
    cp = get_object_or_404(ConfigurableProduct, product__id=id)
    options = ''
    for og in cp.option_group.all():
        for opt in og.option_set.all():
            options += '<option value="%s">%s</option>' % (opt.id, str(opt))
    if not options:
        return '<option>No valid options found in "%s"</option>' % cp.product.slug
    return http.HttpResponse(options, mimetype="text/html")


def get_product(request, product_slug=None, selected_options=(), 
    default_view_tax=NOTSET):
    """Basic product view"""
    
    errors = request.session.get('ERRORS', None)
    if errors is not None:
        del(request.session['ERRORS'])
    try:
        product = Product.objects.get_by_site(active=True, slug=product_slug)
    except Product.DoesNotExist:
        return bad_or_missing(request, _('The product you have requested does not exist.'))

    if default_view_tax == NOTSET:
        default_view_tax = config_value('TAX', 'DEFAULT_VIEW_TAX')

    subtype_names = product.get_subtypes()
    
    # Save product id for xheaders, in case we display a ConfigurableProduct
    product_id = product.id
    
    # Clone product object in order to have current product variations in context (extra_context)
    current_product = product

    if 'ProductVariation' in subtype_names:
        selected_options = product.productvariation.unique_option_ids
        #Display the ConfigurableProduct that this ProductVariation belongs to.
        product = product.productvariation.parent.product
        subtype_names = product.get_subtypes()

    best_discount = find_best_auto_discount(product)
    
    extra_context = {
        'product': product,
        'current_product' : current_product,
        'default_view_tax': default_view_tax,
        'sale': best_discount,
        'error_message' : errors,
    }

    # Get the template context from the Product.
    extra_context = product.add_template_context(context=extra_context,
        request=request, selected_options=selected_options,
        default_view_tax=default_view_tax)

    template = find_product_template(product, producttypes=subtype_names)
    context = RequestContext(request, extra_context)
    
    response = http.HttpResponse(template.render(context))
    populate_xheaders(request, response, Product, product_id)
    return response

def get_price(request, product_slug):
    """Get base price for a product, returning the answer encoded as JSON."""
    quantity = Decimal('1')

    try:
        product = Product.objects.get_by_site(active=True, slug=product_slug)
    except Product.DoesNotExist:
        return http.HttpResponseNotFound(json_encode(('', _("not available"))), mimetype="text/javascript")

    prod_slug = product.slug

    if request.method == "POST" and request.POST.has_key('quantity'):
        try:
            quantity = round_decimal(request.POST['quantity'], places=2, roundfactor=.25)
        except RoundedDecimalError:
            quantity = Decimal('1.0')
            log.warn("Could not parse a decimal from '%s', returning '1.0'", request.POST['quantity'])

    if 'ConfigurableProduct' in product.get_subtypes():
        cp = product.configurableproduct
        chosen_options = optionids_from_post(cp, request.POST)
        pvp = cp.get_product_from_options(chosen_options)

        if not pvp:
            return http.HttpResponse(json_encode(('', _("not available"))), mimetype="text/javascript")
        prod_slug = pvp.slug
        price = moneyfmt(pvp.get_qty_price(quantity))
    else:
        price = moneyfmt(product.get_qty_price(quantity))

    if not price:
        return http.HttpResponse(json_encode(('', _("not available"))), mimetype="text/javascript")

    return http.HttpResponse(json_encode((prod_slug, price)), mimetype="text/javascript")


def get_price_detail(request, product_slug):
    """Get all price details for a product, returning the response encoded as JSON."""
    results = {
        "success" : False,
        "message" :  _("not available")
    }
    price = None

    if request.method=="POST":
        reqdata = request.POST
    else:
        reqdata = request.GET

    try:
        product = Product.objects.get_by_site(active=True, slug=product_slug)
        found = True

        prod_slug = product.slug

        if reqdata.has_key('quantity'):
            try:
                quantity = round_decimal(reqdata['quantity'], places=2, roundfactor=.25)
            except RoundedDecimalError:
                quantity = Decimal('1.0')
                log.warn("Could not parse a decimal from '%s', returning '1.0'", reqdata['quantity'])
        else:
            quantity = Decimal('1.0')

        if 'ConfigurableProduct' in product.get_subtypes():
            cp = product.configurableproduct
            chosen_options = optionids_from_post(cp, reqdata)
            product = cp.get_product_from_options(chosen_options)

        if product:
            price = product.get_qty_price(quantity)

            results['slug'] = product.slug
            results['price'] = float(price)
            results['success'] = True
            results['message'] = ""

    except Product.DoesNotExist:
        found = False

    data = json_encode(results)
    if found:
        return http.HttpResponse(data, mimetype="text/javascript")
    else:
        return http.HttpResponseNotFound(data, mimetype="text/javascript")
