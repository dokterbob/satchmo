from django.contrib.auth.decorators import user_passes_test
from django.core import urlresolvers
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _
from satchmo.product import forms
from satchmo.product.models import Product
from satchmo.product.forms import VariationManagerForm
from satchmo.shop.views.utils import bad_or_missing
import logging

log = logging.getLogger('product.adminviews')

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

    return render_to_response('admin/inventory_form.html', ctx)

edit_inventory = user_passes_test(lambda u: u.is_authenticated() and u.is_staff, login_url='/accounts/login/')(edit_inventory)

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

export_products = user_passes_test(lambda u: u.is_authenticated() and u.is_staff, login_url='/accounts/login/')(export_products)

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

import_products = user_passes_test(lambda u: u.is_authenticated() and u.is_staff, login_url='/accounts/login/')(import_products)
        
def product_active_report(request):
    
    products = Product.objects.filter(active=True)
    products = [p for p in products.all() if 'productvariation' not in p.get_subtypes]
    ctx = RequestContext(Request, {title: 'Active Product Report', 'products' : products })
    return render_to_response('admin/product/active_product_report.html', ctx)
    
product_active_report = user_passes_test(lambda u: u.is_authenticated() and u.is_staff, login_url='/accounts/login/')(product_active_report)    

def variation_list(request):
    products = [p for p in Product.objects.all() if "ConfigurableProduct" in p.get_subtypes()]
    ctx = RequestContext(request, {
           'products' : products,
    })
    
    return render_to_response('admin/product/configurableproduct/variation_manager_list.html', ctx)

    

def variation_manager(request, product_slug = ""):
    try:
        product = Product.objects.get(slug=product_slug)
        subtypes = product.get_subtypes()
        
        if 'ProductVariation' in subtypes:
            # got a variation, we want to work with its parent
            product = product.productvariation.parent.product
            if 'ConfigurableProduct' in product.get_subtypes():
                url = urlresolvers.reverse("satchmo_admin_variation_manager", 
                    kwargs = {'product_slug' : product.slug})
                return HttpResponseRedirect(url)
            
        if 'ConfigurableProduct' not in subtypes:
            return bad_or_missing(request, _('The product you have requested is not a Configurable Product.'))
            
    except Product.DoesNotExist:
            return bad_or_missing(request, _('The product you have requested does not exist.'))
     
    if request.method == 'POST':
        new_data = request.POST.copy()       
        form = VariationManagerForm(new_data, product=product)
        if form.is_valid():
            log.debug("Saving form")
            form.save(request)
            # rebuild the form
            form = VariationManagerForm(product=product)
        else:
            log.debug('errors on form')
    else:
        form = VariationManagerForm(product=product)
    
    ctx = RequestContext(request, {
        'product' : product,
        'form' : form,
    })
    return render_to_response('admin/product/configurableproduct/variation_manager.html', ctx)
    
variation_manager = user_passes_test(lambda u: u.is_authenticated() and u.is_staff, login_url='/accounts/login/')(variation_manager)    
