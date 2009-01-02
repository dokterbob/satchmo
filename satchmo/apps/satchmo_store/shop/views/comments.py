"""Satchmo product rating views"""
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.comments.models import Comment
from django.contrib.comments.views.comments import post_comment
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect, Http404
from django.contrib.sites.models import Site

from logging import getLogger

log = getLogger('satchmo_store.shop.views.ratings')

def post_rating(request, url='/ratings/posted/', maxcomments=1):
    """Wrap django.contrib.comments.views.comments.post_comment, so that we can control where the user
    is returned after submit, also add the ability to control the maximum number of ratings per user 
    per product.
    """
    if request.method != "POST":
        raise Http404, _("One or more of the required fields wasn't submitted")
        
    if request.POST.has_key('url'):
        url = request.POST['url']
        
    response = post_comment(request)

    if maxcomments > 0 and not request.user.is_anonymous():
        try:
            target = request.POST['target']
        except KeyError:
            raise Http404, _("One or more of the required fields wasn't submitted")
            
        content_type_id, object_id = target.split(':')
        
        try:
            ct = ContentType.objects.get(pk=content_type_id)
        except ContentType.DoesNotExist:
            raise Http404, _("Bad ContentType: %s" % content_type_id)
        
        comments = Comment.objects.filter(object_id__exact=object_id,
            content_type__app_label__exact=ct.app_label,
            content_type__model__exact=ct.model,
            site__exact=Site.objects.get_current(),
            is_public__exact=True,
            user__exact=request.user.id).order_by('submit_date')
            
        ct = len(comments)
        if ct > maxcomments:
            log.debug("Got %i comments for user - removing all but %i", ct, maxcomments)
            for c in comments:
                c.delete()
                ct -= 1
                if ct == maxcomments: break
    
    return HttpResponseRedirect(url)
