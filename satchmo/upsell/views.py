import logging

log = logging.getLogger('upsell.views')

def cart_add_listener(cart=None, product=None, form=None, request=None):
    """Post-processes the form, handling upsell formfields.
    
    fields (potentially) in the form:
        upsell_count: controls how many upsell formblocks to look for.
        for ix in range(0,upsell_count):
            upsell_include_ix: true if this one is to be included
            upsell_qty_ix: quantity
            upsell_slug_ix: product slug        
    """
    log.debug("cart_add_listener heard satchmo_cart_add_complete")
    try:
        rawct = form.get('upsell_count', 0)
        ct = int(rawct)
    except ValueError:
        log.debug("Got bad upsell_count: %s", rawct)
        ct = 0
        
    results = []
    if ct>0:
        for i in range(0,ct):
            results.append(_add_upsell(form, cart, i))
            
    return results
            
def _add_upsell(form, cart, i):
    field_include = "upsell_include_%i" % i
    field_qty = "upsell_qty_%i" % i
    field_slug = "upsell_slug_%i" % i
    slug = ""
    qty = 0
    
    if form.get(field_include, "false") == "true":
        slug = form.get(field_slug, "")
        if slug:
            try:
                rawqty = form.get(field_qty, 0)
                if rawqty == "MATCH":
                    qty = int(form['quantity'])
                else:
                    qty = int(rawqty)
            except ValueError:
                log.debug('Bad upsell qty=%s', rawqty)
                qty = 0

        if qty > 0:
            from satchmo.product.models import Product

            try:
                product = Product.objects.get(slug=slug)
                
                if cart.add_item(product, number_added=qty):
                    log.info('Added upsell item: %s qty=%i', product.slug, qty)
                    return (True, product)
                else:
                    log.debug('Failed to add upsell item: %s qty=%i', product.slug, qty)
                    return (False, product)
                    
            except Product.DoesNotExist:
                log.debug("Could not find product: %s", slug)
                return (False, None)
                
    return (False, None)