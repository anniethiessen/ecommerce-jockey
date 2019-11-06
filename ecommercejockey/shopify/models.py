from decimal import Decimal

from slugify import slugify

from django.db.models import (
    Model,
    BooleanField,
    CharField,
    DecimalField,
    ForeignKey,
    ManyToManyField,
    OneToOneField,
    PositiveIntegerField,
    TextField,
    URLField,
    CASCADE,
    Q
)

from core.mixins import MessagesMixin
from core.models import (
    NotesBaseModel,
    RelevancyBaseModel
)
from .managers import (
    ShopifyProductManager,
    ShopifyVariantManager
)


class ShopifyVendor(Model):
    name = CharField(
        max_length=255,
        unique=True
    )

    def __str__(self):
        return self.name


class ShopifyTag(Model):
    name = CharField(
        max_length=255,
        unique=True
    )

    def __str__(self):
        return self.name


class ShopifyCollectionRule(Model):
    column = CharField(
        max_length=25
    )
    relation = CharField(
        max_length=10
    )
    condition = CharField(
        max_length=50
    )

    def __str__(self):
        return f'{self.column} :: {self.relation} :: {self.condition}'


class ShopifyCollection(RelevancyBaseModel, NotesBaseModel):
    WEB_SCOPE = 'web'
    GLOBAL_SCOPE = 'global'
    PUBLISHED_SCOPE_CHOICES = [
        (WEB_SCOPE, WEB_SCOPE),
        (GLOBAL_SCOPE, GLOBAL_SCOPE)
    ]

    ALPHA_ASC_ORDER = 'alpha-asc'
    ALPHA_DEC_ORDER = 'alpha-dec'
    CREATED_ASC_ORDER = 'created'
    CREATED_DEC_ORDER = 'created-desc'
    PRICE_ASC_ORDER = 'price-asc'
    PRICE_DEC_ORDER = 'price-desc'
    BEST_SELLING_ORDER = 'best-selling'
    SORT_ORDER_CHOICES = [
        (ALPHA_ASC_ORDER, 'Alphabetical (ascending)'),
        (ALPHA_DEC_ORDER, 'Alphabetical (descending)'),
        (CREATED_ASC_ORDER, 'Creation Date (ascending)'),
        (CREATED_DEC_ORDER, 'Creation Date (descending)'),
        (PRICE_ASC_ORDER, 'Price (ascending)'),
        (PRICE_DEC_ORDER, 'Price (descending)'),
        (BEST_SELLING_ORDER, 'Best Selling')
    ]

    collection_id = PositiveIntegerField(
        blank=True,
        help_text='Populated by Shopify',
        null=True,
        unique=True
    )
    title = CharField(
        max_length=150
    )
    body_html = TextField(
        blank=True
    )
    image_src = URLField(
        max_length=250
    )
    image_alt = CharField(
        max_length=30
    )
    is_published = BooleanField(
        default=False
    )
    published_scope = CharField(
        choices=PUBLISHED_SCOPE_CHOICES,
        default=WEB_SCOPE,
        max_length=10
    )
    tags = ManyToManyField(
        ShopifyTag,
        blank=True,
        related_name='collections'
    )
    rules = ManyToManyField(
        ShopifyCollectionRule,
        blank=True,
        related_name='collections'
    )
    disjunctive = BooleanField(
        default=False
    )
    sort_order = CharField(
        choices=SORT_ORDER_CHOICES,
        default=BEST_SELLING_ORDER,
        max_length=15
    )

    # <editor-fold desc="relevancy properties ...">
    @property
    def may_be_relevant(self):
        """
        Returns whether or not object may be relevant based on
        attributes and related attributes.

        .. Topic:: **-May Be Relevant Conditions-**

            1.

        :return: whether or not object may be relevant
        :rtype: bool

        """

        return False

    @property
    def relevancy_errors(self):
        """
        Returns a concatenation of errors based on relevancy.

        :return: errors based on relevancy
        :rtype: str

        """

        msgs = []

        if self.is_relevant:
            # if not self.dataset.is_relevant:
            #     error = "dataset not relevant"
            #     msgs.append(error)
            # if not self.vehicle_relevant_count:
            #     error = "no relevant vehicles"
            #     msgs.append(error)
            # if not self.html or self.html == '':
            #     error = "no html"
            #     msgs.append(error)
            # if not self.category_relevant_count == 3:
            #     error = f"{self.category_relevant_count} categories"
            #     msgs.append(error)
            # if not self.description_pies_attribute_count:
            #     error = "missing description PIES"
            #     msgs.append(error)
            # if not self.digital_assets_pies_attribute_count:
            #     error = "missing digital assets PIES"
            #     msgs.append(error)
            pass
        return ', '.join(msgs)
    relevancy_errors.fget.short_description = 'Errors'
    # </editor-fold>

    def __str__(self):
        return self.title


class ShopifyProduct(RelevancyBaseModel, NotesBaseModel):
    APPAREL_TYPE = 'Apparel'
    AUTOMOTIVE_TYPE = 'Automotive Parts'
    PRODUCT_TYPE_CHOICES = [
        (APPAREL_TYPE, APPAREL_TYPE),
        (AUTOMOTIVE_TYPE, AUTOMOTIVE_TYPE)
    ]

    WEB_SCOPE = 'web'
    GLOBAL_SCOPE = 'global'
    PUBLISHED_SCOPE_CHOICES = [
        (WEB_SCOPE, WEB_SCOPE),
        (GLOBAL_SCOPE, GLOBAL_SCOPE)
    ]

    product_id = PositiveIntegerField(
        blank=True,
        help_text='Populated by Shopify',
        null=True,
        unique=True
    )
    title = CharField(
        blank=True,
        max_length=100
    )
    body_html = TextField(
        blank=True,
        verbose_name='body HTML'
    )
    vendor = ForeignKey(
        ShopifyVendor,
        blank=True,
        null=True,
        related_name='products',
        on_delete=CASCADE
    )
    product_type = CharField(
        choices=PRODUCT_TYPE_CHOICES,
        default=AUTOMOTIVE_TYPE,
        max_length=20
    )
    is_published = BooleanField(
        default=False
    )
    published_scope = CharField(
        choices=PUBLISHED_SCOPE_CHOICES,
        default=WEB_SCOPE,
        max_length=10
    )
    tags = ManyToManyField(
        ShopifyTag,
        blank=True,
        related_name='products'
    )
    seo_title = CharField(
        blank=True,
        max_length=200
    )
    seo_description = TextField(
        blank=True
    )

    # <editor-fold desc="relevancy properties ...">
    @property
    def may_be_relevant(self):
        """
        Returns whether or not object may be relevant based on
        attributes and related attributes.

        .. Topic:: **-May Be Relevant Conditions-**

            1. No relevancy errors

        :return: whether or not object may be relevant
        :rtype: bool

        """

        return bool(not self.relevancy_errors)

    @property
    def relevancy_errors(self):
        """
        Returns a concatenation of errors based on relevancy.

        :return: errors based on relevancy
        :rtype: str

        """

        msgs = []
        if not self.title:
            error = "missing title"
            msgs.append(error)
        if not self.body_html:
            error = "missing Body HTML"
            msgs.append(error)
        if not self.vendor:
            error = "missing vendor"
            msgs.append(error)
        if not self.tags.all().count() >= 5:
            error = "missing tags"
            msgs.append(error)
        if not self.images.all().count() >= 1:
            error = "missing tags"
            msgs.append(error)
        if not self.variants.all().count() >= 1:
            error = "missing variants"
            msgs.append(error)
        if not self.variants.first().title == 'Default Title':
            error = "first variant not default title"
            msgs.append(error)
        if not (self.variants.first().weight
                and self.variants.first().weight_unit):
            error = "first variant missing weight"
            msgs.append(error)
        if not self.variants.first().price:
            error = "first variant missing price"
            msgs.append(error)
        if not self.variants.first().cost:
            error = "first variant missing cost"
            msgs.append(error)
        if not self.variants.first().sku:
            error = "first variant missing SKU"
            msgs.append(error)
        if not self.variants.first().barcode:
            error = "first variant missing barcode"
            msgs.append(error)
        return ', '.join(msgs)
    relevancy_errors.fget.short_description = 'Errors'
    # </editor-fold>

    # <editor-fold desc="perform properties ...">
    def perform_calculated_fields_update(self):
        try:
            if self.calculator.title_:
                self.title = self.calculator.title_
            if self.calculator.body_html_:
                self.body_html = self.calculator.body_html_
            for tag_name in self.calculator.tags_:
                tag, _ = ShopifyTag.objects.get_or_create(name=tag_name)
                self.tags.add(tag)
            self.save()
            for image_src in self.calculator.images_:
                image, _ = ShopifyImage.objects.get_or_create(
                    product=self,
                    src=image_src
                )
            return self.get_update_success_msg()
        except Exception as err:
            return self.get_instance_error_msg(str(err))
    # </editor-fold>

    objects = ShopifyProductManager()

    def __str__(self):
        s = []
        if self.vendor:
            s.append(str(self.vendor))
        if self.title:
            s.append(self.title)
        if not s:
            s.append(str(self.id))
        return ' :: '.join(s)


class ShopifyImage(Model):
    product = ForeignKey(
        ShopifyProduct,
        related_name='images',
        on_delete=CASCADE
    )
    image_id = PositiveIntegerField(
        blank=True,
        help_text='Populated by Shopify',
        null=True,
        unique=True
    )
    src = URLField(
        max_length=250
    )
    position = PositiveIntegerField(
        blank=True,
        null=True
    )

    def __str__(self):
        return str(self.product)


class ShopifyOption(Model):
    product = ForeignKey(
        ShopifyProduct,
        related_name='options',
        on_delete=CASCADE
    )
    option_id = PositiveIntegerField(
        blank=True,
        help_text='Populated by Shopify',
        null=True,
        unique=True
    )
    name = CharField(
        max_length=100
    )
    value = TextField()

    def __str__(self):
        return f'{self.product} :: {self.name}'


class ShopifyVariant(Model, MessagesMixin):
    MANUAL_FULFILLMENT = 'manual'
    SHOPIFY_FULFILLMENT = 'create me'
    FULFILLMENT_SERVICE_CHOICES = [
        (MANUAL_FULFILLMENT, MANUAL_FULFILLMENT),
        (SHOPIFY_FULFILLMENT, SHOPIFY_FULFILLMENT)
    ]

    MANUAL_INVENTORY = 'manual'
    SHOPIFY_INVENTORY = 'create me'
    INVENTORY_MANAGEMENT_CHOICES = [
        (MANUAL_INVENTORY, MANUAL_INVENTORY),
        (SHOPIFY_INVENTORY, SHOPIFY_INVENTORY)
    ]

    ALLOW_POLICY = 'allow'
    DENY_POLICY = 'deny'
    INVENTORY_POLICY_CHOICES = [
        (ALLOW_POLICY, ALLOW_POLICY),
        (DENY_POLICY, DENY_POLICY)
    ]

    G_UNIT = 'g'
    KG_UNIT = 'kg'
    OZ_UNIT = 'oz'
    LB_UNIT = 'lb'
    WEIGHT_UNIT_CHOICES = [
        (G_UNIT, G_UNIT),
        (KG_UNIT, KG_UNIT),
        (OZ_UNIT, OZ_UNIT),
        (LB_UNIT, LB_UNIT)
    ]

    product = ForeignKey(
        ShopifyProduct,
        related_name='variants',
        on_delete=CASCADE
    )
    variant_id = PositiveIntegerField(
        blank=True,
        help_text='Populated by Shopify',
        null=True,
        unique=True
    )
    image_id = PositiveIntegerField(
        blank=True,
        help_text='Populated by Shopify',
        null=True
    )
    inventory_item_id = PositiveIntegerField(
        blank=True,
        help_text='Populated by Shopify',
        null=True
    )
    title = CharField(
        default='Default Title',
        max_length=30
    )
    grams = PositiveIntegerField(
        blank=True,
        null=True
    )
    weight = PositiveIntegerField(
        blank=True,
        null=True
    )
    weight_unit = CharField(
        blank=True,
        choices=WEIGHT_UNIT_CHOICES,
        max_length=3,
        null=True
    )
    inventory_management = CharField(
        choices=INVENTORY_MANAGEMENT_CHOICES,
        default=SHOPIFY_INVENTORY,
        max_length=100
    )
    inventory_policy = CharField(
        choices=INVENTORY_POLICY_CHOICES,
        default=ALLOW_POLICY,
        max_length=10
    )
    fulfillment_service = CharField(
        choices=FULFILLMENT_SERVICE_CHOICES,
        default=MANUAL_FULFILLMENT,
        max_length=100
    )
    price = DecimalField(
        blank=True,
        decimal_places=2,
        max_digits=10,
        null=True
    )
    compare_at_price = DecimalField(
        blank=True,
        decimal_places=2,
        max_digits=10,
        null=True
    )
    cost = DecimalField(
        blank=True,
        decimal_places=2,
        max_digits=10,
        null=True
    )
    sku = CharField(
        blank=True,
        max_length=50
    )
    barcode = CharField(
        blank=True,
        max_length=50
    )
    is_taxable = BooleanField(
        default=True
    )
    tax_code = CharField(
        blank=True,
        max_length=20
    )

    # <editor-fold desc="perform properties ...">
    def perform_calculated_fields_update(self):
        try:
            if self.product.calculator.weight_:
                self.weight = self.product.calculator.weight_
            if self.product.calculator.weight_unit_:
                self.weight_unit = self.product.calculator.weight_unit_
            if self.product.calculator.cost_:
                self.cost = self.product.calculator.cost_
            if self.product.calculator.price_:
                self.price = self.product.calculator.price_
            if self.product.calculator.sku_:
                self.sku = self.product.calculator.sku_
            if self.product.calculator.barcode_:
                self.barcode = self.product.calculator.barcode_
            self.save()
            return self.get_update_success_msg()
        except Exception as err:
            return self.get_instance_error_msg(str(err))
    # </editor-fold>

    objects = ShopifyVariantManager()

    def __str__(self):
        s = str(self.product)
        if self.title:
            s += f' :: {self.title}'
        return s


class ShopifyCalculator(Model):
    product = OneToOneField(
        ShopifyProduct,
        related_name='calculator',
        on_delete=CASCADE
    )

    # <editor-fold desc="update logic properties ...">
    @property
    def __has_sema_product(self):
        return bool(self.product.item and self.product.item.sema_product)

    @property
    def __has_premier_product(self):
        return bool(self.product.item and self.product.item.premier_product)

    @property
    def sema_product(self):
        return (
            self.product.item.sema_product
            if self.__has_sema_product else None
        )

    @property
    def premier_product(self):
        return (
            self.product.item.premier_product
            if self.__has_premier_product else None
        )

    @property
    def title_(self):
        if (self.__has_sema_product
                and self.sema_product.description_pies_attributes.filter(
                    segment='C10_SHO_EN').exists()):
            return self.sema_product.description_pies_attributes.get(
                segment='C10_SHO_EN').value
        return ''
    title_.fget.short_description = ''

    @property
    def body_html_(self):
        if (self.__has_sema_product
                and self.sema_product.description_pies_attributes.filter(
                    segment='C10_EXT_EN').exists()):
            return self.sema_product.description_pies_attributes.get(
                segment='C10_EXT_EN').value
        return ''
    body_html_.fget.short_description = ''

    @property
    def meta_field_sema_html_(self):
        if self.__has_sema_product and self.sema_product.html:
            return self.sema_product.html
        return ''
    meta_field_sema_html_.fget.short_description = ''

    @property
    def vendor_tags_(self):
        tags = []
        if self.product.vendor:
            tags.append(f'vendor:{self.product.vendor.vendor.slug}')
        return tags
    vendor_tags_.fget.short_description = ''

    @property
    def category_tags_(self):
        tags = []
        if (self.__has_sema_product
                and self.sema_product.categories.filter(
                    is_relevant=True).exists()):
            categories = self.sema_product.categories.filter(
                is_relevant=True
            ).values_list('name', flat=True)
            for category in categories:
                tags.append(f'category:{slugify(category)}')
        return tags
    category_tags_.fget.short_description = ''

    @property
    def base_vehicle_tags_(self):
        tags = []
        if self.__has_sema_product:
            if self.sema_product.vehicle_count:
                vehicles = self.sema_product.vehicles.filter(
                    is_relevant=True
                )
            else:
                vehicles = self.sema_product.dataset.vehicles.filter(
                    is_relevant=True
                )
            base_vehicles = [vehicle.base_vehicle_id for vehicle in vehicles]
            base_vehicles = list(dict.fromkeys(base_vehicles))
            for base_vehicle in base_vehicles:
                tags.append(f'base-vehicle:{base_vehicle}')
        return tags
    base_vehicle_tags_.fget.short_description = ''

    @property
    def tags_(self):
        return (
            self.vendor_tags_
            + self.category_tags_
            + self.base_vehicle_tags_
        )
    tags_.fget.short_description = ''

    @property
    def seo_title_(self):
        return ''
    seo_title_.fget.short_description = ''

    @property
    def seo_description_(self):
        return ''
    seo_description_.fget.short_description = ''

    @property
    def weight_(self):
        if self.__has_premier_product and self.premier_product.weight:
            return int(self.premier_product.weight)
        return ''
    weight_.fget.short_description = ''

    @property
    def weight_unit_(self):
        if self.__has_premier_product and self.premier_product.weight:
            return ShopifyVariant.LB_UNIT
        return ''
    weight_unit_.fget.short_description = ''

    @property
    def cost_(self):
        if self.__has_premier_product and self.premier_product.cost_cad:
            return self.premier_product.cost_cad
        return ''
    cost_.fget.short_description = ''

    @property
    def price_(self):
        if self.cost_:
            return round(self.cost_ * Decimal(1.2), 2)
        return ''
    price_.fget.short_description = ''

    @property
    def sku_(self):
        if self.__has_premier_product:
            return self.premier_product.premier_part_number
        return ''
    sku_.fget.short_description = ''

    @property
    def barcode_(self):
        if self.__has_premier_product and self.premier_product.upc:
            return self.premier_product.upc
        return ''
    barcode_.fget.short_description = ''

    @property
    def images_(self):
        images = []
        if self.__has_sema_product:
            values = self.sema_product.digital_assets_pies_attributes.exclude(
                Q(value__endswith='.pdf')
                | Q(value__contains='logo')
            ).values_list('value', flat=True)
            images += list(values)
        return images
    images_.fget.short_description = ''
    # </editor-fold>

    def __str__(self):
        return str(self.product)
