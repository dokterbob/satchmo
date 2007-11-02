from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.views.decorators.cache import never_cache
from satchmo.contact.models import Order
from satchmo.contact.models import ORDER_STATUS

def home(request):
    title = _("Site Administration")
    if request.GET.get('legacy', False) or not request.user.is_superuser:
        return render_to_response('admin/index.html', {'title': title}, context_instance=RequestContext(request))
    else:
        pending = unicode(ORDER_STATUS[1][1])
        inProcess = unicode(ORDER_STATUS[2][1])
        pendings =  Order.objects.filter(status=pending).order_by('timestamp')
        in_process = Order.objects.filter(status=inProcess).order_by('timestamp')
        return render_to_response('admin/portal.html', 
                                    {'pendings': pendings,
                                     'in_process': in_process,
                                     'title': title},
                                 RequestContext(request))
home = staff_member_required(never_cache(home))
