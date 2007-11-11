from django.template import Library
from satchmo.product.models import Category

try:
    from xml.etree.ElementTree import Element, SubElement, tostring
except ImportError:
    from elementtree.ElementTree import Element, SubElement, tostring

register = Library()

def recurse_for_children(current_node, parent_node, active_cat, show_empty=True):
    child_count = current_node.child.count()

    if show_empty or child_count > 0 or current_node.product_set.count() > 0:
        temp_parent = SubElement(parent_node, 'li')
        attrs = {'href': current_node.get_absolute_url()}
        if current_node == active_cat:
            attrs["class"] = "current"
        link = SubElement(temp_parent, 'a', attrs)
        link.text = current_node.name

        if child_count > 0:
            new_parent = SubElement(temp_parent, 'ul')
            children = current_node.child.all()
            for child in children:
                recurse_for_children(child, new_parent, active_cat)

def category_tree(id=None):
    """
    Creates an unnumbered list of the categories.  For example:
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
        active_cat = Category.objects.get(id=id)
    root = Element("ul")
    for cats in Category.objects.filter(parent__isnull=True):
        recurse_for_children(cats, root, active_cat)
    return tostring(root, 'utf-8')

register.simple_tag(category_tree)

