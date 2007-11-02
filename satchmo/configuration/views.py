from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.admin.views.decorators import staff_member_required

from satchmo.configuration import *
from satchmo.configuration import forms
import logging

log = logging.getLogger('configuration.views')

def group_settings(request, group, template='configuration/group_settings.html'):
    # Determine what set of settings this editor is used for
    mgr = ConfigurationSettings()
    if group is None:
        settings = mgr
        title = 'Site settings'
    else:
        settings = mgr[group]
        title = settings.name
        log.debug('title: %s', title)

    # Create an editor customized for the current user
    #editor = forms.customized_editor(settings)

    if request.method == 'POST':
        # Populate the form with user-submitted data
        data = request.POST.copy()
        form = forms.SettingsEditor(data, settings=settings)
        if form.is_valid():
            form.full_clean()
            for name, value in form.cleaned_data.items():
                group, key = name.split('__')
                cfg = mgr.get_config(group, key)
                if cfg.update(value):

                    # Give user feedback as to which settings were changed
                    request.user.message_set.create(message='Updated %s on %s' % (cfg.key, cfg.group.key))

            return HttpResponseRedirect(request.path)
    else:
        # Leave the form populated with current setting values
        #form = editor()
        form = forms.SettingsEditor(settings=settings)

    return render_to_response(template, {
        'title': title,
        'group' : group,
        'form': form,
    }, context_instance=RequestContext(request))
group_settings = staff_member_required(group_settings)

# Site-wide setting editor is identical, but without a group
# staff_member_required is implied, since it calls group_settings
def site_settings(request):
    return group_settings(request, group=None, template='configuration/site_settings.html')
