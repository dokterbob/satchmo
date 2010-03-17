"""
Associates products to each other for upselling purposes.
"""

# TODO:
# - Rename Upsell object to what it actually is, a CrossSell
# - Implement an Upsell which would *replace* the item.  Like a "supersize" concept.

from datetime import date
from decimal import Decimal, getcontext
from django.conf import settings
from django.db import models
from django.utils.translation import get_language, gettext_lazy as _
from django.utils.translation import ugettext, ugettext_lazy as _
from keyedcache.models import CachedObjectMixin
from product.models import Product
import datetime
import keyedcache
import logging

log = logging.getLogger('upsell.models')

UPSELL_CHOICES=(
    ('CHECKBOX_1_FALSE', _('Checkbox to add 1')),
    ('CHECKBOX_1_TRUE', _('Checkbox to add 1, checked by default')),
    ('CHECKBOX_MATCH_FALSE', _('Checkbox to match quantity')),
    ('CHECKBOX_MATCH_TRUE', _('Checkbox to match quantity, checked by default')),
    ('FORM', _('Form with 0 quantity')),
)

class Upsell(models.Model, CachedObjectMixin):
    
    target = models.ManyToManyField(Product, verbose_name=_('Target Product'), 
        related_name="upselltargets",
        help_text = _("The products for which you want to show this goal product as an Upsell."))
    
    goal = models.ForeignKey(Product, verbose_name=_('Goal Product'), 
        related_name="upsellgoals")
    
    create_date = models.DateField(_("Creation Date"))

    style = models.CharField(_("Upsell Style"), choices=UPSELL_CHOICES,
        default='CHECKBOX_1_FALSE', max_length=20)
        
    notes = models.TextField(_('Notes'), blank=True, null=True,
        help_text = _("Internal notes"))
        
                
    def _description(self):
        """Get the description, looking up by language code, falling back intelligently.
        """
        language_code = get_language()

        try:
            trans = self.cache_get(trans=language_code)

        except keyedcache.NotCachedError, e:
            trans = self._find_translation(language_code)

        if trans:
            return trans.description
        else:
            return ""
            
    description = property(fget=_description)

    def _find_translation(self, language_code):
        c = self.translations.filter(languagecode__exact = language_code)
        ct = c.count()

        if not c or ct == 0:
            pos = language_code.find('-')
            if pos>-1:
                short_code = language_code[:pos]
                log.debug("%s: Trying to find root language content for: [%s]", self, short_code)
                c = self.translations.filter(languagecode__exact = short_code)
                ct = c.count()
                if ct>0:
                    log.debug("%s: Found root language content for: [%s]", self, short_code)

        if not c or ct == 0:
            #log.debug("Trying to find default language content for: %s", self)
            c = self.translations.filter(languagecode__istartswith = settings.LANGUAGE_CODE)
            ct = c.count()

        if not c or ct == 0:
            #log.debug("Trying to find *any* language content for: %s", self)
            c = self.translations.all()
            ct = c.count()

        if ct > 0:
            trans = c[0]
        else:
            trans = None

        self.cache_set(trans=language_code, value=trans)

        return trans
        
    def is_form(self):
        """Returns true if the style is a FORM"""
        return self.style.startswith("FORM")
        
    def is_qty_one(self):
        """Returns true if this style has a '1' in the center field"""
        parts = self.style.split("_")
        return parts[1] == '1'

    def is_checked(self):
        """Returns true if this style ends with TRUE"""
        return self.style.endswith('TRUE')
        
    def __unicode__(self):
        return u"Upsell for %s" % self.goal
        
    def save(self, **kwargs):
        self.create_date = datetime.date.today()
        self.cache_delete()
        super(Upsell, self).save(**kwargs)
        self.cache_set()
        return self
        
    class Meta:
        ordering = ('goal',)
        
class UpsellTranslation(models.Model):

    menu = models.ForeignKey(Upsell, related_name="translations")
    languagecode = models.CharField(_('language'), max_length=10, 
        choices=settings.LANGUAGES, default=settings.LANGUAGES[0][0])
    description = models.TextField(_('Description'), blank=True)

    class Meta:
        ordering=('languagecode', )
