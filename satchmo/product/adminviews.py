from django.contrib.auth.decorators import user_passes_test
from django.core import urlresolvers
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _
from satchmo.product import forms
from satchmo.product.models import Product
import logging

log = logging.getLogger('product.adminviews')

@user_passes_test(lambda u: u.is_authenticated() and u.is_staff, login_url='/accounts/login/')
def edit_inventory(request):
    """A quick inventory price, qty update form"""
    if request.POST:
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

    return render_to_response('admin/inventory_form.html', ctx)

@user_passes_test(lambda u: u.is_authenticated() and u.is_staff, login_url='/accounts/login/')
def export_products(request, template='admin/product_export_form.html'):
    """A product export tool"""
    if request.method == 'POST':
        new_data = request.POST.copy()
        form = forms.ProductExportForm(new_data)
        if form.is_valid():
            return form.export(request)
    else:
        form = forms.ProductExportForm()
        fileform = forms.ProductImportForm()  
        

    ctx = RequestContext(request, {
        'title' : _('Product Import/Export'),
        'form' : form,
        'importform': fileform
        })

    return render_to_response(template, ctx)

@user_passes_test(lambda u: u.is_authenticated() and u.is_staff, login_url='/accounts/login/')
def import_products(request, maxsize=10000000):  
    """ 
    Imports product from an uploaded file.
    """  

    if request.method == 'POST':  
        errors = []
        results = []
        if 'upload' in request.FILES:  
            infile = request.FILES['upload']              
            form = forms.ProductImportForm()
            results, errors = form.import_from(infile, maxsize=maxsize)
                       
        else:
            errors.append('File: %s' % request.FILES.keys())
            errors.append(_('No upload file found'))
                 
        ctx = RequestContext(request, {
            'errors' : errors,
            'results' : results
        })
        return render_to_response("admin/product_import_result.html", ctx)  
    else:  
        url = urlresolvers.reverse('satchmo_admin_product_export')
        return HttpResponseRedirect(url)
        
@user_passes_test(lambda u: u.is_authenticated() and u.is_staff, login_url='/accounts/login/')
def product_active_report(request):
    
    products = Product.objects.filter(active=True)
    products = [p for p in products.all() if 'productvariation' not in p.get_subtypes]
    ctx = RequestContext(Request, {title: 'Active Product Report', 'products' : products })
    return render_to_response('admin/product/active_product_report.html', ctx)
    
    