from django.shortcuts import render_to_response
from django.template import RequestContext

def example(request):
    ctx = RequestContext(request, {})
    return render_to_response('localsite/example.html', context_instance=ctx)
