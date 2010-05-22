from decimal import Decimal
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from l10n.utils import lookup_translation
from product.models import Product, OptionGroup, get_product_quantity_price, get_product_quantity_adjustments
from product.modules.configurable.models import get_all_options
from satchmo_utils.fields import CurrencyField
from satchmo_utils.unique_id import slugify

SATCHMO_PRODUCT=True

def get_product_types():
    return ('CustomProduct',)

class CustomProduct(models.Model):
    """
    Product which must be custom-made or ordered.
    """
    product = models.OneToOneField(Product, verbose_name=_('Product'), primary_key=True)
    downpayment = models.IntegerField(_("Percent Downpayment"), default=20)
    deferred_shipping = models.BooleanField(_('Deferred Shipping'),
        help_text=_('Do not charge shipping at checkout for this item.'),
        default=False)
    option_group = models.ManyToManyField(
        OptionGroup,
        verbose_name=_('Option Group'),
        blank=True)

    def _is_shippable(self):
        return not self.deferred_shipping
    is_shippable = property(fget=_is_shippable)

    def _get_fullPrice(self):
        """
        returns price as a Decimal
        """
        return self.get_qty_price(Decimal('1'))

    unit_price = property(_get_fullPrice)

    def add_template_context(self, context, selected_options, **kwargs):
        """
        Add context for the product template.
        Return the updated context.
        """
        from product.utils import serialize_options

        options = serialize_options(self, selected_options)
        if not 'options' in context:
            context['options'] = options
        else:
            curr = list(context['options'])
            curr.extend(list(options))
            context['options'] = curr

        return context

    def get_qty_price(self, qty, include_discount=True):
        """
        If QTY_DISCOUNT prices are specified, then return the appropriate discount price for
        the specified qty.  Otherwise, return the unit_price
        returns price as a Decimal
        """
        if include_discount:
            price = get_product_quantity_price(self.product, qty)
        else:
            adjustment = get_product_quantity_adjustments(self, qty)
            if adjustment.price is not None:
                price = adjustment.price.price
            else:
                price = None

        if not price and qty == Decimal('1'): # Prevent a recursive loop.
            price = Decimal("0.00")
        elif not price:
            price = self.product._get_fullPrice()

        return price * self.downpayment / 100

    def get_full_price(self, qty=Decimal('1')):
        """
        Return the full price, ignoring the deposit.
        """
        price = get_product_quantity_price(self.product, qty)
        if not price:
            price = self.product.unit_price

        return price

    full_price = property(fget=get_full_price)



    def _get_subtype(self):
        return 'CustomProduct'

    def __unicode__(self):
        return u"CustomProduct: %s" % self.product.name

    def get_valid_options(self):
        """
        Returns all of the valid options
        """
        return get_all_options(self, ids_only=True)

    def save(self, **kwargs):
        if hasattr(self.product,'_sub_types'):
            del self.product._sub_types
        super(CustomProduct, self).save(**kwargs)


    class Meta:
        verbose_name = _('Custom Product')
        verbose_name_plural = _('Custom Products')


class CustomTextField(models.Model):
    """
    A text field to be filled in by a customer.
    """

    name = models.CharField(_('Custom field name'), max_length=40, )
    slug = models.SlugField(_("Slug"), help_text=_("Auto-generated from name if blank"),
        blank=True)
    products = models.ForeignKey(CustomProduct, verbose_name=_('Custom Fields'),
        related_name='custom_text_fields')
    sort_order = models.IntegerField(_("Sort Order"),
        help_text=_("The display order for this group."), default=0)
    price_change = CurrencyField(_("Price Change"), max_digits=14,
        decimal_places=6, blank=True, null=True)

    def save(self, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, instance=self)
        super(CustomTextField, self).save(**kwargs)

    def translated_name(self, language_code=None):
        return lookup_translation(self, 'name', language_code)

    class Meta:
        ordering = ('sort_order',)
        unique_together = ('slug', 'products')

class CustomTextFieldTranslation(models.Model):
    """A specific language translation for a `CustomTextField`.  This is intended for all descriptions which are not the
    default settings.LANGUAGE.
    """
    customtextfield = models.ForeignKey(CustomTextField, related_name="translations")
    languagecode = models.CharField(_('language'), max_length=10, choices=settings.LANGUAGES)
    name = models.CharField(_("Translated Custom Text Field Name"), max_length=255, )
    version = models.IntegerField(_('version'), default=1)
    active = models.BooleanField(_('active'), default=True)

    class Meta:
        verbose_name = _('CustomTextField Translation')
        verbose_name_plural = _('CustomTextField Translations')
        ordering = ('customtextfield', 'name','languagecode')
        unique_together = ('customtextfield', 'languagecode', 'version')

    def __unicode__(self):
        return u"CustomTextFieldTranslation: [%s] (ver #%i) %s Name: %s" % (self.languagecode, self.version, self.customtextfield, self.name)
