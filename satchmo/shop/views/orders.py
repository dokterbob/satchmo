from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from satchmo.contact.models import Contact
from satchmo.shop.models import Order
from satchmo.shop.views.utils import bad_or_missing

def order_history(request):
    orders = None
    try:
        contact = Contact.objects.from_request(request, create=False)
        orders = Order.objects.filter(contact=contact).order_by('-timestamp')
    
    except Contact.DoesNotExist:
        contact = None
        
    ctx = RequestContext(request, {
        'contact' : contact,
        'orders' : orders})

    return render_to_response('contact/order_history.html', ctx)

order_history = login_required(order_history)

def order_tracking(request, order_id):
    order = None
    try:
        contact = Contact.objects.from_request(request, create=False)
        try:
            order = Order.objects.get(id__exact=order_id, contact=contact)
        except Order.DoesNotExist:
            pass
    except Contact.DoesNotExist:
        contact = None

    if order is None:
        return bad_or_missing(request, _("The order you have requested doesn't exist, or you don't have access to it."))

    ctx = RequestContext(request, {
        'contact' : contact,
        'order' : order})

    return render_to_response('contact/order_tracking.html', ctx)

order_tracking = login_required(order_tracking)