from django import http
from django.contrib.auth.decorators import login_required
from django.core import urlresolvers
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from satchmo.configuration import config_value, config_get_group, SettingNotSet
from satchmo.contact import signals, CUSTOMER_ID
from satchmo.contact.common import get_area_country_options
from satchmo.contact.forms import ExtendedContactInfoForm
from satchmo.contact.models import Contact
import logging

log = logging.getLogger('satchmo.contact.views')

def view(request):
    """View contact info."""
    try:
        user_data = Contact.objects.get(user=request.user.id)
    except Contact.DoesNotExist:
        user_data = None

    contact_dict = {
        'user_data': user_data, 
    }

    signals.satchmo_contact_view.send(user_data, contact=user_data, contact_dict=contact_dict)
            
    context = RequestContext(request, contact_dict)
    
    return render_to_response('contact/view_profile.html', context)

view = login_required(view)

def update(request):
    """Update contact info"""

    init_data = {}
    areas, countries, only_country = get_area_country_options(request)

    try:
        contact = Contact.objects.from_request(request, create=False)
    except Contact.DoesNotExist:
        contact = None
    

    if request.method == "POST":
        new_data = request.POST.copy()
        form = ExtendedContactInfoForm(countries, areas, contact, new_data, shippable=True,
            initial=init_data)

        if form.is_valid():
            if contact is None and request.user:
                contact = Contact(user=request.user)
            custID = form.save(contact=contact)
            request.session[CUSTOMER_ID] = custID
            url = urlresolvers.reverse('satchmo_account_info')
            return http.HttpResponseRedirect(url)
        else:
            signals.satchmo_contact_view.send(contact, contact=contact, contact_dict=init_data)

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
            
        signals.satchmo_contact_view.send(contact, contact=contact, contact_dict=init_data)
        form = ExtendedContactInfoForm(countries, areas, contact, shippable=True, initial=init_data)

    init_data['form'] = form
    init_data['country'] = only_country
    
    context = RequestContext(request, init_data)
        
    return render_to_response('contact/update_form.html', context)

update = login_required(update)

