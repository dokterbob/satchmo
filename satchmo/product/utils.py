from satchmo import tax
from satchmo.l10n.utils import moneyfmt
from satchmo.product.models import ProductVariation
from satchmo.shop.models import Config

def get_taxprocessor(user):
    if user.is_authenticated():
        user = user
    else:
        user = None

    return tax.get_processor(user=user)

def get_tax(user, product, quantity):
    taxer = get_taxprocessor(user)
    return taxer.by_product(product, quantity)

def productvariation_details(product, include_tax, user):
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
        taxer = get_taxprocessor(user)
        tax_class = product.taxClass

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
                tax_price = taxer.by_price(tax_class, price) + price
                taxed[qty] = moneyfmt(tax_price)

        detail['PRICE'] = base
        if include_tax:
            detail['TAXED'] = taxed

        # build option map
        opts = [(opt.id, opt.value) for opt in p.options.order_by('optionGroup')]
        optkey = "::".join([opt[1] for opt in opts])
        details[optkey] = detail

    return details

def serialize_options(product, selected_options=set()):
    """
    Return a list of optiongroups and options for display to the customer.
    Only returns options that are actually used by members of this product.

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

    all_options = product.get_valid_options()

    for options in all_options:
        for option in options:
            if not d.has_key(option.optionGroup_id):
                d[option.optionGroup.id] = {
                    'name': option.optionGroup.translated_name(),
                    'id': option.optionGroup.id,
                    'items': [],
                }
            if not option in d[option.optionGroup_id]['items']:
                d[option.optionGroup_id]['items'] += [option]
                option.selected = option.unique_id in selected_options

    return d.values()
