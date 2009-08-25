from keyedcache import cache_get, cache_set, NotCachedError
from product.models import Product
import logging

log = logging.getLogger('product.queries')

def bestsellers(count):
    """Look up the bestselling products and return in a list"""        
    sellers = []
    cached = False
    try:
        pks = cache_get('BESTSELLERS', count=count)
        if pks:
            pks = [long(pk) for pk in pks.split(',')]
            productdict = Product.objects.in_bulk(pks)
            #log.debug(productdict)
            for pk in pks:
                try:
                    if (int(pk)) in productdict:
                        key = int(pk)
                    elif long(pk) in productdict:
                        key = long(pk)
                    else:
                        continue
                    sellers.append(productdict[key])
                except ValueError:
                    pass
            
            log.debug('retrieved bestselling products from cache')
        cached = True    
    except NotCachedError:
        pass
    
    except ValueError:
        pass

    if not cached:
        products = Product.objects.active_by_site()
        work = []
        for p in products:
            ct = p.orderitem_set.count()
            if ct>0:
                work.append((ct, p))
        
        work.sort()
        work = work[-count:]
        work.reverse()
    
        sellers = []
        pks = []
    
        for p in work:
            product = p[1]
            pks.append("%i" % product.pk)
            sellers.append(product)
         
        pks = ",".join(pks)
        log.debug('calculated bestselling %i products, set to cache: %s', count, pks)
        cache_set('BESTSELLERS', count=count, value=pks)
        
    return sellers
