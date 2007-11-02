from django import template

register = template.Library()

@register.inclusion_tag('contact/_addressblock.html')
def addressblock(address):
    """Output an address as a text block"""
    return {"address" : address}
