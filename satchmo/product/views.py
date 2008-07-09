import logging
from django import http
from django.db.models import Q
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.template.loader import select_template
from django.utils.translation import ugettext as _
from satchmo import tax
from satchmo.configuration import config_value
from satchmo.discount.utils import find_best_auto_discount
from satchmo.l10n.utils import moneyfmt
from satchmo.product.models import Category, Product, ConfigurableProduct, ProductVariation
from satchmo.shop.models import Config
from satchmo.shop.utils.json import json_encode
from satchmo.shop.views.utils import bad_or_missing

try:
    set
except NameError:
    from sets import Set as set     #python 2.3 fallback

log = logging.getLogger('product.views')

NOTSET = object()

def find_product_template(product, producttypes=None):
    if producttypes is None:
        producttypes = product.get_subtypes()

    templates = ["product/detail_%s.html" % x.lower() for x in producttypes]
    templates.append('base_product.html')
    return select_template(templates)

def serialize_options(config_product, selected_options=set()):
    """
    Return a list of optiongroups and options for display to the customer.
    Only returns options that are actually used by members of this ConfigurableProduct.

    Return Value:
    [
    {
    name: 'group name',
    id: 'group id',
    items: [{
        name: 'opt name',
        value: 'opt value',
        price_change: 'opt price',
        selected: False,
        },{..}]
    },
    {..}
    ]

    Note: This doesn't handle the case where you have multiple options and
    some combinations aren't available. For example, you have option_groups
    color and size, and you have a yellow/large, a yellow/small, and a
    white/small, but you have no white/large - the customer will still see
    the options white and large.
    """
    d = {}

    all_options = config_product.get_valid_options()

    for options in all_options:
        for option in options:
            if not d.has_key(option.optionGroup_id):
                d[option.optionGroup.id] = {
                        'name': option.optionGroup.translated_name(),
                        'id': option.optionGroup.id,
                        'items': []
                        }
            if not option in d[option.optionGroup_id]['items']:
                d[option.optionGroup_id]['items'] += [option]
                option.selected = option.unique_id in selected_options

    return d.values()

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

    p_types = product.get_subtypes()

    options = []
    details = None

    if default_view_tax:
        include_tax = True

    if 'ProductVariation' in p_types:
        selected_options = product.productvariation.option_values
        #Display the ConfigurableProduct that this ProductVariation belongs to.
        product = product.productvariation.parent.product
        p_types = product.get_subtypes()

    if 'ConfigurableProduct' in p_types:
        options = serialize_options(product.configurableproduct, selected_options)
        details = _productvariation_details(product, include_tax, request.user)

    if 'CustomProduct' in p_types:
        options = serialize_options(product.customproduct, selected_options)

    template = find_product_template(product, producttypes=p_types)

    sale = find_best_auto_discount(product)

    attributes = {
        'product': product,
        'options': options,
        'details': details,
        'default_view_tax': default_view_tax,
        'sale' : sale,
    }

    if include_tax:
        tax_amt = _get_tax(request.user, product, 1)
        attributes['product_tax'] = tax_amt
        attributes['price_with_tax'] = product.unit_price+tax_amt

    ctx = RequestContext(request, attributes)
    return http.HttpResponse(template.render(ctx))

def optionset_from_post(configurableproduct, POST):
    chosenOptions = set()
    for opt_grp in configurableproduct.option_group.all():
        if POST.has_key(str(opt_grp.id)):
            chosenOptions.add('%s-%s' % (opt_grp.id, POST[str(opt_grp.id)]))
    return chosenOptions

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
        chosenOptions = optionset_from_post(cp, request.POST)
        pvp = cp.get_product_from_options(chosenOptions)

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
            chosenOptions = optionset_from_post(cp, reqdata)
            product = cp.get_product_from_options(chosenOptions)

        if product:
            price = product.get_qty_price(quantity)
            base_tax = _get_tax(request.user, product, quantity)
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

def _get_taxprocessor(user):
    if user.is_authenticated():
        user = user
    else:
        user = None

    return tax.get_processor(user=user)

def _get_tax(user, product, quantity):
    taxer = _get_taxprocessor(user)
    return taxer.by_product(product, quantity)

def _productvariation_details(product, include_tax, user):
    """Build the product variation details, for conversion to javascript.

    Returns variation detail dictionary built like so:
    details = {
        "OPTION_KEY" : {
            "SLUG": "Variation Slug",
            "PRICE" : {"qty" : "$price", [...]},
            "TAXED" : "$taxed price",   # omitted if no taxed price requested
            "QTY" : 1
        },
        [...]
    }
    """

    config = Config.get_shop_config()
    ignore_stock = config.no_stock_checkout

    if include_tax:
        taxer = _get_taxprocessor(user)
        taxclass = product.taxClass

    details = {}

    for p in ProductVariation.objects.by_parent(product):

        detail = {}

        prod = p.product
        detail['SLUG'] = prod.slug

        if not prod.active:
            qty = -1
        elif ignore_stock:
            qty = 10000
        else:
            qty = prod.items_in_stock

        detail['QTY'] = qty

        base = {}
        if include_tax:
            taxed = {}

        for qty, price in p.get_qty_price_list():
            base[qty] = moneyfmt(price)
            if include_tax:
                taxprice = taxer.by_price(taxclass, price) + price
                taxed[qty] = moneyfmt(taxprice)

        detail['PRICE'] = base
        if include_tax:
            detail['TAXED'] = taxed

        # build option map
        opts = [(opt.id, opt.value) for opt in p.options.order_by('optionGroup')]
        optkey = "::".join([opt[1] for opt in opts])
        details[optkey] = detail

    return details
