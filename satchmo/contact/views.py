import logging
from django import http
from django.contrib.auth.decorators import login_required
from django.core import urlresolvers
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from satchmo.configuration import config_value, config_get_group, SettingNotSet
from satchmo.contact.common import get_area_country_options
from satchmo.contact.forms import ExtendedContactInfoForm
from satchmo.contact.models import Contact, Order
from satchmo.shop.views.utils import bad_or_missing

log = logging.getLogger('satchmo.contact.views')

@login_required
def view(request):
    """View contact info."""
    try:
        user_data = Contact.objects.get(user=request.user.id)
    except Contact.DoesNotExist:
        user_data = None

    show_newsletter = False
    newsletter = False

    if config_get_group('NEWSLETTER'):
        show_newsletter = True
        from satchmo.newsletter import is_subscribed
        if user_data:
            newsletter = is_subscribed(user_data)
        
    context = RequestContext(request, {
        'user_data': user_data, 
        'show_newsletter' : show_newsletter, 
        'newsletter' : newsletter })
    
    return render_to_response('contact/view_profile.html', context)

@login_required
def update(request):
    """Update contact info"""

    init_data = {}
    areas, countries, only_country = get_area_country_options(request)

    try:
        contact = Contact.objects.from_request(request, create=False)
    except Contact.DoesNotExist:
        contact = None

    if request.POST:
        new_data = request.POST.copy()
        form = ExtendedContactInfoForm(countries, areas, contact, new_data,
            initial=init_data)

        if form.is_valid():
            if contact is None and request.user:
                contact = Contact(user=request.user)
            custID = form.save(contact=contact)
            request.session['custID'] = custID
            url = urlresolvers.reverse('satchmo_account_info')
            return http.HttpResponseRedirect(url)
        else:
            if config_get_group('NEWSLETTER'):
                show_newsletter = True
            else:
                show_newsletter = False

    else:
        if contact:
            #If a person has their contact info, make sure we populate it in the form
            for item in contact.__dict__.keys():
                init_data[item] = getattr(contact,item)
            if contact.shipping_address:
                for item in contact.shipping_address.__dict__.keys():
                    init_data["ship_"+item] = getattr(contact.shipping_address,item)
            if contact.billing_address:
                for item in contact.billing_address.__dict__.keys():
                    init_data[item] = getattr(contact.billing_address,item)
            if contact.primary_phone:
                init_data['phone'] = contact.primary_phone.phone
            
        show_newsletter = False
        current_subscriber = False
        if config_get_group('NEWSLETTER'):
            show_newsletter = True
            if contact:
                from satchmo.newsletter import is_subscribed
                current_subscriber = is_subscribed(contact)

        init_data['newsletter'] = current_subscriber
            
        form = ExtendedContactInfoForm(countries, areas, contact, initial=init_data)

    context = RequestContext(request, {
        'form': form,
        'country': only_country,
        'show_newsletter': show_newsletter})
    return render_to_response('contact/update_form.html', context)

@login_required
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

@login_required
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

