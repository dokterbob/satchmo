from django import template
from django.core.urlresolvers import reverse
from django.template import Context, Template
from django.utils.translation import ugettext_lazy as _
from product import active_product_types

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
    subtypes = product.get_subtypes()
    for app, subtype in active_product_types():
        is_config = "ConfigurableProduct" in subtypes
        app_label = app.split(".")[-1]
        if subtype in subtypes:
            edit_url = reverse('admin:%s_%s_change' %
                               (app_label, subtype.lower()),
                                args=(product.pk,))
            output += ('<li><a href="%s">' % edit_url +
                       _('Edit %(subtype)s') % {'subtype': subtype} +
                       '</a></li>')
            if is_config or subtype=="ProductVariation":
                 output += '<li><a href="%s">Variation Manager</a></li>' % (reverse("satchmo_admin_variation_manager", args = [product.id]))
        else:
            if not(is_config and subtype=="ProductVariation"):
                add_url = reverse('admin:%s_%s_add' %
                                  (app_label, subtype.lower()))
                output += ('<li><a href="%s?product=%s">' % (add_url, product.id) +
                           _('Add %(subtype)s') % {'subtype': subtype} +
                           '</a></li>')
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
            p_url = '/admin/product/product/%s/' % product.pk
            pv_url = '/admin/product/productvariation/%s/delete/' % product.pk
            output += """
            <tr>
            <td>%s</td>
            <td><a href="%s">%s</a></td>
            <td><a class="deletelink" href="%s">%s</a></td>
            </tr>
            """ % (opt_str, p_url, product.slug, pv_url,
                _("Delete ProductVariation"))
        else:
            #opt_pks = [str(opt.pk) for opt in p_opt]
            #opt_pks = ','.join(opt_pks)
            # TODO [NFA]: Blocked by Django ticket #7738.
            opt_pks = ''
            add_url = '/admin/product/productvariation/add/' + \
                "?product=%s&parent=%s&options=%s" % (
                configurableproduct.product.pk, configurableproduct.product.pk,
                opt_pks)
            output += """
            <tr>
            <td>%s</td>
            <td/>
            <td><a href="%s" class="add-another" id="add_productvariation"> <img src="{%% admin_media_prefix %%}img/admin/icon_addlink.gif" width="10" height="10" alt="Add ProductVariation"/> Add Variation</a></td>
            </tr>
            """ % (opt_str, add_url)
    output += "</table>"
    t = Template(output)
    return t.render(Context())

register.simple_tag(list_variations)

