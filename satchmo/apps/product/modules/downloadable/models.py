from django.contrib.sites.models import Site
from django.core import urlresolvers
from django.db import models
from django.db.models.fields.files import FileField
from django.utils.encoding import smart_str
from django.utils.hashcompat import sha_constructor
from django.utils.translation import ugettext_lazy as _
from livesettings import config_value
from product import signals
from product.models import Product
import product.modules.downloadable.config
from satchmo_store.shop.models import Order
from satchmo_utils import normalize_dir
import datetime
import os
import random

SATCHMO_PRODUCT=True

def get_product_types():
    return ('DownloadableProduct',)


def _protected_dir(instance, filename):
    # if we get a SettingNotSet exception (even though we've already
    # imported/loaded it), that's bad, so let it bubble up.
    raw = config_value('PRODUCT', 'PROTECTED_DIR')
    updir = os.path.normpath(normalize_dir(raw))
    return os.path.join(updir, instance.file.field.get_filename(filename))

class DownloadableProduct(models.Model):
    """
    This type of Product is a file to be downloaded
    """
    product = models.OneToOneField(Product, verbose_name=_("Product"), primary_key=True)
    file = FileField(_("File"), upload_to=_protected_dir)
    num_allowed_downloads = models.IntegerField(
        _("Num allowed downloads"),
        help_text=_("Number of times link can be accessed. Enter 0 for unlimited."),
        default=0)
    expire_minutes = models.IntegerField(
        _("Expire minutes"),
        help_text=_("Number of minutes the link should remain active. Enter 0 for unlimited."),
        default=0)
    active = models.BooleanField(_("Active"), help_text=_("Is this download currently active?"), default=True)
    is_shippable = False
    is_downloadable = True

    def __unicode__(self):
        return self.product.slug

    def _get_subtype(self):
        return 'DownloadableProduct'

    def create_key(self):
        salt = sha_constructor(str(random.random())).hexdigest()[:5]
        download_key = sha_constructor(salt+smart_str(self.product.name)).hexdigest()
        return download_key

    def order_success(self, order, order_item):
        signals.subtype_order_success.send(self, product=self, order=order, subtype="download")

    class Meta:
        verbose_name = _("Downloadable Product")
        verbose_name_plural = _("Downloadable Products")

    def save(self, *args, **kwargs):
        if hasattr(self.product,'_sub_types'):
            del self.product._sub_types
        super(DownloadableProduct, self).save(*args, **kwargs)

class DownloadLink(models.Model):
    downloadable_product = models.ForeignKey(DownloadableProduct, verbose_name=_('Downloadable product'))
    order = models.ForeignKey(Order, verbose_name=_('Order'))
    key = models.CharField(_('Key'), max_length=40)
    num_attempts = models.IntegerField(_('Number of attempts'), )
    time_stamp = models.DateTimeField(_('Time stamp'), )
    active = models.BooleanField(_('Active'), default=True)

    def _attempts_left(self):
        return self.downloadable_product.num_allowed_downloads - self.num_attempts
    attempts_left = property(_attempts_left)

    def is_valid(self):
        # Check num attempts and expire_minutes
        if not self.downloadable_product.active:
            return (False, _("This download is no longer active"))
        maxattempts = self.downloadable_product.num_allowed_downloads
        if maxattempts > 0 and self.num_attempts >= maxattempts:
            return (False, _("You have exceeded the number of allowed downloads."))
        expiremins = self.downloadable_product.expire_minutes
        expire_time = datetime.timedelta(minutes=expiremins) + self.time_stamp
        if expiremins > 0 and datetime.datetime.now() > expire_time:
            return (False, _("This download link has expired."))
        return (True, "")

    def get_absolute_url(self):
        return('satchmo_store.shop.views.download.process', (), { 'download_key': self.key})
    get_absolute_url = models.permalink(get_absolute_url)

    def get_full_url(self):
        url = urlresolvers.reverse('satchmo_download_process', kwargs= {'download_key': self.key})
        return('http://%s%s' % (Site.objects.get_current(), url))

    def save(self, **kwargs):
        """
       Set the initial time stamp
        """
        if self.time_stamp is None:
            self.time_stamp = datetime.datetime.now()
        super(DownloadLink, self).save(**kwargs)

    def __unicode__(self):
        return u"%s - %s" % (self.downloadable_product.product.slug, self.time_stamp)

    def _product_name(self):
        return u"%s" % (self.downloadable_product.product.translated_name())
    product_name=property(_product_name)

    class Meta:
        verbose_name = _("Download Link")
        verbose_name_plural = _("Download Links")


import config
import listeners
listeners.start_default_listening()
