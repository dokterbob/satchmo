VERSION = (0, 9, 0)
            
# Dynamically calculate the version based on VERSION tuple
if len(VERSION)>2 and VERSION[2] is not None:
    str_version = "%d.%d_%s" % VERSION[:3]
else:
    str_version = "%d.%d" % VERSION[:2]

__version__ = str_version

def get_version():
    "Returns the version as a human-format string."
    hg_rev='hg-unknown'
    v = '.'.join([str(i) for i in VERSION[:-1]])
    if VERSION[-1]:
        try:
            import os
            from mercurial import ui, hg
            dir = os.path.dirname(__file__)
            hg_dir = os.path.normpath(os.path.join(dir,"../../../"))
            repo = hg.repository(ui.ui(), hg_dir)
            c = repo['tip']
            hg_rev = "hg-%s:%s" % (c.rev(), c.hex()[0:12])
        except:
            pass
        v = '%s-%s %s' % (v, VERSION[-1], hg_rev)
    return v
