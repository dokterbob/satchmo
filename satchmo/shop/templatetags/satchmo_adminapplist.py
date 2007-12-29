from django import template
from django.db import models
register = template.Library()

class FilterAdminApplistNode(template.Node):
    def __init__(self, listname, varname):
        self.listname = listname
        self.varname = varname

    def render(self, context):
        all_apps = {}
        for app in models.get_apps():
            name = app.__name__.rsplit('.')[-2]
            all_apps[name] = app.__name__

        filtered_app_list = []
        for entry in context[self.listname]:
            app = all_apps.get(entry['name'].lower())
            if app.split('.')[0] != 'satchmo':
                filtered_app_list.append(entry)
        context[self.varname] = filtered_app_list
        return ''

def filter_admin_app_list(parser, token):
    """Filters the list of installed apps returned by
       django.contrib.admin.templatetags.adminapplist,
       excluding apps installed by satchmo.
    """
    tokens = token.contents.split()
    if len(tokens) < 4:
        raise template.TemplateSyntaxError, "'%s' tag requires two arguments" % tokens[0]
    if tokens[2] != 'as':
        raise template.TemplateSyntaxError, "Second argument to '%s' tag must be 'as'" % tokens[0]
    return FilterAdminApplistNode(tokens[1], tokens[3])

register.tag('filter_admin_app_list', filter_admin_app_list)
