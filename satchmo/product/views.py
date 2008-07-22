import logging
from django import http
from django.db.models import Q
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.template.loader import select_template
from django.utils.translation import ugettext as _
from satchmo.configuration import config_value
from satchmo.discount.utils import find_best_auto_discount
from satchmo.l10n.utils import moneyfmt
from satchmo.product.models import Category, Product, ConfigurableProduct
from satchmo.product.utils import get_tax
from satchmo.shop.views.utils import bad_or_missing
from satchmo.tax.utils import get_tax_processor
from satchmo.utils.json import json_encode
import datetime
import random

try:
    set
except NameError:
    from sets import Set as set     # Python 2.3 fallback.

log = logging.getLogger('product.views')

NOTSET = object()

def find_product_template(product, producttypes=None):
    if producttypes is None:
        producttypes = product.get_subtypes()

    templates = ["product/detail_%s.html" % x.lower() for x in producttypes]
    templates.append('base_product.html')
    return select_template(templates)

def get_product(request, product_slug, selected_options=set(), include_tax=NOTSET, default_view_tax=NOTSET):
    try:
        product = Product.objects.get(active=True, slug=product_slug)
    except Product.DoesNotExist:
        return bad_or_missing(request, _('The product you have requested does not exist.'))

    if default_view_tax == NOTSET:
        default_view_tax = config_value('TAX', 'DEFAULT_VIEW_TAX')

    if default_view_tax:
        include_tax = True

    elif include_tax == NOTSET:
        include_tax = default_view_tax

    if default_view_tax:
        include_tax = True

    subtype_names = product.get_subtypes()

    if 'ProductVariation' in subtype_names:
        selected_options = product.productvariation.option_values
        #Display the ConfigurableProduct that this ProductVariation belongs to.
        product = product.productvariation.parent.product
        subtype_names = product.get_subtypes()

    extra_context = {
        'product': product,
        'default_view_tax': default_view_tax,
        'sale': find_best_auto_discount(product),
    }

    # Get the template context from the Product.
    extra_context = product.add_template_context(context=extra_context,
        request=request, selected_options=selected_options,
        include_tax=include_tax, default_view_tax=default_view_tax)

    if include_tax:
        tax_amt = get_tax(request.user, product, 1)
        extra_context['product_tax'] = tax_amt
        extra_context['price_with_tax'] = product.unit_price + tax_amt

    template = find_product_template(product, producttypes=subtype_names)
    context = RequestContext(request, extra_context)
    return http.HttpResponse(template.render(context))

def optionset_from_post(configurableproduct, POST):
    chosen_options = set()
    for opt_grp in configurableproduct.option_group.all():
        if POST.has_key(str(opt_grp.id)):
            chosen_options.add('%s-%s' % (opt_grp.id, POST[str(opt_grp.id)]))
    return chosen_options

def get_price(request, product_slug):
    quantity = 1

    try:
        product = Product.objects.get(active=True, slug=product_slug)
    except Product.DoesNotExist:
        return http.HttpResponseNotFound(json_encode(('', _("not available"))), mimetype="text/javascript")

    prod_slug = product.slug

    if request.method == "POST" and request.POST.has_key('quantity'):
        quantity = int(request.POST['quantity'])

    if 'ConfigurableProduct' in product.get_subtypes():
        cp = product.configurableproduct
        chosen_options = optionset_from_post(cp, request.POST)
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
        product = Product.objects.get(active=True, slug=product_slug)
        found = True

        prod_slug = product.slug

        if reqdata.has_key('quantity'):
            quantity = int(reqdata['quantity'])
        else:
            quantity = 1

        if 'ConfigurableProduct' in product.get_subtypes():
            cp = product.configurableproduct
            chosen_options = optionset_from_post(cp, reqdata)
            product = cp.get_product_from_options(chosen_options)

        if product:
            price = product.get_qty_price(quantity)
            base_tax = get_tax(request.user, product, quantity)
            price_with_tax = price+base_tax

            results['slug'] = product.slug
            results['currency_price'] = moneyfmt(price)
            results['price'] = float(price)
            results['tax'] = float(base_tax)
            results['currency_tax'] = moneyfmt(base_tax)
            results['currency_price_with_tax'] = moneyfmt(price_with_tax)
            results['price_with_tax'] = float(price_with_tax)
            results['success'] = True
            results['message'] = ""

    except Product.DoesNotExist:
        found = False

    data = json_encode(results)
    if found:
        return http.HttpResponse(data, mimetype="text/javascript")
    else:
        return http.HttpResponseNotFound(data, mimetype="text/javascript")


def do_search(request):
    if request.GET:
        keywords = request.GET.get('keywords', '').split(' ')
    else:
        keywords = request.POST.get('keywords', '').split(' ')

    keywords = filter(None, keywords)

    if not keywords:
        return render_to_response('search.html', RequestContext(request))

    categories = Category.objects
    products = Product.objects.active()
    for keyword in keywords:
        categories = categories.filter(
            Q(name__icontains=keyword) |
            Q(meta__icontains=keyword) |
            Q(description__icontains=keyword))
        products = products.filter(Q(name__icontains=keyword)
            | Q(short_description__icontains=keyword)
            | Q(description__icontains=keyword)
            | Q(meta__icontains=keyword)
            | Q(sku__iexact=keyword))
    clist = list(categories)
    plist = [p for p in products if not p.has_variants]

    context = RequestContext(request, {'results': {'categories': clist, 'products': plist}})
    return render_to_response('search.html', context)

def get_configurable_product_options(request, id):
    cp = get_object_or_404(ConfigurableProduct, product__id=id)
    options = ''
    for og in cp.option_group.all():
        for opt in og.option_set.all():
            options += '<option value="%s">%s</option>' % (opt.id, str(opt))
    if not options:
        return '<option>No valid options found in "%s"</option>' % cp.product.slug
    return http.HttpResponse(options, mimetype="text/html")

def display_featured():
    """
    Used by the index generic view to choose how the featured products are displayed.
    Items can be displayed randomly or all in order
    """
    random_display = config_value('SHOP','RANDOM_FEATURED')
    num_to_display = config_value('SHOP','NUM_DISPLAY')
    if not random_display:
        return(Product.objects.filter(active=True).filter(featured=True))[:num_to_display]
    else:
        return(Product.objects.filter(active=True).filter(featured=True).order_by('?')[:num_to_display])

