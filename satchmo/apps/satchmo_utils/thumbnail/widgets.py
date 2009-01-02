from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from satchmo_utils.thumbnail.utils import make_admin_thumbnail

class AdminImageWithThumbnailWidget(forms.FileInput):
    """
    A FileField Widget that shows its current image as a thumbnail if it has one.
    """
    def __init__(self, attrs={}):
        super(AdminImageWithThumbnailWidget, self).__init__(attrs)
        
    def render(self, name, value, attrs=None):
        output = []
        if value and hasattr(value, "url"):
            thumb = make_admin_thumbnail(value.url)
            if not thumb:
                thumb = value.url
            output.append('<img src="%s" /><br/>%s<br/> %s ' % \
                (thumb, value.url, _('Change:')))
        output.append(super(AdminImageWithThumbnailWidget, self).render(name, value, attrs))
        return mark_safe(u''.join(output))
