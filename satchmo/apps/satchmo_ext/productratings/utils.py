from django.conf import settings
from django.contrib.comments.models import Comment
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _
import logging
import operator

log = logging.getLogger('product.comments.utils')

def average(ratings):
    """ Average a list of numbers, return None if it fails """
    ratings = filter(lambda x: x is not None, ratings)
    total = reduce(operator.add, ratings)
    if(total == None):
        return None
    return float(total)/len(ratings)


def get_product_rating(product, site=None):
    """Get the average product rating"""
    if site is None:
        site = Site.objects.get_current()
    
    site = site.id
    manager = Comment.objects
    comments = manager.filter(object_pk__exact=str(product.id),
                               content_type__app_label__exact='product',
                               content_type__model__exact='product',
                               site__id__exact=site,
                               is_public__exact=True)
    ratings = []
    for comment in comments:
        if hasattr(comment,'productrating'):
            rating = comment.productrating.rating
            if rating > 0:
                ratings.append(rating)

    log.debug("Ratings: %s", ratings)
    if ratings:
        return average(ratings)
    
    else:
        return None

def get_product_rating_string(product, site=None):
    """Get the average product rating as a string, for use in templates"""
    rating = get_product_rating(product, site=site)
    
    if rating is not None:
        rating = "%0.1f" % rating
        if rating.endswith('.0'):
            rating = rating[0]
        rating = rating + "/5"
    else:
        rating = _('Not Rated')
        
    return rating
    
