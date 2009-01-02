"""
Useful signals:

 - `collect_urls`: send by urls modules to allow listeners to add urls to that module::
 
   Ex: collect_urls.send(sender=MODULE, patterns=urlpatterns)
"""
import django.dispatch

collect_urls = django.dispatch.Signal()
