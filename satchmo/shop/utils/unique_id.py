"""
Create a unique user id given a first and last name.
First, we try simple concatenation of first and last name.
If that doesn't work, we add random numbers to the name
"""

from django.contrib.auth.models import User
from satchmo.shop.utils import random_string
import re
import unicodedata
from htmlentitydefs import name2codepoint
from django.utils.encoding import smart_unicode, force_unicode

def generate_id(first_name=None, last_name=None):
    valid_id = False
    test_name = first_name + last_name
    while valid_id is False:
        try:
            User.objects.get(username=test_name)
        except User.DoesNotExist:
            valid_id = True
        else:
            test_name = first_name + last_name + "_" + random_string(7, True)
    return(test_name)
    
    import re
    import unicodedata
    from htmlentitydefs import name2codepoint
    from django.utils.encoding import smart_unicode, force_unicode


# From http://www.djangosnippets.org/snippets/369/
def slugify(s, entities=True, decimal=True, hexadecimal=True,
   instance=None, slug_field='slug', filter_dict=None):
    s = smart_unicode(s)

    #character entity reference
    if entities:
        s = re.sub('&(%s);' % '|'.join(name2codepoint), lambda m: unichr(name2codepoint[m.group(1)]), s)

    #decimal character reference
    if decimal:
        try:
            s = re.sub('&#(\d+);', lambda m: unichr(int(m.group(1))), s)
        except:
            pass

    #hexadecimal character reference
    if hexadecimal:
        try:
            s = re.sub('&#x([\da-fA-F]+);', lambda m: unichr(int(m.group(1), 16)), s)
        except:
            pass

    #translate
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore')

    #replace unwanted characters
    s = re.sub(r'[^-a-z0-9]+', '-', s.lower())

    #remove redundant -
    s = re.sub('-{2,}', '-', s).strip('-')

    slug = s
    if instance:
        def get_query():
            query = instance.__class__.objects.filter(**{slug_field: slug})
            if filter_dict:
                query = query.filter(**filter_dict)
            if instance.pk:
                query = query.exclude(pk=instance.pk)
            return query
        counter = 1
        while get_query():
            slug = "%s-%s" % (s, counter)
            counter += 1
    return slug

