"""Utility functions used by signals to attach Ratings to Comments"""
from django.contrib.comments.models import Comment
from django.contrib.sites.models import Site
from django.core import urlresolvers
from django.utils.encoding import smart_str
from livesettings import config_value
from models import ProductRating
from product.models import Product
from satchmo_utils import url_join
import logging
from django.conf import settings

log = logging.getLogger('productratings')

def save_rating(comment=None, request=None, **kwargs):
    """Create a rating and save with the comment"""
    
    # should always be true
    if request.method != "POST":
        return
    
    data = request.POST.copy()
    if 'rating' not in data:
        return
    
    raw = data['rating']
    try:
        rating = int(raw)
    except ValueError:
        log.error('Could not parse rating from posted rating: %s', raw)
        return
        
    if comment.content_type.app_label == "product" and comment.content_type.model == "product":
        if hasattr(comment, 'rating'):
            log.debug('editing existing comment %s, setting rating=%i', comment, rating)
            productrating = comment.rating
            productrating.rating = rating
    
        else:
            log.debug("Creating new rating for comment: %s = %i", comment, rating)
            p = Product.objects.get(pk=comment.object_pk)
            productrating = ProductRating(comment=comment, rating=rating)
        
            productrating.save()
    else:
        log.debug('Not saving rating for comment on a %s object', comment.content_type.model)
    
def one_rating_per_product(comment=None, request=None, **kwargs):
    site = Site.objects.get_current()
    comments = Comment.objects.filter(object_pk__exact=comment.object_pk,
                               content_type__app_label__exact='product',
                               content_type__model__exact='product',
                               site__exact=site,
                               is_public__exact=True,
                               user__exact=request.user)
                               
    for c in comments:
        if not c == comment:
            c.delete()            

def check_with_akismet(comment=None, request=None, **kwargs):
    if config_value("PRODUCT", "AKISMET_ENABLE"):
        key = config_value("PRODUCT", "AKISMET_KEY")
        if key:             
            site = Site.objects.get_current()
            shop = urlresolvers.reverse('satchmo_shop_home')
            from akismet import Akismet
            akismet = Akismet(
                key=settings.AKISMET_API_KEY,
                blog_url='http://%s' % url_join(site.domain, shop))
            if akismet.verify_key():
                akismet_data = { 'comment_type': 'comment',
                                 'referrer': request.META.get('HTTP_REFERER', ""),
                                 'user_ip': comment.ip_address,
                                 'user_agent': '' }
                if akismet.comment_check(smart_str(comment.comment), data=akismet_data, build_data=True):
                    comment.is_public=False
                    comment.save()
                    log.info("Akismet marked comment #%i as spam", comment.id)
                else:
                    log.debug("Akismet accepted comment #%i", comment.id)
            else:
                log.warn("Akismet key '%s' not accepted by akismet service.", key)
        else:
            log.info("Akismet enabled, but no key found.  Please put in your admin settings.")
