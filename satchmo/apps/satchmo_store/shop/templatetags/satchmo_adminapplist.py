from django import template
from django.db import models
register = template.Library()

try:
    ''.rsplit
    def rsplit(s, delim, maxsplit):
        return s.rsplit(delim, maxsplit)
except AttributeError:
    def rsplit(s, delim, maxsplit):
        """
        Return a list of the words of the string s, scanning s
        from the end. To all intents and purposes, the resulting
        list of words is the same as returned by split(), except
        when the optional third argument maxsplit is explicitly
        specified and nonzero. When maxsplit is nonzero, at most
        maxsplit number of splits - the rightmost ones - occur,
        and the remainder of the string is returned as the first
        element of the list (thus, the list will have at most
        maxsplit+1 elements). New in version 2.4.
        >>> rsplit('foo.bar.baz', '.', 0)
        ['foo.bar.baz']
        >>> rsplit('foo.bar.baz', '.', 1)
        ['foo.bar', 'baz']
        >>> rsplit('foo.bar.baz', '.', 2)
        ['foo', 'bar', 'baz']
        >>> rsplit('foo.bar.baz', '.', 99)
        ['foo', 'bar', 'baz']
        """
        assert maxsplit >= 0
           
        if maxsplit == 0: return [s]
           
        # the following lines perform the function, but inefficiently.
        #  This may be adequate for compatibility purposes
        items = s.split(delim)
        if maxsplit < len(items):
            items[:-maxsplit] = [delim.join(items[:-maxsplit])]
        return items

class FilterAdminApplistNode(template.Node):
    def __init__(self, listname, varname):
        self.listname = listname
        self.varname = varname

    def render(self, context):
        all_apps = {}
        for app in models.get_apps():
            name = len(rsplit(app.__name__, '.', 0))>1 and rsplit(app.__name__, '.', 0)[-2] or app.__name__
            all_apps[name] = app.__name__

        filtered_app_list = []
        for entry in context[self.listname]:
            app = all_apps.get(entry['name'].lower(),'')
            if not app.startswith('satchmo_'):
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
