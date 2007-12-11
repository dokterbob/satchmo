from django.template import Library, Node
from satchmo.product.models import Category
from satchmo.shop.templatetags import get_filter_args

register = Library()

def product_images(product, args=""):
    args, kwargs = get_filter_args(args, 
        keywords=('include_main', 'maximum'), 
        boolargs=('include_main'),
        intargs=('maximum'),
        stripquotes=True)

    q = product.productimage_set
    if kwargs.get('include_main', True):
        q = q.all()
    else:
        main = product.main_image
        q = q.exclude(id = main.id)
    
    maximum = kwargs.get('maximum', -1)
    if maximum>-1:
        q = list(q)[:maximum]
    
    return q

register.filter('product_images', product_images)