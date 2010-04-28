from django.db.models import signals
from django.db.models.fields.files import ImageField
from livesettings import config_value, SettingNotSet
from satchmo_utils.thumbnail.utils import remove_file_thumbnails, rename_by_field
from satchmo_utils import normalize_dir
import logging
import os

#ensure config is loaded
import satchmo_utils.thumbnail.config

log = logging.getLogger('thumbnail.fields')

def upload_dir(instance, filename):
    raw = "images/"

    try:
        raw = config_value('PRODUCT', 'IMAGE_DIR')
    except SettingNotSet:
        pass
    except ImportError, e:
        log.warn("Error getting upload_dir, OK if you are in SyncDB.")

    updir = normalize_dir(raw)
    return os.path.join(updir, filename)

class ImageWithThumbnailField(ImageField):
    """ ImageField with thumbnail support

        auto_rename: if it is set perform auto rename to
        <class name>-<field name>-<object pk>.<ext>
        on pre_save.
    """

    def __init__(self, verbose_name=None, name=None,
                 width_field=None, height_field=None,
                 auto_rename=None, name_field=None,
                 upload_to=upload_dir, **kwargs):

        self.auto_rename = auto_rename

        self.width_field, self.height_field = width_field, height_field
        if upload_to == "__DYNAMIC__":
            upload_to = upload_dir
        super(ImageWithThumbnailField, self).__init__(verbose_name, name,
                                                      width_field, height_field,
                                                      upload_to=upload_to,
                                                      **kwargs)
        self.name_field = name_field
        self.auto_rename = auto_rename

    def _save_rename(self, instance, **kwargs):
        if hasattr(self, '_renaming') and self._renaming:
            return
        if self.auto_rename is None:
            # if we get a SettingNotSet exception (even though we've already
            # imported/loaded it), that's bad, so let it bubble up; don't try
            # to guess a default (which should be set in the default config in
            # the first place.)
            self.auto_rename = config_value('THUMBNAIL', 'RENAME_IMAGES')

        image = getattr(instance, self.attname)
        if image and self.auto_rename:
            if self.name_field:
                field = getattr(instance, self.name_field)
                image = rename_by_field(image.name, '%s-%s-%s' \
                                        % (instance.__class__.__name__,
                                           self.name,
                                           field
                                           )
                                        )
            else:
                # XXX this needs testing, maybe it can generate too long image names (max is 100)
                image = rename_by_field(image.name, '%s-%s-%s' \
                                        % (instance.__class__.__name__,
                                           self.name,
                                           instance._get_pk_val()
                                           )
                                        )
            setattr(instance, self.attname, image)
            self._renaming = True
            instance.save()
            self._renaming = False

    def _delete_thumbnail(self, sender, instance=None, **kwargs):
        image = getattr(instance, self.attname)
        if hasattr(image, 'path'):
            remove_file_thumbnails(image.path)

    def contribute_to_class(self, cls, name):
        super(ImageWithThumbnailField, self).contribute_to_class(cls, name)
        signals.pre_delete.connect(self._delete_thumbnail, sender=cls)
        signals.post_save.connect(self._save_rename, sender=cls)

try:
    # South introspection rules for our custom field.
    from south.modelsinspector import add_introspection_rules

    add_introspection_rules([(
        (ImageWithThumbnailField, ),
        [],
        {
            'auto_rename': ["auto_rename", {"default": None}],
            'name_field': ["name_field", {"default": None}],
            'auto_rename': ["auto_rename", {"default": None}],
        },
    )], ['satchmo_utils\.thumbnail\.field'])
except ImportError:
    pass
