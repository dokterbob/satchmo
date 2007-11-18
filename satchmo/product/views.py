from django import http
from django.db.models import Q
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.template.loader import select_template
from django.utils import simplejson
from django.utils.translation import ugettext as _
from satchmo.product.models import Category, Product, ConfigurableProduct
from satchmo.shop.templatetags.satchmo_currency import moneyfmt
from satchmo.shop.views.utils import bad_or_missing
from sets import Set
import logging

log = logging.getLogger('product.views')

def find_product_template(product, producttypes=None):
    if producttypes is None:
        producttypes = product.get_subtypes()
    
    templates = ["product/detail_%s.html" % x.lower() for x in producttypes]
    templates.append('base_product.html')
    return select_template(templates)

def serialize_options(config_product, selected_options=Set()):
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
    for options in config_product.get_valid_options():
        for option in options:
            if not d.has_key(option.optionGroup_id):
                d[option.optionGroup.id] = {
                        'name': option.optionGroup.name,
                        'id': option.optionGroup.id,
                        'items': []
                        }
            if not option in d[option.optionGroup_id]['items']:
                d[option.optionGroup_id]['items'] += [option]
                option.selected = option.unique_id in selected_options
    return d.values()

def get_product(request, product_slug, selected_options=Set()):
    try:
        product = Product.objects.get(active=True, slug=product_slug)
    except Product.DoesNotExist:
        return bad_or_missing(request, _('The product you have requested does not exist.'))

    p_types = product.get_subtypes()

    options = []

    if 'ProductVariation' in p_types:
        selected_options = product.productvariation.option_values
        #Display the ConfigurableProduct that this ProductVariation belongs to.
        product = product.productvariation.parent.product
        p_types = product.get_subtypes()

    if 'ConfigurableProduct' in p_types:
        options = serialize_options(product.configurableproduct, selected_options)
    
    if 'CustomProduct' in p_types:
        options = serialize_options(product.customproduct, selected_options)

    template = find_product_template(product, producttypes=p_types)
    ctx = RequestContext(request, {'product': product, 'options': options})
    return http.HttpResponse(template.render(ctx))

def optionset_from_post(configurableproduct, POST):
    chosenOptions = Set()
    for opt_grp in configurableproduct.option_group.all():
        if POST.has_key(str(opt_grp.id)):
            chosenOptions.add('%s-%s' % (opt_grp.id, POST[str(opt_grp.id)]))
    return chosenOptions

def get_price(request, product_slug):
    quantity = 1

    try:
        product = Product.objects.get(active=True, slug=product_slug)
    except Product.DoesNotExist:
        return http.HttpResponseNotFound(simplejson.dumps(('', _("not available"))), mimetype="text/javascript")

    prod_slug = product.slug

    if request.POST.has_key('quantity'):
        quantity = int(request.POST['quantity'])

    if 'ConfigurableProduct' in product.get_subtypes():
        cp = product.configurableproduct
        chosenOptions = optionset_from_post(cp, request.POST)
        pvp = cp.get_product_from_options(chosenOptions)

        if not pvp:
            return http.HttpResponse(simplejson.dumps(('', _("not available"))), mimetype="text/javascript")
        prod_slug = pvp.slug
        price = moneyfmt(pvp.get_qty_price(quantity))
    else:
        price = moneyfmt(product.get_qty_price(quantity))

    if not price:
        return http.HttpResponse(simplejson.dumps(('', _("not available"))), mimetype="text/javascript")

    return http.HttpResponse(simplejson.dumps((prod_slug, price)), mimetype="text/javascript")

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
        categories = categories.filter(Q(name__icontains=keyword) | Q(meta__icontains=keyword) | Q(description__icontains=keyword))
        products = products.filter(Q(name__icontains=keyword) | Q(short_description__icontains=keyword) | Q(description__icontains=keyword) | Q(meta__icontains=keyword))
    clist = []
    plist = []
    for category in categories:
        clist.append(category)
    for product in products:
        # we only want to see the master products not each variation of the product
        if not product.has_variants:
            plist.append(product)

    context = RequestContext(request, {'results': {'categories': clist, 'products': plist}})
    return render_to_response('search.html', context)

def getConfigurableProductOptions(request, id):
    cp = get_object_or_404(ConfigurableProduct, product__id=id)
    options = ''
    for og in cp.option_group.all():
        for opt in og.option_set.all():
            options += '<option value="%s">%s</option>' % (opt.id, str(opt))
    if not options:
        return '<option>No valid options found in "%s"</option>' % cp.product.slug
    return http.HttpResponse(options, mimetype="text/html")
