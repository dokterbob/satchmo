from django.conf import settings
from django.contrib.comments.models import Comment, FreeComment
from django.utils.translation import ugettext_lazy as _
from models import Product
from satchmo.caching import cache_get, cache_set, NotCachedError
from satchmo.configuration import config_value
from django.contrib.sites.models import Site
import logging
import math
import operator

log = logging.getLogger('product.comments')

def average(ratings):
    """ Average a list of numbers, return None if it fails """
    total = reduce(operator.add, ratings)
    if(total == None):
        return None
    return float(total)/len(ratings)


def get_product_rating(product, free=False, site=None):
    """Get the average product rating"""
    if site is None:
        site = Site.objects.get_current()
    
    site = site.id
        
    manager = free and FreeComment.objects or Comment.objects
    comments = manager.filter(object_id__exact=product.id,
                               content_type__app_label__exact='product',
                               content_type__model__exact='product',
                               site__id__exact=site,
                               is_public__exact=True)
    ratings = [comment.rating1 for comment in comments]
    #log.debug(ratings)
    if ratings:
        return average(ratings)
    
    else:
        return None

def get_product_rating_string(product, free=False, site=None):
    """Get the average product rating as a string, for use in templates"""
    rating = get_product_rating(product, free=free, site=site)
    
    if rating is not None:
        rating = "%0.1f" % rating
        if rating.endswith('.0'):
            rating = rating[0]
        rating = rating + "/5"
    else:
        rating = _('Not Rated')
        
    return rating
    
def highest_rated(num=None, free=False, site=None):
    """Get the most highly rated products"""
    if site is None:
        site = Site.objects.get_current()

    site = site.id

    try:
        pks = cache_get("BESTRATED", site=site, free=free, num=num)
        pks = [pk for pk in pks.split(',')]
        log.debug('retrieved highest rated products from cache')
        
    except NotCachedError, nce:
        # here were are going to do just one lookup for all product comments
        manager = free and FreeComment.objects or Comment.objects
        comments = manager.filter(content_type__app_label__exact='product',
                                   content_type__model__exact='product',
                                   site__id__exact=site,
                                   is_public__exact=True).order_by('object_id')
        
        # then make lists of ratings for each
        commentdict = {}
        for comment in comments:
            commentdict.setdefault(comment.object_id, []).append(comment.rating1)
        
        # now take the average of each, and make a nice list suitable for sorting
        ratelist = [(average(ratings), pk) for pk, ratings in commentdict.items()]
        ratelist.sort()
        #log.debug(ratelist)
        
        # chop off the highest and reverse so highest is the first
        if num is None:
            num = config_value('SHOP', 'NUM_DISPLAY')
        ratelist = ratelist[-num:]
        ratelist.reverse()

        pks = ["%i" % p[1] for p in ratelist]
        pkstring = ",".join(pks)
        log.debug('calculated highest rated products, set to cache: %s', pkstring)
        cache_set(nce.key, value=pkstring)
    
    if pks:
        pks = [pk for pk in pks if _is_int(pk)]
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
        
        
def _is_int(v):
    try:
        v = int(v)
        return True
    except ValueError:
        return False
