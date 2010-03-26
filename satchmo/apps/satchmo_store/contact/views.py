from django import http
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import login_required
from django.core import urlresolvers
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from livesettings import config_value, config_get_group, SettingNotSet
from satchmo_store.contact import signals, CUSTOMER_ID
from satchmo_store.contact.forms import ExtendedContactInfoForm
from satchmo_store.contact.models import Contact
from satchmo_store.shop.models import Config
import logging

log = logging.getLogger('satchmo_store.contact.views')

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

    return render_to_response('contact/view_profile.html',
                              context_instance=context)

view = login_required(view)

def update(request):
    """Update contact info"""

    init_data = {}
    shop = Config.objects.get_current()

    try:
        contact = Contact.objects.from_request(request, create=False)
    except Contact.DoesNotExist:
        contact = None
    

    if request.method == "POST":
        new_data = request.POST.copy()            
        form = ExtendedContactInfoForm(data=new_data, shop=shop, contact=contact, shippable=True,
            initial=init_data)

        if form.is_valid():
            if contact is None and request.user:
                contact = Contact(user=request.user)
            custID = form.save(contact=contact)
            request.session[CUSTOMER_ID] = custID
            redirect_to = request.REQUEST.get(REDIRECT_FIELD_NAME, '')
            if not redirect_to or '//' in redirect_to or ' ' in redirect_to:
                redirect_to = urlresolvers.reverse('satchmo_account_info')

            return http.HttpResponseRedirect(redirect_to)
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
            if contact.organization:
                init_data['organization'] = contact.organization.name
   
            
        signals.satchmo_contact_view.send(contact, contact=contact, contact_dict=init_data)
        form = ExtendedContactInfoForm(shop=shop, contact=contact, shippable=True, initial=init_data)

    init_data['form'] = form
    if shop.in_country_only:
        init_data['country'] = shop.sales_country
    else:
        countries = shop.countries()
        if countries and countries.count() == 1:
            init_data['country'] = countries[0]
    
    
    init_data['next'] = request.REQUEST.get(REDIRECT_FIELD_NAME, '')
    context = RequestContext(request, init_data)

    return render_to_response('contact/update_form.html',
                              context_instance=context)

update = login_required(update)

