from django.core import urlresolvers
from django import forms
import logging
from django.utils.translation import ugettext, ugettext_lazy as _

log = logging.getLogger('payment.listeners')

def form_terms_listener(sender, form=None, **kwargs):
    """Adds a 'do you accept the terms and conditions' checkbox to the form"""

    try:
        url = urlresolvers.reverse('shop_terms')
    except urlresolvers.NoReverseMatch:
        log.warn('To use the form_terms_listener, you must have a "shop_terms" url in your site urls')
        url = "#"
        
    link = u'<a href="%s"></a>' % ugettext('terms and conditions')
    form.fields['terms'] = forms.BooleanField(
        label=_('Do you accept the %(terms_link)s?') % {'terms_link' : link}, 
        widget=forms.CheckboxInput(), required=True)
