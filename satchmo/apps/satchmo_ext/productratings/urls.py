"""urlpatterns for productratings.  Note that you do not need to add these to your urls anywhere, they'll be automatically added by the collect_urls signals."""

from django.conf.urls.defaults import *
import logging

log = logging.getLogger('productratings.urls')

productpatterns = patterns('satchmo_ext.productratings.views',
    (r'^view/bestrated/$', 
        'display_bestratings', {}, 'satchmo_product_best_rated'),
)

# Override comments with our redirecting view. You can remove the next two
# URLs if you aren't using ratings.
#(r'^comments/post/$', 'comments.post_rating', {'maxcomments': 1 }, 'satchmo_rating_post'),
commentpatterns = patterns('',
    (r'^comments/', include('django.contrib.comments.urls')),
)

def add_product_urls(sender, patterns=(), section="", **kwargs):
    if section=="product":
        log.debug('adding ratings urls')
        patterns += productpatterns

def add_comment_urls(sender, patterns=(), **kwargs):
    log.debug('adding comments urls')
    patterns += commentpatterns
