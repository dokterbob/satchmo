VERSION = (0, 7, 'pre')

def get_version():
    "Returns the version as a human-format string."
    v = '.'.join([str(i) for i in VERSION[:-1]])
    if VERSION[-1]:
        import satchmo
        from django.utils.version import get_svn_revision
        v = '%s-%s-%s' % (v, VERSION[-1], get_svn_revision(path=satchmo.__path__[0]))
    return v
