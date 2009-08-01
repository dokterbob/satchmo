"""Tags for manipulating brands on templates."""

from django.template import Library, Node, TemplateSyntaxError
from satchmo_ext.brand.models import Brand
from satchmo_utils.templatetags import get_filter_args

register = Library()

class BrandListNode(Node):
    """Template Node tag which pushes the brand list into the context"""
    def __init__(self, var, nodelist):
        self.var = var
        self.nodelist = nodelist

    def render(self, context):
        brands = Brand.objects.active()
        context[self.var] = brands
        context.push()
        context[self.var] = brands
        output = self.nodelist.render(context)
        context.pop()
        return output            
            
def do_brandlistnode(parser, token):
    """Push the brand list into the context using the given variable name.

    Sample usage::

        {% brand_list as var %}
        
    """
    args = token.split_contents()
    if len(args) != 3:
        raise TemplateSyntaxError("%r tag expecting '[slug] as varname', got: %s" % (args[0], args))
    
    var = args[2]
    nodelist = parser.parse(('endbrand_list',))
    parser.delete_first_token()
    return BrandListNode(var, nodelist)

register.tag('brand_list', do_brandlistnode)
