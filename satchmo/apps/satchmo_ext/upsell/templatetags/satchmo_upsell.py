from django import template

register = template.Library()

def product_upsell(product):
    """
    Display the list of products that are upsell candidates for currently viewed product.
    """
    goals = None
    if product.upselltargets.count() > 0:
        goals = product.upselltargets.all()
        
    return { 'goals' : goals }
register.inclusion_tag("upsell/product_upsell.html", takes_context=False)(product_upsell)