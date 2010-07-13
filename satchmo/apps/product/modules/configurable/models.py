from decimal import Decimal
from django import forms
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import smart_str
from product.models import Option, Product, ProductPriceLookup, OptionGroup, Price ,make_option_unique_id
from product.prices import get_product_quantity_price, get_product_quantity_adjustments
from satchmo_utils import cross_list
from satchmo_utils.unique_id import slugify
import datetime
import logging

SATCHMO_PRODUCT=True

def get_product_types():
    return ('ConfigurableProduct','ProductVariation')

def sorted_tuple(lst):
    ret = []
    for x in lst:
        if not x in ret:
            ret.append(x)
    ret.sort()
    return tuple(ret)

log = logging.getLogger('product.modules.configurable')

def get_all_options(obj, ids_only=False):
    """
    Returns all possible combinations of options for this products OptionGroups as a List of Lists.
    Ex:
    For OptionGroups Color and Size with Options (Blue, Green) and (Large, Small) you'll get
    [['Blue', 'Small'], ['Blue', 'Large'], ['Green', 'Small'], ['Green', 'Large']]
    Note: the actual values will be instances of Option instead of strings
    """
    sublist = []
    masterlist = []
    #Create a list of all the options & create all combos of the options
    for opt in obj.option_group.select_related().all():
        for value in opt.option_set.all():
            if ids_only:
                sublist.append(value.unique_id)
            else:
                sublist.append(value)
        masterlist.append(sublist)
        sublist = []
    results = cross_list(masterlist)
    return results

class ConfigurableProduct(models.Model):
    """
    Product with selectable options.
    This is a sort of virtual product that is visible to the customer, but isn't actually stocked on a shelf,
    the specific "shelf" product is determined by the selected options.
    """
    product = models.OneToOneField(Product, verbose_name=_("Product"), primary_key=True)
    option_group = models.ManyToManyField(OptionGroup, blank=True, verbose_name=_("Option Group"))
    create_subs = models.BooleanField(_("Create Variations"), default=False, help_text =_("Create ProductVariations for all this product's options.  To use this, you must first add an option, save, then return to this page and select this option."))

    def __init__(self, *args, **kwargs):
        super(ConfigurableProduct, self).__init__(*args, **kwargs)

    def _get_subtype(self):
        return 'ConfigurableProduct'

    def get_all_options(self):
        """
        Returns all possible combinations of options for this products OptionGroups as a List of Lists.
        Ex:
        For OptionGroups Color and Size with Options (Blue, Green) and (Large, Small) you'll get
        [['Blue', 'Small'], ['Blue', 'Large'], ['Green', 'Small'], ['Green', 'Large']]
        Note: the actual values will be instances of Option instead of strings
        """
        sublist = []
        masterlist = []
        #Create a list of all the options & create all combos of the options
        for opt in self.option_group.all():
            for value in opt.option_set.all():
                sublist.append(value)
            masterlist.append(sublist)
            sublist = []
        return cross_list(masterlist)

    def get_valid_options(self):
        """
        Returns unique_ids from get_all_options(), but filters out Options that this
        ConfigurableProduct doesn't have a ProductVariation for.
        """
        variations = self.productvariation_set.filter(product__active='1')
        active_options = [v.unique_option_ids for v in variations]
        all_options = get_all_options(self, ids_only=True)
        return [opt for opt in all_options if self._unique_ids_from_options(opt) in active_options]

    def create_all_variations(self):
        """
        Get a list of all the optiongroups applied to this object
        Create all combinations of the options and create variations
        """
        # Create a new ProductVariation for each combination.
        for options in self.get_all_options():
            self.create_variation(options)

    def create_variation(self, options, name=u"", sku=u"", slug=u""):
        """Create a productvariation with the specified options.
        Will not create a duplicate."""
        log.debug("Create variation: %s", options)
        variations = self.get_variations_for_options(options)

        if not variations:
            # There isn't an existing ProductVariation.
            if self.product:
                site = self.product.site
            else:
                site = self.site

            variant = Product(site=site, items_in_stock=0, name=name)
            optnames = [opt.value for opt in options]
            if not slug:
                slug = slugify(u'%s_%s' % (self.product.slug, u'_'.join(optnames)))

            while Product.objects.filter(slug=slug).count():
                slug = u'_'.join((slug, unicode(self.product.id)))

            variant.slug = slug

            log.info("Creating variation for [%s] %s", self.product.slug, variant.slug)
            variant.save()

            pv = ProductVariation(product=variant, parent=self)
            pv.save()

            for option in options:
                pv.options.add(option)

            pv.name = name
            pv.sku = sku
            pv.save()

        else:
            variant = variations[0].product
            log.debug("Existing variant: %s", variant)
            dirty = False
            if name and name != variant.name:
                log.debug("Updating name: %s --> %s", self, name)
                variant.name = name
                dirty = True
            if sku and sku != variant.sku:
                variant.sku = sku
                log.debug("Updating sku: %s --> %s", self, sku)
                dirty = True
            if slug:
                # just in case
                slug = slugify(slug)
            if slug and slug != variant.slug:
                variant.slug = slug
                log.debug("Updating slug: %s --> %s", self, slug)
                dirty = True
            if dirty:
                log.debug("Changed existing variant, saving: %s", variant)
                variant.save()
            else:
                log.debug("No change to variant, skipping save: %s", variant)

        return variant

    def _unique_ids_from_options(self, options):
        """
        Takes an iterable of Options (or str(Option)) and outputs a sorted tuple of
        option unique ids suitable for comparing to a productvariation.option_values
        """
        optionlist = []
        for opt in options:
            if isinstance(options[0], Option):
                opt = opt.unique_id
            optionlist.append(opt)

        return sorted_tuple(optionlist)

    def get_product_from_options(self, options):
        """
        Accepts an iterable of either Option object or a sorted tuple of
        options ids.
        Returns the product that matches or None
        """
        options = self._unique_ids_from_options(options)
        pv = None
        if hasattr(self, '_variation_cache'):
            pv =  self._variation_cache.get(options, None)
        else:
            for member in self.productvariation_set.all():
                if member.unique_option_ids == options:
                    pv = member
                    break
        if pv:
            return pv.product
        return None

    def get_variations_for_options(self, options):
        """
        Returns a list of existing ProductVariations with the specified options.
        """
        variations = ProductVariation.objects.filter(parent=self)
        for option in options:
            variations = variations.filter(options=option)
        return variations

    def add_template_context(self, context, request, selected_options, default_view_tax=False, **kwargs):
        """
        Add context for the product template.
        Return the updated context.
        """
        from product.utils import productvariation_details, serialize_options

        selected_options = self._unique_ids_from_options(selected_options)

        options = serialize_options(self, selected_options)
        if not 'options' in context:
            context['options'] = options
        else:
            curr = list(context['options'])
            curr.extend(list(options))
            context['options'] = curr

        details = productvariation_details(self.product, default_view_tax,
                                           request.user)
        if 'details' in context:
            context['details'].update(details)
        else:
            context['details'] = details

        return context

    def save(self, **kwargs):
        """
        Right now this only works if you save the suboptions, then go back and choose to create the variations.
        """
        super(ConfigurableProduct, self).save(**kwargs)
        if hasattr(self.product,'_sub_types'):
            del self.product._sub_types
        # Doesn't work with admin - the manipulator doesn't add the option_group
        # until after save() is called.
        if self.create_subs and self.option_group.count():
            self.create_all_variations()
            self.create_subs = False
            super(ConfigurableProduct, self).save(**kwargs)

        ProductPriceLookup.objects.smart_create_for_product(self.product)

    def get_absolute_url(self):
        return self.product.get_absolute_url()

    def setup_variation_cache(self):
        self._variation_cache = {}
        for member in self.productvariation_set.all():
            key = member.unique_option_ids
            self._variation_cache[key] = member

    class Meta:
        verbose_name = _("Configurable Product")
        verbose_name_plural = _("Configurable Products")

    def __unicode__(self):
        return self.product.slug


class ProductVariationManager(models.Manager):

    def by_parent(self, parent):
        """Get the list of productvariations which have the `product` as the parent"""
        return ProductVariation.objects.filter(parent=parent)

class ProductVariation(models.Model):
    """
    This is the real Product that is ordered when a customer orders a
    ConfigurableProduct with the matching Options selected

    """
    product = models.OneToOneField(Product, verbose_name=_('Product'), primary_key=True)
    options = models.ManyToManyField(Option, verbose_name=_('Options'))
    parent = models.ForeignKey(ConfigurableProduct, verbose_name=_('Parent'))

    objects = ProductVariationManager()

    def _get_fullPrice(self):
        """ Get price based on parent ConfigurableProduct """
        # allow explicit setting of prices.
        #qty_discounts = self.price_set.exclude(expires__isnull=False, expires__lt=datetime.date.today()).filter(quantity__lte=1)
        try:
            qty_discounts = Price.objects.filter(product__id=self.product.id).exclude(expires__isnull=False, expires__lt=datetime.date.today())
            if qty_discounts.count() > 0:
                # Get the price with the quantity closest to the one specified without going over
                return qty_discounts.order_by('-quantity')[0].dynamic_price

            if self.parent.product.unit_price is None:
                log.warn("%s: Unexpectedly no parent.product.unit_price", self)
                return None

        except AttributeError:
            pass

        # calculate from options
        return self.parent.product.unit_price + self.price_delta()

    unit_price = property(_get_fullPrice)

    def _get_optionName(self):
        "Returns the options in a human readable form"
        if self.options.count() == 0:
            return self.parent.verbose_name
        output = self.parent.verbose_name + " ( "
        numProcessed = 0
        # We want the options to be sorted in a consistent manner
        optionDict = dict([(sub.option_group.sort_order, sub) for sub in self.options.all()])
        for optionNum in optionDict.keys().sort():
            numProcessed += 1
            if numProcessed == self.options.count():
                output += optionDict[optionNum].name
            else:
                output += optionDict[optionNum].name + "/"
        output += " )"
        return output
    full_name = property(_get_optionName)

    def _optionkey(self):
        #todo: verify ordering
        optkeys = [smart_str(x) for x in self.options.values_list('value', flat=True).order_by('option_group__id')]
        return "::".join(optkeys)
    optionkey = property(fget=_optionkey)

    def _get_option_ids(self):
        """
        Return a sorted tuple of all the valid options for this variant.
        """
        qry = self.options.values_list('option_group__id', 'value').order_by('option_group')
        ret = [make_option_unique_id(*v) for v in qry]
        return sorted_tuple(ret)

    unique_option_ids = property(_get_option_ids)

    def _get_subtype(self):
        return 'ProductVariation'

    def _has_variants(self):
        return True
    has_variants = property(_has_variants)

    def _get_category(self):
        """
        Return the primary category associated with this product
        """
        return self.parent.product.category.all()[0]
    get_category = property(_get_category)

    def _check_optionParents(self):
        groupList = []
        for option in self.options.all():
            if option.option_group.id in groupList:
                return(True)
            else:
                groupList.append(option.option_group.id)
        return(False)

    def get_qty_price(self, qty, include_discount=True):
        if include_discount:
            price = get_product_quantity_price(
                self.product, qty,
                delta=self.price_delta(False),
                parent=self.parent.product)
        else:
            adjustment = get_product_quantity_adjustments(self, qty, parent=self.parent.product)
            if adjustment.price is not None:
                price = adjustment.price.price + self.price_delta(True)
            else:
                price = None

        return price

    def get_qty_price_list(self):
        """Return a list of tuples (qty, price)"""
        prices = Price.objects.filter(product__id=self.product.id).exclude(expires__isnull=False, expires__lt=datetime.date.today())
        if prices.count() > 0:
            # prices directly set, return them
            pricelist = [(price.quantity, price.dynamic_price) for price in prices]
        else:
            prices = self.parent.product.get_qty_price_list()
            price_delta = self.price_delta()

            pricelist = [(qty, price+price_delta) for qty, price in prices]

        return pricelist

    def _is_shippable(self):
        product = self.product
        parent = self.parent.product
        return (product.shipclass == 'YES' or
                (product.shipclass == "DEFAULT"
                 and parent.shipclass in ("DEFAULT", "YES"))
                )

    is_shippable = property(fget=_is_shippable)

    def isValidOption(self, field_data, all_data):
        raise forms.ValidationError(_("Two options from the same option group cannot be applied to an item."))

    def price_delta(self, include_discount=True):
        # TODO: deltas aren't taken into account by satchmo_price_query
        price_delta = Decimal("0.00")
        for option in self.options.all():
            if option.price_change:
                price_delta += Decimal(option.price_change)
        return price_delta

    def save(self, **kwargs):
        # don't save if the product is a configurableproduct
        if "ConfigurableProduct" in self.product.get_subtypes():
            log.warn("cannot add a productvariation subtype to a product which already is a configurableproduct. Aborting")
            return

        pvs = ProductVariation.objects.filter(parent=self.parent)
        pvs = pvs.exclude(product=self.product)
        for pv in pvs:
            if pv.unique_option_ids == self.unique_option_ids:
                return # Don't allow duplicates

        if not self.product.name:
            # will force calculation of default name
            self.name = ""

        super(ProductVariation, self).save(**kwargs)
        ProductPriceLookup.objects.smart_create_for_product(self.product)

    def _set_name(self, name):
        if not name:
            name = self.parent.product.name
            options = [option.name for option in self.options.order_by("option_group")]
            if options:
                name = u'%s (%s)' % (name, u'/'.join(options))
            log.debug("Setting default name for ProductVariant: %s", name)

        self.product.name = name
        self.product.save()

    def _get_name(self):
        return self.product.name

    name = property(fset=_set_name, fget=_get_name)

    def _set_sku(self, sku):
        if not sku:
            sku = self.product.slug
        self.product.sku = sku
        self.product.save()

    def _get_sku(self):
        return self.product.sku

    sku = property(fset=_set_sku, fget=_get_sku)

    def get_absolute_url(self):
        return self.product.get_absolute_url()

    class Meta:
        verbose_name = _("Product variation")
        verbose_name_plural = _("Product variations")

    def __unicode__(self):
        return self.product.slug
