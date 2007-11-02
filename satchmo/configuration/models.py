from django.conf import settings
from django.contrib.sites.models import Site
from django.db import models
from django.db.models import loading
from satchmo.caching import cache_key, cache_get, NotCachedError
from satchmo.caching.models import CachedObjectMixin
import logging

log = logging.getLogger('configuration.models')

__all__ = ['SettingNotSet', 'SettingManager', 'Setting']


class SettingNotSet(Exception):    
    def __init__(self, k):
        self.key = k


class SettingManager(models.Manager):
    def get_query_set(self):
        all = super(SettingManager, self).get_query_set()
        site_id = settings.SITE_ID
        return all.filter(site__id__exact=site_id)


class Setting(models.Model, CachedObjectMixin):
    site = models.ForeignKey(Site)
    group = models.CharField(max_length=100, blank=False, null=False)
    key = models.CharField(max_length=100, blank=False, null=False)
    value = models.CharField(max_length=255, blank=True)

    objects = SettingManager()

    @classmethod
    def find(cls, group, key):
        """Get a setting from cache, if possible"""
        site_id = settings.SITE_ID
        ck = cache_key('Setting', site_id, group, key)
        try:
            setting = cache_get(ck)
            
        except NotCachedError:
            if loading.app_cache_ready():
                try:
                    setting = Setting.objects.get(site__id__exact=site_id, key__exact=key, group__exact=group)
                    setting.cache_set()
                
                except Setting.DoesNotExist:
                    raise SettingNotSet(key)
            else:
                raise SettingNotSet("App cache not loaded: %s" % key)
                
        return setting

    def __nonzero__(self):
        return self.id is not None

    def cache_key(self, *args, **kwargs):
        return cache_key('Setting', self.site, self.group, self.key)

    def delete(self):
        self.cache_delete()
        super(Setting, self).delete()

    def save(self):
        self.site = Site.objects.get_current()
        super(Setting, self).save()
        self.cache_set()
