from django import template

register = template.Library()

def addressblock(address):
    """Output an address as a HTML formatted text block"""
    return {"address" : address}

register.inclusion_tag('contact/_addressblock.html')(addressblock)

def contact_for_user(user):
    if not user.is_anonymous() and user.contact_set.count() > 0:
        return user.contact_set.all()[0]
    return None

register.filter('contact_for_user')(contact_for_user)
