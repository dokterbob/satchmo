"""Adds a new HTTPS handler to urllib2, which uses the SSL library from Python 2.6."""

import logging
log = logging.getLogger('sslurllib')
import sys

# We only need this wrapper for Python versions < 2.6
# sys.hexversion is guaranteed to always increment
if sys.hexversion >= 0x020600F0: 
    runningPython26 = True
else: 
    runningPython26 = False
    
try:
    import ssl
    _sane = True
except:
    log.warning('ssl is not installed, please install it from http://pypi.python.org/pypi/ssl/')
    _sane = False
    
if _sane and not runningPython26:
    import httplib, socket, urllib2
    __all__ = ['HTTPSv2Connection', 'HTTPSv2Handler']
    
    log.debug('Installing SSLv2 HTTPS Methods into urllib2')
    
    class HTTPSv2Connection(httplib.HTTPConnection):
        """This class allows communication via SSLv2."""

        default_port = httplib.HTTPS_PORT

        def __init__(self, host, port=None, key_file=None, cert_file=None,
                     strict=None):
            httplib.HTTPConnection.__init__(self, host, port, strict)
            self.key_file = key_file
            self.cert_file = cert_file

        def connect(self):
            "Connect to a host on a given (SSL) port."
            log.debug('HTTPSv2 connecting to %s:%s', self.host, self.port)
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            ssl_sock = ssl.wrap_socket(sock,
                                       ca_certs=self.cert_file)

            ssl_sock.connect((self.host, self.port))
            self.sock = ssl_sock

    class HTTPSv2Handler(urllib2.HTTPSHandler):
        """Overrides the base urllib2 HTTPSHandler."""
        
        def https_open(self, req):
            return self.do_open(HTTPSv2Connection, req)

    # now instantiate the HTTPSv2Handler and install it.
    v2handler = HTTPSv2Handler()
    opener = urllib2.build_opener(v2handler)
    
    # this will make our new subclassed HTTPSHandler be used for all HTTPSConnections
    urllib2.install_opener(opener)
    
