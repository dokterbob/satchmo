"""From http://www.davidcramer.net/code/62/set-cookies-without-a-response-in-django.html

Used with permission.  Thank you David Cramer.

To install, add the prehandler to the beginning of your middleware list, and the posthandler to the end.  Then, you can use request.COOKIES.get|set|delete anywhere in the code and they'll be automatically added to the response.
"""

from Cookie import SimpleCookie, Morsel
import copy
 
class CookiePreHandlerMiddleware(object):
    """
    This middleware modifies request.COOKIES and adds a set and delete method.
 
    `set` matches django.http.HttpResponse.set_cookie
    `delete` matches django.http.HttpResponse.delete_cookie
 
    This should be the first middleware you load.
    """
    def process_request(self, request):
        cookies = CookieHandler()
        for k, v in request.COOKIES.iteritems():
            cookies[k] = str(v)
        request.COOKIES = cookies
        request._orig_cookies = copy.deepcopy(request.COOKIES)
 
class CookiePostHandlerMiddleware(object):
    """
    This middleware modifies updates the response will all modified cookies.
 
    This should be the last middleware you load.
    """
    def process_response(self, request, response):
        if hasattr(request, '_orig_cookies') and request.COOKIES != request._orig_cookies:
            for k,v in request.COOKIES.iteritems():
                if request._orig_cookies.get(k) != v:
                    dict.__setitem__(response.cookies, k, v)
        return response
 
class StringMorsel(Morsel):
    def __str__(self):
        return self.value
 
    def __eq__(self, a):
        if isinstance(a, str):
            return str(self) == a
        elif isinstance(a, Morsel):
            return a.output() == self.output()
        return False
 
    def __ne__(self, a):
        if isinstance(a, str):
            return str(self) != a
        elif isinstance(a, Morsel):
            return a.output() != self.output()
        return True
 
    def __repr__(self):
        return str(self)
 
class CookieHandler(SimpleCookie):
    def __set(self, key, real_value, coded_value):
        """Private method for setting a cookie's value"""
        M = self.get(key, StringMorsel())
        M.set(key, real_value, coded_value)
        dict.__setitem__(self, key, M)
 
    def __setitem__(self, key, value):
        """Dictionary style assignment."""
        rval, cval = self.value_encode(value)
        self.__set(key, rval, cval)
 
    def set(self, key, value='', max_age=None, expires=None, path='/', domain=None, secure=None):
        self[key] = value
        for var in ('max_age', 'path', 'domain', 'secure', 'expires'):
            val = locals()[var]
            if val is not None:
                self[key][var.replace('_', '-')] = val
 
    def delete(self, key, path='/', domain=None):
        self[key] = ''
        if path is not None:
            self[key]['path'] = path
        if domain is not None:
            self[key]['domain'] = domain
        self[key]['expires'] = 0
        self[key]['max-age'] = 0