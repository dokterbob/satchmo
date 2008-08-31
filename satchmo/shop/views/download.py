from django.core import urlresolvers
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import loader, RequestContext
from django.utils.translation import ugettext_lazy as _
from satchmo.shop.models import DownloadLink
import mimetypes

import os
import os.path
import re

SHA1_RE = re.compile('^[a-f0-9]{40}$')

def _validate_key(download_key):
    """
    Helper function to make sure the key is valid and all the other constraints on
    the download are still valid.
    Returns a tuple (False,"Error Message", None) or (True, None, dl_product)
    """
    download_key = download_key.lower()
    if not SHA1_RE.search(download_key):
        error_message = _("The download key is invalid.")
        return (False, error_message, None)
    try:
        dl_product = DownloadLink.objects.get(key=download_key)
    except:
        error_message = _("The download key is invalid.")
        return (False, error_message, None)
    valid, msg = dl_product.is_valid()
    if not valid:
        return (False, msg, None)
    else:
        return (True, None, dl_product)
    
def process(request, download_key):
    """
    Validate that the key is good, then set a session variable.
    Redirect to the download view.
    
    We use this two step process so that we can easily display meaningful feedback
    to the user.   
    """
    valid, msg, dl_product = _validate_key(download_key)
    if not valid:
        context = RequestContext(request, {'error_message': msg})
        return render_to_response('download.html', context)
    else:
        # The key is valid so let's set the session variable and redirect to the 
        # download view
        request.session['download_key'] = download_key
        url = urlresolvers.reverse('satchmo_download_send', kwargs= {'download_key': download_key})
        context = RequestContext(request, {'download_product': dl_product,
                                            'dl_url' : url})
        return render_to_response('download.html', context)
   
def send_file(request, download_key):
    """
    After the appropriate session variable has been set, we commence the download.
    The key is maintained in the url but the session variable is used to control the
    download in order to maintain security.
    
    For this to work, your server must support the X-Sendfile header
    Lighttpd and Apache should both work with the headers used below.
    For apache, will need mod_xsendfile
    For lighttpd, allow-x-send-file must be enabled
    
    Also, you must ensure that the directory where the file is stored is protected
    from users.  In lighttpd.conf:
    $HTTP["url"] =~ "^/static/protected/" {
    url.access-deny = ("")
    }
    """
    if not request.session.get('download_key', False):
        url = urlresolvers.reverse('satchmo_download_process', kwargs = {'download_key': download_key})
        return HttpResponseRedirect(url)
    valid, msg, dl_product = _validate_key(request.session['download_key'])
    if not valid:
        url = urlresolvers.reverse('satchmo_download_process', kwargs = {'download_key': request.session['download_key']})
        return HttpResponseRedirect(url)
    file_name = os.path.split(dl_product.downloadable_product.file.path)[1]
    dl_product.num_attempts += 1
    dl_product.save()
    del request.session['download_key']
    response = HttpResponse()
    response['X-Sendfile'] = dl_product.downloadable_product.file.path
    response['X-LIGHTTPD-send-file'] = dl_product.downloadable_product.file.path
    response['Content-Disposition'] = "attachment; filename=%s" % file_name
    response['Content-length'] =  os.stat(dl_product.downloadable_product.file.path).st_size
    contenttype, encoding = mimetypes.guess_type(file_name)
    if contenttype:
        response['Content-type'] = contenttype
    return response
