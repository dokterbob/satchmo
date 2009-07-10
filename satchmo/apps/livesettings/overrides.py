"""Allows livesettings to be "locked down" and no longer use the settings page or the database
for settings retrieval.
"""

from django.conf import settings as djangosettings
from django.contrib.sites.models import Site
from django.db import transaction

__all__ = ['get_overrides']

def _safe_get_siteid(site):
    if not site:
        try:
            site = Site.objects.get_current()
        except:
            transaction.rollback()
        if site and site.id:
            siteid = site.id
        else:
            siteid = djangosettings.SITE_ID
    else:
        siteid = site.id
    transaction.commit()
    return siteid

_safe_get_siteid=transaction.commit_manually(_safe_get_siteid)

def get_overrides(siteid=-1):
    """Check to see if livesettings is allowed to use the database.  If not, then
    it will only use the values in the dictionary, LIVESETTINGS_OPTIONS[SITEID]['SETTINGS'],
    this allows 'lockdown' of a live site.

    The LIVESETTINGS dict must be formatted as follows::

    LIVESETTINGS_OPTIONS = {
            1 : {
                    'DB' : [True/False],
                    SETTINGS = {
                        'GROUPKEY' : {'KEY', val, 'KEY2', val},
                        'GROUPKEY2' : {'KEY', val, 'KEY2', val},
                    }
                }
            }

    In the settings dict above, the "val" entries must exactly match the format 
    stored in the database for a setting.  Do not use a literal True or an integer,
    it needs to be the string representation of them.

    Returns a tuple (DB_ALLOWED, SETTINGS)
    """
    if siteid == -1:
        siteid = _safe_get_siteid(None)

    overrides = (True, {})
    if hasattr(djangosettings, 'LIVESETTINGS_OPTIONS'):
        opts = djangosettings.LIVESETTINGS_OPTIONS
        if opts.has_key(siteid):
            opts = opts[siteid]
            overrides = (opts['DB'], opts['SETTINGS'])

    return overrides
