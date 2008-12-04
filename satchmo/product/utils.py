from satchmo.configuration import config_value
from satchmo.discount.utils import calc_by_percentage, find_best_auto_discount
from satchmo.l10n.utils import moneyfmt
from satchmo.product.models import ProductVariation, Option, split_option_unique_id, ProductPriceLookup, OptionGroup
from satchmo.shop.models import Config
from satchmo.tax.utils import get_tax_processor
import logging

log = logging.getLogger('product.utils')

def get_taxprocessor(user):
    if user.is_authenticated():
        user = user
    else:
        user = None

    return get_tax_processor(user=user)

def get_tax(user, product, quantity):
    taxer = get_taxprocessor(user)
    return taxer.by_product(product, quantity)

def productvariation_details(product, include_tax, user, create=False):
    """Build the product variation details, for conversion to javascript.

    Returns variation detail dictionary built like so:
    details = {
        "OPTION_KEY" : {
            "SLUG": "Variation Slug",
            "PRICE" : {"qty" : "$price", [...]},
            "SALE" : {"qty" : "$price", [...]},
            "TAXED" : "$taxed price",   # omitted if no taxed price requested
            "QTY" : 1
        },
        [...]
    }
    """

    config = Config.objects.get_current()
    ignore_stock = config.no_stock_checkout
    discount = find_best_auto_discount(product)
    use_discount = discount and discount.percentage > 0

    if include_tax:
        taxer = get_taxprocessor(user)
        tax_class = product.taxClass

    details = {'SALE' : use_discount}
    
    curr = config_value('SHOP', 'CURRENCY')
    curr = curr.replace("_", " ")

    variations = ProductPriceLookup.objects.filter(parentid=product.id)
    if variations.count() == 0:
        if create:
            log.debug('Creating price lookup for %s', product)
            ProductPriceLookup.objects.smart_create_for_product(product)
            variations = ProductPriceLookup.objects.filter(parentid=product.id)
        else:
            log.warning('You must run satchmo_rebuild_pricing and add it to a cron-job to run every day, or else the product details will not work for product detail pages.')
    for detl in variations:
        key = detl.key
        if details.has_key(key):
            detail = details[key]
        else:
            detail = {}
            detail['SLUG'] = detl.productslug

            if not detl.active:
                qty = -1
            elif ignore_stock:
                qty = 10000
            else:
                qty = detl.items_in_stock

            detail['QTY'] = qty

            detail['PRICE'] = {}
            
            if use_discount:
                detail['SALE'] = {}
                
            if include_tax:
                detail['TAXED'] = {}
                if use_discount:
                    detail['TAXED_SALE'] = {}
                
            details[key] = detail
        
        price = detl.dynamic_price
        
        detail['PRICE'][detl.quantity] = moneyfmt(price, curr=curr)
        if use_discount:
            detail['SALE'][detl.quantity] = moneyfmt(calc_by_percentage(price, discount.percentage), curr=curr)
        
        if include_tax:
            tax_price = taxer.by_price(tax_class, price) + price
            detail['TAXED'][detl.quantity] = moneyfmt(tax_price, curr=curr)
            detail['TAXED_SALE'][detl.quantity] = moneyfmt(calc_by_percentage(tax_price, discount.percentage), curr=curr)
                
    return details

def serialize_options(product, selected_options=()):
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
    all_options = product.get_valid_options()
    group_sortmap = OptionGroup.objects.get_sortmap()

    # first get all objects
    # right now we only have a list of option.unique_ids, and there are
    # probably a lot of dupes, so first list them uniquely
    values = []
    
    if all_options != [[]]:
        vals = {}
        groups = {}
        opts = {}
        serialized = {}
        
        for options in all_options:
            for option in options:
                if not opts.has_key(option):
                    k, v = split_option_unique_id(option)
                    vals[v] = False
                    groups[k] = False
                    opts[option] = None
        
        for option in Option.objects.filter(option_group__id__in = groups.keys(), value__in = vals.keys()):
            uid = option.unique_id
            if opts.has_key(uid):
                opts[uid] = option

        # now we have all the objects in our "opts" dictionary, so build the serialization dict

        for option in opts.values():
            if not serialized.has_key(option.option_group_id):
                serialized[option.option_group.id] = {
                    'name': option.option_group.translated_name(),
                    'id': option.option_group.id,
                    'items': [],
                }
            if not option in serialized[option.option_group_id]['items']:
                serialized[option.option_group_id]['items'] += [option]
                option.selected = option.unique_id in selected_options

        # first sort the option groups
        for k, v in serialized.items():
            values.append((group_sortmap[k], v))
        
        values.sort()
        values = zip(*values)[1]

        #now go back and make sure option items are sorted properly.
        for v in values:
            v['items'] = _sort_options(v['items'])
    
    log.debug('serialized: %s', values)
    
    log.debug('Serialized Options %s: %s', product.product.slug, values)
    return values


def _sort_options(lst):
    work = [(opt.sort_order, opt) for opt in lst] 
    work.sort()
    return zip(*work)[1]
    