from django import newforms as forms
from django.conf import settings
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.decorators import user_passes_test
from django.core import urlresolvers
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from satchmo.caching.models import *
import logging

log = logging.getLogger('caching.views')

class CacheDeleteForm(forms.Form):
    tag = forms.CharField('Key to delete', required=False)
    children = forms.BooleanField('Include Children?', initial=True)
    kill_all = forms.BooleanField('Delete all keys?', initial=False)
    
    def delete_cache(self):
        
        data = self.cleaned_data
        if data['kill_all']:
            caching.cache_delete()
            result = "Deleted all keys"
        elif data['tag']:
            caching.cache_delete(data['tag'], children=data['children'])
            if data['children']:
                result = "Deleted %s and children" % data['tag']
            else:
                result = "Deleted %s" % data['tag']
        else:
            result = "Nothing selected to delete"
        
        log.debug(result)
        return result

@user_passes_test(lambda u: u.is_authenticated() and u.is_staff, login_url='/accounts/login/')
def stats_page(request):
    calls = caching.CACHE_CALLS
    hits = caching.CACHE_HITS
    
    if (calls and hits):
        rate =  float(caching.CACHE_HITS)/caching.CACHE_CALLS*100
    else:
        rate = 0
        
    try:
        running = caching.cache_require()
        
    except caching.CacheNotRespondingError:
        running = False
        
    ctx = RequestContext(request, {
        'cache_count' : len(caching.CACHED_KEYS),
        'cache_running' : running,
        'cache_time' : settings.CACHE_TIMEOUT,
        'cache_backend' : settings.CACHE_BACKEND,
        'cache_calls' : caching.CACHE_CALLS,
        'cache_hits' : caching.CACHE_HITS,
        'hit_rate' : "%02.1f" % rate
    })
    
    return render_to_response('caching/stats.html', ctx)
    
@user_passes_test(lambda u: u.is_authenticated() and u.is_staff, login_url='/accounts/login/')    
def view_page(request):
    keys = caching.CACHED_KEYS.keys()
    
    keys.sort()
    
    ctx = RequestContext(request, { 
        'cached_keys' : keys,
    })
    
    return render_to_response('caching/view.html', ctx)

@user_passes_test(lambda u: u.is_authenticated() and u.is_staff, login_url='/accounts/login/')
def delete_page(request):
    log.debug("delete_page")
    if request.method == "POST":
        form = CacheDeleteForm(request.POST)
        if form.is_valid():
            log.debug('delete form valid')
            results = form.delete_cache()
            url = urlresolvers.reverse('caching_stats')
            return HttpResponseRedirect(url)
        else:
            log.debug("Errors in form: %s", form.errors)
    else:
        log.debug("new form")
        form = CacheDeleteForm()
            
    ctx = RequestContext(request, { 
        'form' : form,
    })
    
    return render_to_response('caching/delete.html', ctx)

