"""
Create a unique user id given a first and last name.
First, we try simple concatenation of first and last name.
If that doesn't work, we add random numbers to the name
"""

from django.contrib.auth.models import User
from django.utils.encoding import smart_unicode, force_unicode
from htmlentitydefs import name2codepoint
from satchmo_utils import random_string
import re
import unicodedata

_is_alnum_re = re.compile(r'\w+')
_ID_MIN_LENGTH = 5  # minimum reasonable length for username
_ID_MAX_LENGTH = 30 # as defined in django.auth.contrib.models.User.username field

def _id_generator(first_name, last_name, email):
    def _alnum(s, glue=''):
        return glue.join(filter(len, _is_alnum_re.findall(s))).lower()
    # The way to generate id is by trying:
    #  1. username part of email
    #  2. ascii-transliterated first+last name
    #  3. whole email with non-alphanumerics replaced by underscore
    #  4. random string
    # Every try must return at least _ID_MIN_LENGTH chars to succeed and is truncated
    # to _ID_MAX_LENGTH. All IDs are lowercased.
    id = _alnum(email.split('@')[0])
    if len(id) >= _ID_MIN_LENGTH:
        yield id[:_ID_MAX_LENGTH]
    id = _alnum(unicodedata.normalize('NFKD', first_name + last_name).encode('ascii', 'ignore'))
    if len(id) >= _ID_MIN_LENGTH:
        yield id[:_ID_MAX_LENGTH]
    id = _alnum(email, glue='_')
    if len(id) >= _ID_MIN_LENGTH:
        yield id[:_ID_MAX_LENGTH]
    while True:
        yield _alnum('%s_%s' % (id[:_ID_MIN_LENGTH], random_string(_ID_MIN_LENGTH, True)))[:_ID_MAX_LENGTH]

def generate_id(first_name='', last_name='', email=''):
    valid_id = False
    gen = _id_generator(first_name, last_name, email)
    test_name = gen.next()
    while valid_id is False:
        try:
            User.objects.get(username=test_name)
        except User.DoesNotExist:
            valid_id = True
        else:
            test_name = gen.next()
    return test_name

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
    #Added _ because this is a valid slug option
    s = re.sub(r'[^-a-z0-9_]+', '-', s.lower())

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

