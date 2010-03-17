from django.core.cache import cache
from django.contrib.sites.models import Site
from django.template import Library, Node, Variable
from django.template import TemplateSyntaxError, VariableDoesNotExist
from product.models import Category
from satchmo_utils.templatetags import get_filter_args

import logging
import re

log = logging.getLogger('shop.templatetags')

try:
    from xml.etree.ElementTree import Element, SubElement, tostring
except ImportError:
    from elementtree.ElementTree import Element, SubElement, tostring

register = Library()

def recurse_for_children(current_node, parent_node, active_cat, show_empty=True):
    child_count = current_node.child.active().count()

    if show_empty or child_count > 0 or current_node.product_set.count() > 0:
        li_id = 'category-%s' % current_node.id
        li_attrs = {'id': li_id }
        temp_parent = SubElement(parent_node, 'li', li_attrs)
        attrs = {'href': current_node.get_absolute_url()}
        link = SubElement(temp_parent, 'a', attrs)
        link.text = current_node.translated_name()

        if child_count > 0:
            new_parent = SubElement(temp_parent, 'ul')
            children = current_node.child.active()
            for child in children:
                recurse_for_children(child, new_parent, active_cat)

@register.simple_tag
def category_tree(id=None):
    """
    Creates an unnumbered list of the categories.

    Example::

        <ul>
            <li>Books
                <ul>
                <li>Science Fiction
                    <ul>
                    <li>Space stories</li>
                    <li>Robot stories</li>
                    </ul>
                </li>
                <li>Non-fiction</li>
                </ul>
        </ul>
    """
    active_cat = None
    if id:
        try:
            active_cat = Category.objects.active().get(id=id)
        except Category.DoesNotExist:
            active_cat = None
    # We call the category on every page so we will cache
    # The actual structure to save db hits
    current_site = Site.objects.get_current()
    cache_key = "cat-%s" % current_site.id
    existing_tree = cache.get(cache_key, None)
    if existing_tree is None:
        root = Element("ul")
        for cats in Category.objects.root_categories():
            recurse_for_children(cats, root, active_cat)
        existing_tree = root
        cache.set(cache_key, existing_tree)
    # If we have an active cat, search through and identify it
    # This search is less expensive than the multiple db calls
    if active_cat:
        active_cat_id = "category-%s" % active_cat.id
        for li in existing_tree.getiterator("li"):
            if li.attrib["id"] == active_cat_id:
                link = li.find("a")
                link.attrib["class"] = "current"
                break
    return tostring(existing_tree, 'utf-8')

class CategoryListNode(Node):
    """Template Node tag which pushes the category list into the context"""
    def __init__(self, slug, var, nodelist):
        self.var = var
        self.slug = slug
        self.nodelist = nodelist

    def render(self, context):

        if self.slug:
            try:
                cat = Category.objects.active().get(slug__iexact=self.slug.resolve(context))
                cats = cat.child.all()
            except (Category.DoesNotExist, VariableDoesNotExist):
                log.warn("No category found for slug: %s", self.slug)
                cats = []

        else:
            cats = Category.objects.root_categories()

        context[self.var] = cats

        context.push()
        context[self.var] = cats
        output = self.nodelist.render(context)
        context.pop()
        return output

@register.tag
def category_list(parser, token):
    """Push the category list into the context using the given variable name.

    Sample usage::

        {% category_list slug as var %}
        or
        {% category_list as var %}


    """
    args = token.split_contents()
    ct = len(args)
    if not ct in (3,4):
        raise TemplateSyntaxError("%r tag expecting '[slug] as varname', got: %s" % (args[0], args))

    if ct == 3:
        slug = None
        var = args[2]
    else:
        slug = Variable(args[1])
        var = args[3]

    nodelist = parser.parse(('endcategory_list',))
    parser.delete_first_token()

    return CategoryListNode(slug, var, nodelist)

class SetVariableInContextNode(Node):
    def __init__(self, var, val):
        self.var = var
        self.val = val

    def render(self, context):
        context[self.var] = self.val
        return ''

@register.tag
def categories_for_slugs(parser, token):
    """
    Usage: {% categories_for_slugs "slug[,slug...]" as varname %}

    Sets the variable *varname* in the context to a list of categories, given by
    the list of slugs.

    Useful if you want to specify a custom list of categories and override the
    default category listing from satchmo. 
    
    Example usage::

        {% categories_for_slug "hats,boots,accessories" as categories %}
        <ul>
            {% for child in categories.child.active %}
            <li><a href="{{ child.get_absolute_url }}">{{ child.translated_name }}</a></li>
            {% endfor %}
        </ul>
        
    """
    try:
        # Splitting by None == splitting by spaces.
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise TemplateSyntaxError, "%r tag requires arguments" \
              % token.contents.split()[0]

    m = re.search(r'"([^ "]+)" as (\w+)', arg)

    if not m:
        raise TemplateSyntaxError, "%r tag had invalid arguments" \
              % tag_name

    cat_slugs, var = m.groups()
    cats=[]

    for cat_slug in cat_slugs.split(','):
        try:
            cat = Category.objects.get(slug__iexact=cat_slug)
        except Category.DoesNotExist:
            log.warn("No category found for slug: %s", cat_slug)
            cat = None
        cats.append(cat)

    return SetVariableInContextNode(var, cats)

@register.filter
def product_category_siblings(product, args=""):
    args, kwargs = get_filter_args(args,
        keywords=('variations', 'include_self'),
        boolargs=('variations', 'include_self'),
        stripquotes=True)

    sibs = product.get_category.product_set.all().order_by('ordering', 'name')
    if not kwargs.get('variations', True):
        sibs = [sib for sib in sibs if not sib.has_variants]

    if not kwargs.get('include_self', True):
        sibs = [sib for sib in sibs if not sib == product]

    return sibs

class AllProductsForVariableSlugNode(Node):
    """
    Sets the variable *var* in the context to result of

      category.active_products(include_children=True)

    where category is the instance of Category with the slug specified in the
    context variable *slug_var*.
    """
    def __init__(self, slug_var, var):
        self.slug_var = slug_var
        self.var = var

    def render(self, context):
        try:
            slug = self.slug_var.resolve(context)
        except VariableDoesNotExist:
            log.error("The variable '%s' was not found in the context.", self.slug_var)
            return ''

        try:
            cat = Category.objects.active().get(slug__iexact=slug)
        except Category.DoesNotExist:
            log.error("No category found for slug: %s" % slug)
            return ''

        context[self.var] = cat.active_products(include_children=True)
        return ''

class AllProductsForSlugNode(Node):
    """
    Sets the variable *var* in the context to result of

      category.active_products(include_children=True)

    where category is the instance of Category with the slug *slug*.
    """
    def __init__(self, slug, var):
        self.slug = slug
        self.var = var

    def render(self, context):
        try:
            cat = Category.objects.active().get(slug__iexact=self.slug)
        except Category.DoesNotExist:
            log.error("No category found for slug: %s" % self.slug)
            return ''

        context[self.var] = cat.active_products(include_children=True)
        return ''

class AllProductsNode(Node):
    """
    Sets the variable *var* in the context to result of

      category.active_products(include_children=True)

    where category is the variable *category* in the context.
    """
    def __init__(self, var):
        self.var = var

    def render(self, context):
        cat = context.get('category')

        if not cat:
            log.error("The variable 'category' was not found in the context.")

        context[self.var] = cat.active_products(include_children=True)
        return ''

@register.tag
def all_products_for_category(parser, token):
    """
    Usage:
     1. {% all_products_for_category as varname %}
     2. {% all_products_for_category for slug_var as varname %}
     3. {% all_products_for_category for "slug" as varname %}

    Sets the variable *varname* in the context to a list of all products that
    are active in *category*, and is equivalent to the result of:

      category.active_products(include_children=True)

    where *category* is:
     1. the 'category' variable in the context, for usage 1.
     2. the instance of Category with the slug in the context variable
        *slug_var*, for usage 2.
     3. the instance of Category with the slug *slug*, for usage 3.
    """
    try:
        # Splitting by None == splitting by spaces.
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise TemplateSyntaxError, "%r tag requires arguments" \
              % token.contents.split()[0]

    m = re.search(r'(.*?)as (\w+)$', arg)

    # First, get the varname - the easiest
    if not m:
        raise TemplateSyntaxError, "Variable name was not specified for %r tag" \
              % tag_name

    arg, var  = m.groups()

    # Now, try and determine usage case the user wants
    if not arg:
        # We're of the first case.
        return AllProductsNode(var)

    m = re.search(r'^for (.+?)$', arg.strip())

    if not m:
        raise TemplateSyntaxError, "Invalid arguments for %r tag" \
              % tag_name

    arg = m.group(1)

    if arg[0] == '"' and arg[-1] == '"':
        # We're of the third case.
        cat_var = arg[1:-1]
        return AllProductsForSlugNode(arg[1:-1], var)
    elif arg:
        # We're of the second case.
        return AllProductsForVariableSlugNode(Variable(arg), var)

    raise TemplateSyntaxError, "Invalid arguments for %r tag" \
          % tag_name
