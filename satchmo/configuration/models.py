from django.conf import settings
from django.contrib.sites.models import Site
from django.db import models
from django.db.models import loading
from satchmo.caching import cache_key, cache_get, NotCachedError
from satchmo.caching.models import CachedObjectMixin
import logging

log = logging.getLogger('configuration.models')

__all__ = ['SettingNotSet', 'Setting', 'LongSetting', 'find_setting']

def find_setting(group, key):
   """Get a setting or longsetting by group and key, cache and return it."""
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
               # maybe it is a "long setting"
               try:
                   setting = LongSetting.objects.get(site__id__exact=site_id, key__exact=key, group__exact=group)
                   setting.cache_set()
                   
               except LongSetting.DoesNotExist:
                   raise SettingNotSet(key)
       else:
           raise SettingNotSet("App cache not loaded: %s" % key)

   return setting


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
        
    class Meta:
        unique_together = ('site', 'group', 'key')


class LongSettingManager(models.Manager):
    def get_query_set(self):
        all = super(LongSettingManager, self).get_query_set()
        site_id = settings.SITE_ID
        return all.filter(site__id__exact=site_id)


class LongSetting(models.Model, CachedObjectMixin):
    """A Setting which can handle more than 255 characters"""
    site = models.ForeignKey(Site)
    group = models.CharField(max_length=100, blank=False, null=False)
    key = models.CharField(max_length=100, blank=False, null=False)
    value = models.TextField(blank=True)

    objects = LongSettingManager()

    def __nonzero__(self):
        return self.id is not None

    def cache_key(self, *args, **kwargs):
        # note same cache pattern as Setting.  This is so we can look up in one check.
        # they can't overlap anyway, so this is moderately safe.  At the worst, the 
        # Setting will override a LongSetting.
        return cache_key('Setting', self.site, self.group, self.key)

    def delete(self):
        self.cache_delete()
        super(LongSetting, self).delete()

    def save(self):
        self.site = Site.objects.get_current()
        super(LongSetting, self).save()
        self.cache_set()
        
    class Meta:
        unique_together = ('site', 'group', 'key')
    