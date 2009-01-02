VERSION = (0, 9, 'pre')

# Dynamically calculate the version based on VERSION tuple
if len(VERSION)>2 and VERSION[2] is not None:
    str_version = "%d.%d_%s" % VERSION[:3]
else:
    str_version = "%d.%d" % VERSION[:2]

__version__ = str_version

def get_version():
    "Returns the version as a human-format string."
    v = '.'.join([str(i) for i in VERSION[:-1]])
    if VERSION[-1]:
        import satchmo_store
        from django.utils.version import get_svn_revision
        v = '%s-%s-%s' % (v, VERSION[-1], get_svn_revision(path=satchmo_store.__path__[0]))
    return v
