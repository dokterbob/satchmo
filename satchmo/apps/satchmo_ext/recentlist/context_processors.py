from livesettings import config_value
from product.models import Product

def recent_products(request):
    """Puts the recently-viewed products in the page variables"""
    recent = request.session.get('RECENTLIST',[])
    maxrecent = config_value('PRODUCT','RECENT_MAX')
        
    products = []
    for slug in recent:
        if len(products) > maxrecent:
            break
            
        try:
            p = Product.objects.get_by_site(slug__exact = slug)
            products.append(p)
        except Product.DoesNotExist:
            pass
    
    return {'recent_products' : products}
    