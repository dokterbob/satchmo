"""
Useful signals:

 - `collect_urls`: send by urls modules to allow listeners to add urls to that module::
 
   Ex: collect_urls.send(sender=MODULE, patterns=urlpatterns)
   
 - `form_initialdata`: send by forms when collecting initial data::
 
   Ex: form_initialdata(sender=FORM, [arg=val, arg2=val2, ...])
"""
import django.dispatch

collect_urls = django.dispatch.Signal()

form_initialdata = django.dispatch.Signal()