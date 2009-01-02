"""Product queries using ratings."""
from django.contrib.comments.models import Comment
from django.contrib.sites.models import Site
from keyedcache import cache_get, cache_set, NotCachedError
from livesettings import config_value
from product.models import Product
from satchmo_ext.productratings.utils import average
import logging
import math

log = logging.getLogger('product.comments.queries')

def highest_rated(count=0, site=None):
    """Get the most highly rated products"""
    if site is None:
        site = Site.objects.get_current()

    site_id = site.id

    try:
        pks = cache_get("BESTRATED", site=site_id, count=count)
        pks = [pk for pk in pks.split(',')]
        log.debug('retrieved highest rated products from cache')
        
    except NotCachedError, nce:
        # here were are going to do just one lookup for all product comments

        comments = Comment.objects.filter(content_type__app_label__exact='product',
            content_type__model__exact='product',
            site__id__exact=site_id,
            productrating__rating__gt=0,
            is_public__exact=True).order_by('object_pk')
        
        # then make lists of ratings for each
        commentdict = {}
        for comment in comments:
            if hasattr(comment, 'productrating'):
                rating = comment.productrating.rating
                if rating>0:
                    commentdict.setdefault(comment.object_pk, []).append(rating)
        
        # now take the average of each, and make a nice list suitable for sorting
        ratelist = [(average(ratings), int(pk)) for pk, ratings in commentdict.items()]
        ratelist.sort()
        #log.debug(ratelist)
        
        # chop off the highest and reverse so highest is the first
        ratelist = ratelist[-count:]
        ratelist.reverse()

        pks = ["%i" % p[1] for p in ratelist]
        pkstring = ",".join(pks)
        log.debug('calculated highest rated products, set to cache: %s', pkstring)
        cache_set(nce.key, value=pkstring)
    
    if pks:
        pks = [pk for pk in pks if _int_or_long(pk)]
        productdict = Product.objects.in_bulk(pks)
        products = []
        for pk in pks:
            try:
                if (int(pk)) in productdict:
                    key = int(pk)
                elif long(pk) in productdict:
                    key = long(pk)
                else:
                    continue
                products.append(productdict[key])
            except ValueError:
                pass
    else:
        products = []
        
    return products
        
        
def _int_or_long(v):
    try:
        v = int(v)
    except ValueError:
        try:
            v = long(v)
        except ValueError:
            return False
    return True