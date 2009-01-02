from django.contrib.auth.decorators import user_passes_test
from django.core import urlresolvers
from product import forms
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _
import logging

log = logging.getLogger('shop.adminviews')

def edit_inventory(request):
    """A quick inventory price, qty update form"""
    if request.method == "POST":
        new_data = request.POST.copy()
        form = forms.InventoryForm(new_data)
        if form.is_valid():
            form.save(request)
            url = urlresolvers.reverse('satchmo_admin_edit_inventory')
            return HttpResponseRedirect(url)
    else:
        form = forms.InventoryForm()

    ctx = RequestContext(request, {
        'title' : _('Inventory Editor'),
        'form' : form
        })

    return render_to_response('shop/admin/inventory_form.html', ctx)

edit_inventory = user_passes_test(lambda u: u.is_authenticated() and u.is_staff, login_url='/accounts/login/')(edit_inventory)