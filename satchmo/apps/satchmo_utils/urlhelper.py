def delete_named_urlpattern(urlpatterns, name):
    """Delete the named urlpattern.
    """

    found = False
    ix = 0

    while not found and ix < len(urlpatterns):
        pattern = urlpatterns[ix]
        if hasattr(pattern, 'url_patterns'):
            found = delete_named_urlpattern(pattern.url_patterns, name)
        else:
            if name and hasattr(pattern, 'name'):
                if pattern.name == name:
                    del urlpatterns[ix]
                    found = True

        if not found:
            ix += 1

    return found

def remove_duplicate_urls(urls, names):
    """Remove any URLs whose names are already in use."""
    for pattern in urls:
        if hasattr(pattern, 'url_patterns'):
            remove_duplicate_urls(pattern.url_patterns, names)

        elif hasattr(pattern, 'name') and pattern.name:
            if pattern.name in names:
                urls.remove(pattern)
            else:
                names.append(pattern.name)

def replace_urlpattern(urlpatterns, replacement):
    """Delete the old urlpattern, and add a new one.
    
    parameters:
        urlpatterns: list
        replacement: an `django.conf.urls.defaults.url` object.
    
    example:
    
        replacement = url(r'^accounts/login/', 'my.site.login_signup', {}, name='auth_login'))
        replace_urlpattern(urlpatterns, replacement)
    """

    found = False
    ix = 0
    if hasattr(replacement, 'name') and replacement.name:
        name = replacement.name
        regex = None
    else:
        name = None
        regex = replacement.regex.pattern
    
    while not found and ix < len(urlpatterns):
        pattern = urlpatterns[ix]
        if hasattr(pattern, 'url_patterns'):
            found = replace_urlpattern(pattern.url_patterns, replacement)
        else:
            if name and hasattr(pattern, 'name'):
                if pattern.name == name:
                    del urlpatterns[ix]
                    urlpatterns.append(replacement)
                    found = True
            elif pattern.regex.pattern == regex:
                del urlpatterns[ix]
                urlpatterns.append(replacement)
                found = True
                    
        if not found:
            ix += 1
            
    return found
    
def replace_urlpatterns(urlpatterns, replacelist):
    for replace in replacelist:
        replace_urlpattern(urlpatterns, replace)
