from django import template

register = template.Library()

def addressblock(address):
    """Output an address as a text block"""
    return {"address" : address}

register.inclusion_tag('contact/_addressblock.html')(addressblock)
