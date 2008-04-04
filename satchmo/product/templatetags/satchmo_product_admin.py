from django import template
from django.conf import settings
from django.template import Context, Template
from satchmo.configuration import config_value
from django.utils.translation import get_language, ugettext_lazy as _

register = template.Library()

def js_make_select_readonly(select):
    #This is really just a mini-template
    #select must be a jquery object
    return """
    select = %(select)s;
    value = select.attr("value");
    if (value){
        text = "";
        for (c in select.children()){
          if (select.children()[c].value == value){
            text = select.children()[c].innerHTML;
            break;
          }
        }
        select.before("<strong>" + text + "</strong><input type=\\"hidden\\" name=\\"" + select.attr("name") + "\\" value=\\"" + value + "\\" \>");
        select.remove();
    }
    """ % {'select':select}

register.simple_tag(js_make_select_readonly)

def edit_subtypes(product):
    output = '<ul>'
    for key in config_value('PRODUCT', 'PRODUCT_TYPES'):
        app, subtype = key.split("::")
        if subtype in product.get_subtypes():
            output += '<li><a href="/admin/%s/%s/%s/">' % (app, subtype.lower(), product.id) + _('Edit %(subtype)s') % {'subtype': subtype} + '</a></li>'
        else:
            output += ' <li><a href="/admin/%s/%s/add/?product_id=%s">' %(app, subtype.lower(), product.id) + _('Add %(subtype)s') % {'subtype': subtype} + '</a></li>'

    output += '</ul>'
    return output

register.simple_tag(edit_subtypes)

def list_variations(configurableproduct):
    opts = configurableproduct.get_all_options()
    output = "{% load admin_modify adminmedia %}"
    output += "<table>"
    for p_opt in opts:
        opt_strs = []
        [opt_strs.append(opt.name) for opt in p_opt]
        opt_str = ', '.join(opt_strs)

        product = configurableproduct.get_product_from_options(p_opt)
        if product:
            #TODO: What's the right way to get this URL?
            p_url = '/admin/product/product/%s/' % product.id
            pv_url = '/admin/product/productvariation/%s/' % product.id

            output += """
            <tr>
            <td>%s</td>
            <td><a href="%s">%s</a></td>
            <td><a class="deletelink" href="%sdelete/"> Delete ProductVariation</a></td>
            </tr>
            """ % (opt_str, p_url, product.slug, pv_url)
        else:
            opt_ids = []
            [opt_ids.append(str(opt.id)) for opt in p_opt]
            opt_ids = ','.join(opt_ids)

            output += """
            <tr>
            <td>%s</td>
            <td/>
            <td><a href="../../productvariation/add/?parent_id=%s&options=%s" class="add-another" id="add_productvariation"> <img src="{%% admin_media_prefix %%}img/admin/icon_addlink.gif" width="10" height="10" alt="Add ProductVariation"/> Add Variation</a></td>
            </tr>
            """ % (opt_str, configurableproduct.product.id, opt_ids)
    output += "</table>"
    t = Template(output)
    return t.render(Context())

register.simple_tag(list_variations)

def customproduct_management(order):
    custom = []
    for orderitem in order.orderitem_set.all():
        if 'CustomProduct' in orderitem.product.get_subtypes():
            custom.append(orderitem)
            
    return {
        'SHOP_BASE' : settings.SHOP_BASE,
        'customitems' : custom
    }

register.inclusion_tag('admin/_customproduct_management.html')(customproduct_management)

def orderpayment_list(order):
    return {
        'SHOP_BASE' : settings.SHOP_BASE, 
        'order' : order,
        'payments' : order.payments.all()
        }

register.inclusion_tag('admin/_orderpayment_list.html')(orderpayment_list)
