from decimal import Decimal
from django.utils.translation import ugettext_lazy as _
from satchmo_store.shop.exceptions import CartAddProhibited
import logging

log = logging.getLogger('upsell.views')

def cart_add_listener(cart=None, product=None, form=None, request=None, **kwargs):
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
    field_include = "upsell_include_%s" % i
    field_qty = "upsell_qty_%s" % i
    field_slug = "upsell_slug_%s" % i
    slug = ""
    qty = Decimal('0')
    
    if form.get(field_include, "false") == "true":
        slug = form.get(field_slug, "")
        if slug:
            try:
                rawqty = form.get(field_qty, 0)
                if rawqty == "MATCH":
                    qty = Decimal(form['quantity'])
                else:
                    qty = Decimal(rawqty)
            except ValueError:
                log.debug('Bad upsell qty=%d', rawqty)
                qty = Decimal('0')

        if qty > 0:
            from product.models import Product
            try:
                product = Product.objects.get_by_site(slug=slug)
                
                try:
                    cart.add_item(product, number_added=qty)
                    log.info('Added upsell item: %s qty=%d', product.slug, qty)
                    return (True, product)
                                        
                except CartAddProhibited, cap:
                    vetomsg = cap.veto_messages() 
                    msg = _("'%(product)s' couldn't be added to the cart. %(details)s") % {
                        'product' : product.slug, 
                        'detail' : cap.message 
                        }
                    log.debug("Failed to add upsell item: '%s', message= %s", product.slug, msg)
                    return (False, product)
                    
            except Product.DoesNotExist:
                log.debug("Could not find product: %s", slug)
                return (False, None)
                
    return (False, None)
