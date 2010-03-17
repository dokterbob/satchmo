from django.contrib.sites.models import SiteManager

def is_multihost_enabled():
    return getattr(SiteManager, 'MULTIHOST', False)

def clean_field(form, field_name):
    return form.fields[field_name].clean(form.data.get(field_name))
