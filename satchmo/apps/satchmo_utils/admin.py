#
#    Autocomplete feature for admin panel
#
#    Most of the code has been written by Jannis Leidel:
#    http://jannisleidel.com/2008/11/autocomplete-form-widget-foreignkey-model-fields/
#
#    to_string_function, Satchmo adaptation and some comments added by emes (Michal Salaban)
#
from django import forms
from django.db import models
from django.db.models.query import QuerySet
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import Message
from django.http import HttpResponse, HttpResponseNotFound
from django.utils.encoding import smart_str
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.text import truncate_words

import operator

class ForeignKeySearchInput(forms.HiddenInput):
    """
    A Widget for displaying ForeignKeys in an autocomplete search input 
    instead in a <select> box.
    """

    to_string_function = lambda s: truncate_words(s, 14)

    class Media:
        css = {
            'all': ('css/jquery.autocomplete.css',)
        }
        js = (
            # The js/jquery.js script is referenced in admin/base_site.html template.
            # Requesting it here again would reset all the plugins loaded afterwards.
            'js/jquery.bgiframe.js',
            'js/jquery.ajaxQueue.js',
            'js/jquery.autocomplete.js'
        )

    def label_for_value(self, value):
        key = self.rel.get_related_field().name
        obj = self.rel.to._default_manager.get(**{key: value})
        return self.to_string_function(obj)

    def __init__(self, rel, search_fields, to_string_function, attrs=None):
        self.rel = rel
        self.search_fields = search_fields
        if to_string_function: self.to_string_function = to_string_function
        super(ForeignKeySearchInput, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        if attrs is None:
            attrs = {}
        rendered = super(ForeignKeySearchInput, self).render(name, value, attrs)
        if value:
            label = self.label_for_value(value)
        else:
            label = u''
        return rendered + mark_safe(u'''
            <style type="text/css" media="screen">
                #lookup_%(name)s {
                    padding-right:16px;
                    background: url(
                        %(admin_media_prefix)simg/admin/selector-search.gif
                    ) no-repeat right;
                }
                #del_%(name)s {
                    display: none;
                }
            </style>
<input type="text" id="lookup_%(name)s" value="%(label)s" />
<a href="#" id="del_%(name)s">
<img src="%(admin_media_prefix)simg/admin/icon_deletelink.gif" />
</a>
<script type="text/javascript">
            var lookup = $('#lookup_%(name)s')
            if (lookup.val()) {
                $('#del_%(name)s').show()
            }
            lookup.attr('size', Math.max(10, lookup.attr('value').length))
            lookup.autocomplete('../search/', {
                formatResult: function(data){ return $('<div />').html(data[0]).text(); },
                extraParams: {
                    search_fields: '%(search_fields)s',
                    app_label: '%(app_label)s',
                    model_name: '%(model_name)s'
                }
            }).result(function(event, data, formatted) {
                if (data) {
                    $('#id_%(name)s').val(data[1]);
                    $('#del_%(name)s').show();
                }
            });
            $('#del_%(name)s').click(function(ele, event) {
                $('#id_%(name)s').val('');
                $('#del_%(name)s').hide();
                $('#lookup_%(name)s').val('');
            });
            </script>
        ''') % {
            'search_fields': ','.join(self.search_fields),
            'admin_media_prefix': settings.ADMIN_MEDIA_PREFIX,
            'model_name': self.rel.to._meta.module_name,
            'app_label': self.rel.to._meta.app_label,
            'label': label,
            'name': name,
        }

class AutocompleteAdmin(admin.ModelAdmin):
    """Admin class for models using the autocomplete feature.

    There are two additional fields:
       - related_search_fields: defines fields of managed model that
         have to be represented by autocomplete input, together with
         a list of target model fields that have to be searched for
         input string,
       - related_string_functions: contains optional functions which
         take target model instance as only argument and return string
         representation. By default __unicode__() method of target
         object is used.
    """

    related_search_fields = {}
    related_string_functions = {}

    def __call__(self, request, url):
        # This is deprecated interface and will be dropped in Django 1.3.
        # Since the version 1.1, Django uses get_urls() method below.
        if url is None:
            pass
        elif url == 'search':
            return self.search(request)
        return super(AutocompleteAdmin, self).__call__(request, url)

    def get_urls(self):
        from django.conf.urls.defaults import url
        patterns = super(AutocompleteAdmin, self).get_urls()
        info = self.admin_site.name, self.model._meta.app_label, self.model._meta.module_name
        patterns.insert(
                -1,     # insert just before (.+) rule (see django.contrib.admin.options.ModelAdmin.get_urls)
                url(
                    r'^search/$',
                    self.search,
                    name='%sadmin_%s_%s_search' % info
                    )
                )
        return patterns

    def search(self, request):
        """
        Searches in the fields of the given related model and returns the
        result as a simple string to be used by the jQuery Autocomplete plugin
        """
        query = request.GET.get('q', None)
        app_label = request.GET.get('app_label', None)
        model_name = request.GET.get('model_name', None)
        search_fields = request.GET.get('search_fields', None)
        try:
            to_string_function = self.related_string_functions[model_name]
        except KeyError:
            to_string_function = lambda x: x.__unicode__()

        if search_fields and app_label and model_name and query:
            def construct_search(field_name):
                # use different lookup methods depending on the notation
                if field_name.startswith('^'):
                    return "%s__istartswith" % field_name[1:]
                elif field_name.startswith('='):
                    return "%s__iexact" % field_name[1:]
                elif field_name.startswith('@'):
                    return "%s__search" % field_name[1:]
                else:
                    return "%s__icontains" % field_name

            model = models.get_model(app_label, model_name)
            qs = model._default_manager.all()
            for bit in query.split():
                or_queries = [models.Q(**{construct_search(
                    smart_str(field_name)): smart_str(bit)})
                        for field_name in search_fields.split(',')]
                other_qs = QuerySet(model)
                other_qs.dup_select_related(qs)
                other_qs = other_qs.filter(reduce(operator.or_, or_queries))
                qs = qs & other_qs
            data = ''.join([u'%s|%s\n' % (to_string_function(f), f.pk) for f in qs])
            return HttpResponse(data)
        return HttpResponseNotFound()

    def formfield_for_dbfield(self, db_field, **kwargs):
        """
        Overrides the default widget for Foreignkey fields if they are
        specified in the related_search_fields class attribute.
        """
        if isinstance(db_field, models.ForeignKey) and \
                db_field.name in self.related_search_fields:
            kwargs['widget'] = ForeignKeySearchInput(
                    db_field.rel,
                    self.related_search_fields[db_field.name],
                    self.related_string_functions.get(db_field.name)
                    )
        field = super(AutocompleteAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        return field
