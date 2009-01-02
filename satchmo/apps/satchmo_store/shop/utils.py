from django.contrib.sites.models import SiteManager

def is_multihost_enabled():
    return getattr(SiteManager, 'MULTIHOST', False)
