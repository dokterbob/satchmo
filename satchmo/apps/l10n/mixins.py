# -*- coding: utf-8 -*-
"""Provides mixin objects to ease programming for translations."""
__docformat__="restructuredtext"

from django.contrib.sites.models import Site
from django.utils.translation import get_language
import keyedcache
import logging
from django.conf import settings

log = logging.getLogger('l10n.mixins')

class TranslatedObjectMixin(object):
    """Allows any object with a "translations" object to find the proper translation.
    """
    
    def _find_translation(self, language_code=None, attr='translations'):
        """Look up a translation for an attr.
        
        Ex: self._find_translation(language_code='en-us', attr='translations')
        """
        if not language_code:
            language_code = get_language()
            
        try:
            site = Site.objects.get_current()
            trans = keyedcache.cache_get([self.__class__.__name__, self.id], site=site, trans=attr, lang=language_code)
        except keyedcache.NotCachedError, nce:
            
            translations = getattr(self, attr)

            c = translations.filter(languagecode__exact = language_code)
            ct = c.count()

            if not c or ct == 0:
                pos = language_code.find('-')
                if pos>-1:
                    short_code = language_code[:pos]
                    #log.debug("%s: Trying to find root language content for: [%s]", self, short_code)
                    c = translations.filter(languagecode__exact = short_code)
                    ct = c.count()
                    if ct>0:
                        #log.debug("%s: Found root language content for: [%s]", self, short_code)
                        pass

            if not c or ct == 0:
                #log.debug("Trying to find default language content for: %s", self)
                c = translations.filter(languagecode__istartswith = settings.LANGUAGE_CODE)
                ct = c.count()

            if not c or ct == 0:
                #log.debug("Trying to find *any* language content for: %s", self)
                c = translations.all()
                ct = c.count()

            if ct > 0:
                trans = c[0]
            else:
                trans = None

            keyedcache.cache_set(nce.key, value=trans)

        return trans

# class ExampleTranslation(models.Model):
# 
#     menu = models.ForeignKey(Example, related_name="translations")
#     languagecode = models.CharField(_('language'), max_length=10, choices=settings.LANGUAGES)
#     title = models.CharField(_('title'), max_length=100, blank=False)
#     description = models.CharField(_('Description'), max_length=100, blank=True)
# 
#     class Meta:
#         ordering=('languagecode', )
