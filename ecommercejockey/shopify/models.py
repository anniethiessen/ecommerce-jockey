import json
from decimal import Decimal

from jsondiff import diff

from django.conf import settings
from django.contrib.contenttypes.fields import (
    GenericForeignKey,
    GenericRelation
)
from django.contrib.contenttypes.models import ContentType
from django.db.models import (
    Model,
    BigIntegerField,
    BooleanField,
    CharField,
    DecimalField,
    ForeignKey,
    ManyToManyField,
    OneToOneField,
    IntegerField,
    PositiveIntegerField,
    SlugField,
    TextField,
    URLField,
    CASCADE,
    SET_NULL,
    Q
)
from django.utils.html import mark_safe

from core.mixins import MessagesMixin
from core.models import (
    NotesBaseModel,
    RelevancyBaseModel
)
from core.admin.utils import (
    get_html_preview,
    # get_image_preview,
    get_images_preview,
    get_json_preview
)
from .clients import shopify_client
from .managers import (
    ShopifyCollectionCalculatorManager,
    ShopifyCollectionManager,
    ShopifyCollectionRuleManager,
    ShopifyImageManager,
    ShopifyOptionManager,
    ShopifyMetafieldManager,
    ShopifyProductCalculatorManager,
    ShopifyProductManager,
    ShopifyTagManager,
    ShopifyVariantManager,
    ShopifyVendorManager
)


class ShopifyVendor(Model, MessagesMixin):
    name = CharField(
        max_length=255,
        unique=True
    )

    # <editor-fold desc="error properties ...">
    @property
    def warnings(self):
        """
        Returns a concatenation of warnings.

        :return: warnings
        :rtype: str

        """

        msgs = []
        return ', '.join(msgs)

    @property
    def errors(self):
        """
        Returns a concatenation of errors.

        :return: errors
        :rtype: str

        """

        msgs = []
        return ', '.join(msgs)
    # </editor-fold>

    # <editor-fold desc="count properties ...">
    @property
    def product_count(self):
        """
        Returns product count.

        :return: product count
        :rtype: int

        """

        return self.products.distinct().count()
    product_count.fget.short_description = 'product count'

    @property
    def product_published_count(self):
        """
        Returns published product count.

        :return: published product count
        :rtype: int

        """

        return self.products.filter(is_published=True).distinct().count()
    product_published_count.fget.short_description = 'published product count'
    # </editor-fold>

    objects = ShopifyVendorManager()

    def __str__(self):
        return self.name


class ShopifyTag(Model, MessagesMixin):
    name = CharField(
        max_length=255,
        unique=True
    )

    # <editor-fold desc="count properties ...">
    @property
    def product_count(self):
        return self.products.count()
    product_count.fget.short_description = 'product count'

    @property
    def product_published_count(self):
        return self.products.filter(is_published=True).count()
    product_published_count.fget.short_description = 'published product count'

    @property
    def collection_count(self):
        return self.collections.count()
    collection_count.fget.short_description = 'collection count'

    @property
    def collection_published_count(self):
        return self.collections.filter(is_published=True).count()
    collection_published_count.fget.short_description = (
        'published collection count'
    )
    # </editor-fold>
    
    objects = ShopifyTagManager()

    def __str__(self):
        return self.name


class ShopifyMetafield(Model, MessagesMixin):
    PRODUCT_OWNER_RESOURCE = 'product'
    COLLECTION_OWNER_RESOURCE = 'smart_collection'
    OWNER_RESOURCE_CHOICES = [
        (PRODUCT_OWNER_RESOURCE, PRODUCT_OWNER_RESOURCE),
        (COLLECTION_OWNER_RESOURCE, 'collection')
    ]

    STRING_VALUE_TYPE = 'string'
    INTEGER_VALUE_TYPE = 'integer'
    JSON_VALUE_TYPE = 'json_string'
    VALUE_TYPE_CHOICES = [
        (STRING_VALUE_TYPE, STRING_VALUE_TYPE),
        (INTEGER_VALUE_TYPE, INTEGER_VALUE_TYPE),
        (JSON_VALUE_TYPE, 'json')
    ]

    content_type = ForeignKey(
        ContentType,
        limit_choices_to=(
            Q(app_label='shopify', model='shopifyproduct')
            | Q(app_label='shopify', model='shopifycollection')
        ),
        on_delete=CASCADE
    )
    object_id = PositiveIntegerField()
    content_object = GenericForeignKey()
    metafield_id = BigIntegerField(
        blank=True,
        help_text='Populated by Shopify',
        null=True,
        unique=True
    )
    owner_resource = CharField(
        choices=OWNER_RESOURCE_CHOICES,
        max_length=20
    )
    namespace = CharField(
        max_length=20
    )
    value_type = CharField(
        choices=VALUE_TYPE_CHOICES,
        default=STRING_VALUE_TYPE,
        max_length=15
    )
    key = CharField(
        max_length=30
    )
    value = TextField(
        max_length=100
    )

    # <editor-fold desc="count properties ...">
    def value_item_count(self):
        if not self.pk:
            return None

        if self.value_type == self._meta.model.JSON_VALUE_TYPE:
            value = json.loads(self.value)
            if isinstance(value, list):
                return len(value)
        return 'N/A'
    value_item_count.short_description = 'item count'
    # </editor-fold>

    # <editor-fold desc="format properties ...">
    @property
    def api_formatted_data(self):
        data = {
            'id': self.metafield_id,
            'owner_resource': self.owner_resource,
            'namespace': self.namespace,
            'value_type': self.value_type,
            'key': self.key,
            'value': self.value
        }
        return dict((k, v) for k, v in data.items() if v)
    # </editor-fold>

    # <editor-fold desc="update properties ...">
    @property
    def state(self):
        return {
            'metafield_id': str(self.metafield_id),
            'namespace': self.namespace,
            'value_type': self.value_type,
            'key': self.key,
            'value': self.value
        }

    def update_metafield_id_from_api_data(self, value):
        try:
            if not self.metafield_id == value:
                self.metafield_id = value
                self.save()
            return
        except Exception:
            raise

    def update_namespace_from_api_data(self, value):
        try:
            if not self.namespace == value:
                self.namespace = value
                self.save()
            return
        except Exception:
            raise

    def update_value_type_from_api_data(self, value):
        try:
            if not self.value_type == value:
                self.value_type = value
                self.save()
            return
        except Exception:
            raise

    def update_key_from_api_data(self, value):
        try:
            if not self.key == value:
                self.key = value
                self.save()
            return
        except Exception:
            raise

    def update_value_from_api_data(self, value):
        try:
            if not self.value == value:
                self.value = value
                self.save()
            return
        except Exception:
            raise

    def update_from_api_data(self, data, *fields):
        field_map = {
            'metafield_id': {
                'data': 'id',
                'function': 'update_metafield_id_from_api_data'
            },
            'namespace': {
                'data': 'namespace',
                'function': 'update_namespace_from_api_data'
            },
            'value_type': {
                'data': 'value_type',
                'function': 'update_value_type_from_api_data'
            },
            'key': {
                'data': 'key',
                'function': 'update_key_from_api_data'
            },
            'value': {
                'data': 'value',
                'function': 'update_value_from_api_data'
            }
        }

        if fields:
            for field in fields:
                if field not in field_map.keys():
                    raise Exception('Invalid update field')
        else:
            fields = field_map.keys()

        msgs = []
        prev = self.state
        for field in fields:
            try:
                extra_msgs = getattr(
                    self,
                    field_map[field]['function']
                )(data[field_map[field]['data']])

                if extra_msgs:
                    msgs += extra_msgs
            except Exception as err:
                msgs.append(
                    self.get_instance_error_msg(
                        error=f'{field} update error: {err}')
                )
                continue

        self.refresh_from_db()
        new = self.state
        msgs.append(
            self.get_update_success_msg(
                previous_data=prev,
                new_data=new
            )
        )

        if not msgs:
            msgs.append(self.get_instance_up_to_date_msg())
        return msgs
    # </editor-fold>

    # <editor-fold desc="perform properties ...">
    def perform_create_to_api(self):
        msgs = []
        if self.metafield_id:
            msgs.append(
                self.get_instance_error_msg(
                    error="Already exists in Shopify")
            )
            return msgs

        try:
            if self.content_type == ContentType.objects.get_for_model(
                    ShopifyProduct):
                client_method = 'create_product_metafield'
                id_field = 'product_id'
            elif self.content_type == ContentType.objects.get_for_model(
                    ShopifyCollection):
                client_method = 'create_collection_metafield'
                id_field = 'collection_id'
            else:
                raise Exception('Invalid content type')

            data = getattr(shopify_client, client_method)(
                getattr(self.content_object, id_field),
                metafield_data=self.api_formatted_data
            )
            msgs.append(
                self.get_create_success_msg(message="Created in Shopify")
            )
            msgs += self.update_from_api_data(data)
        except Exception as err:
            msgs.append(self.get_instance_error_msg(str(err)))

        if not msgs:
            msgs.append(self.get_instance_up_to_date_msg())
        return msgs

    def perform_update_to_api(self):
        msgs = []
        if not self.metafield_id:
            msgs.append(
                self.get_instance_error_msg(
                    error="Doesn't exists in Shopify")
            )
            return msgs

        try:
            if self.content_type == ContentType.objects.get_for_model(
                    ShopifyProduct):
                client_method = 'update_product_metafield'
                id_field = 'product_id'
            elif self.content_type == ContentType.objects.get_for_model(
                    ShopifyCollection):
                client_method = 'update_collection_metafield'
                id_field = 'collection_id'
            else:
                raise Exception('Invalid content type')

            getattr(shopify_client, client_method)(
                getattr(self.content_object, id_field),
                metafield_data=self.api_formatted_data
            )

            msgs.append(
                self.get_update_success_msg(message="Updated in Shopify")
            )
        except Exception as err:
            msgs.append(self.get_instance_error_msg(str(err)))

        if not msgs:
            msgs.append(self.get_instance_up_to_date_msg())
        return msgs

    def perform_update_from_api(self):
        msgs = []
        if not self.metafield_id:
            msgs.append(
                self.get_instance_error_msg(
                    error="Doesn't exists in Shopify")
            )
            return msgs

        try:
            if self.content_type == ContentType.objects.get_for_model(
                    ShopifyProduct):
                client_method = 'retrieve_product_metafield'
                id_field = 'product_id'
            elif self.content_type == ContentType.objects.get_for_model(
                    ShopifyCollection):
                client_method = 'retrieve_collection_metafield'
                id_field = 'collection_id'
            else:
                raise Exception('Invalid content type')

            data = getattr(shopify_client, client_method)(
                getattr(self.content_object, id_field),
                metafield_id=self.metafield_id
            )

            msgs += self.update_from_api_data(data)

        except Exception as err:
            msgs.append(self.get_instance_error_msg(str(err)))

        if not msgs:
            msgs.append(self.get_instance_up_to_date_msg())
        return msgs
    # </editor-fold>

    objects = ShopifyMetafieldManager()

    class Meta:
        unique_together = [
            'content_type',
            'object_id',
            'owner_resource',
            'namespace',
            'key'
        ]

    def delete(self, using=None, keep_parents=False):
        if self.metafield_id:
            try:
                if self.content_type == ContentType.objects.get_for_model(
                        ShopifyProduct):
                    client_method = 'delete_product_metafield'
                    id_field = 'product_id'
                elif self.content_type == ContentType.objects.get_for_model(
                        ShopifyCollection):
                    client_method = 'delete_collection_metafield'
                    id_field = 'collection_id'
                else:
                    raise Exception('Invalid content type')

                getattr(shopify_client, client_method)(
                    getattr(self.content_object, id_field),
                    metafield_id=self.metafield_id
                )
            except Exception as err:
                raise

        super().delete(using=using, keep_parents=keep_parents)

    def __str__(self):
        return f'{self.content_object} :: {self.namespace} :: {self.key}'


class ShopifyCollectionRule(Model, MessagesMixin):
    column = CharField(
        max_length=25
    )
    relation = CharField(
        max_length=10
    )
    condition = CharField(
        max_length=200
    )

    # <editor-fold desc="count properties ...">
    @property
    def collection_count(self):
        return self.collections.count()
    collection_count.fget.short_description = 'collection count'

    @property
    def collection_published_count(self):
        return self.collections.filter(is_published=True).count()
    collection_published_count.fget.short_description = (
        'published collection count'
    )
    # </editor-fold>
    
    objects = ShopifyCollectionRuleManager()

    def __str__(self):
        return f'{self.column} :: {self.relation} :: {self.condition}'


class ShopifyCollection(Model, MessagesMixin):
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

    collection_id = BigIntegerField(
        blank=True,
        help_text='Populated by Shopify',
        null=True,
        unique=True
    )
    handle = SlugField(
        blank=True,
        help_text='Populated by Shopify',
        max_length=150
    )
    title = CharField(
        max_length=150
    )
    body_html = TextField(
        blank=True
    )
    image_src = URLField(
        blank=True,
        max_length=250
    )
    image_alt = CharField(
        blank=True,
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
    parent_collection = ForeignKey(
        'self',
        blank=True,
        null=True,
        on_delete=SET_NULL,
        related_name='child_collections'
    )
    metafields = GenericRelation(
        ShopifyMetafield,
        related_query_name='collection'
    )

    @property
    def level(self):
        if self.parent_collection:
            if self.child_collections.count():
                return '2'
            else:
                return '3'
        else:
            if self.child_collections.count():
                return '1'
            else:
                return ''

    # <editor-fold desc="count properties ...">
    @property
    def tag_count(self):
        return self.tags.count()
    tag_count.fget.short_description = 'tag count'

    @property
    def metafield_count(self):
        return self.metafields.count()
    metafield_count.fget.short_description = 'metafield mount'

    @property
    def rule_count(self):
        return self.rules.count()
    rule_count.fget.short_description = 'rule count'

    @property
    def child_collection_count(self):
        return self.child_collections.count()
    child_collection_count.fget.short_description = 'child count'

    @property
    def child_collection_published_count(self):
        return self.child_collections.filter(is_published=True).count()
    child_collection_published_count.fget.short_description = (
        'published child count'
    )
    # </editor-fold>

    # <editor-fold desc="error properties ...">
    @property
    def warnings(self):
        """
        Returns a concatenation of warnings.

        :return: warnings
        :rtype: str

        """

        msgs = []
        return ', '.join(msgs)

    @property
    def errors(self):
        """
        Returns a concatenation of errors.

        :return: errors
        :rtype: str

        """

        msgs = []
        return ', '.join(msgs)
    # </editor-fold>

    # <editor-fold desc="format properties ...">
    @property
    def api_formatted_data(self):
        data = {
            'id': self.collection_id,
            'title': self.title,
            'body_html': self.api_formatted_body_html,
            'published': self.is_published,
            'published_scope': self.published_scope,
            'rules': self.api_formatted_rules,
            'disjunctive': self.disjunctive,
            'sort_order': self.sort_order
        }
        if self.image_src:
            image_data = {
                'image_src': self.image_src,
                'image_alt': self.image_alt
            }
            data['image'] = image_data
        return dict((k, v) for k, v in data.items() if v)

    @property
    def api_formatted_body_html(self):
        if not self.body_html:
            return self.body_html
        return f"<strong>{self.body_html}</strong>"

    @property
    def api_formatted_rules(self):
        rules = []
        for rule in self.rules.all():
            rules.append(
                {
                    "column": rule.column,
                    "relation": rule.relation,
                    "condition": rule.condition
                }
            )
        for tag in self.tags.all():
            rules.append(
                {
                    "column": 'tag',
                    "relation": 'equals',
                    "condition": tag.name
                }
            )
        return rules
    # </editor-fold>

    # <editor-fold desc="update properties ...">
    @property
    def state(self):
        return {
            'collection_id': str(self.collection_id),
            'title': self.title,
            'handle': self.handle,
            'body_html': self.body_html,
            'image_src': self.image_src,
            'image_alt': self.image_alt,
            'published': str(self.is_published),
            'published_scope': self.published_scope,
            'tags': str(self.tags.count()),
            'rules': str(self.rules.count()),
            'disjunctive': str(self.disjunctive),
            'sort_order': self.sort_order
        }

    def update_collection_id_from_api_data(self, value):
        try:
            if not self.collection_id == value:
                self.collection_id = value
                self.save()
            return
        except Exception:
            raise

    def update_title_from_api_data(self, value):
        try:
            if not self.title == value:
                self.title = value
                self.save()
            return
        except Exception:
            raise

    def update_handle_from_api_data(self, value):
        try:
            if not self.handle == value:
                self.handle = value
                self.save()
            return
        except Exception:
            raise

    def update_body_html_from_api_data(self, value):
        try:
            if value:
                value = value.replace(
                    '<strong>', ''
                ).replace(
                    '</strong>', ''
                ).replace(
                    '&amp;', '&'
                )
            else:
                value = ''
            if not self.body_html == value:
                self.body_html = value
                self.save()
            return
        except Exception:
            raise

    def update_is_published_from_api_data(self, value):
        try:
            value = bool(value)
            if not self.is_published == value:
                self.is_published = value
                self.save()
            return
        except Exception:
            raise

    def update_published_scope_from_api_data(self, value):
        try:
            if not self.published_scope == value:
                self.published_scope = value
                self.save()
            return
        except Exception:
            raise

    def update_rules_from_api_data(self, values):
        try:
            msgs = []
            for value in values:
                if value['column'] == 'tag' and value['relation'] == 'equals':
                    tag, created = ShopifyTag.objects.get_or_create(
                        name=value['condition']
                    )
                    if created:
                        msgs.append(tag.get_create_success_msg())
                    if tag not in self.tags.all():
                        self.tags.add(tag)
                        self.save()
                        msgs.append(
                            self.get_update_success_msg(
                                message=f'{tag} added'
                            )
                        )

                rule, created = ShopifyCollectionRule.objects.get_or_create(
                    column=value['column'],
                    relation=value['relation'],
                    condition=value['condition']
                )
                if created:
                    msgs.append(rule.get_create_success_msg())
                if rule not in self.rules.all():
                    self.rules.add(rule)
                    self.save()
                    msgs.append(
                        self.get_update_success_msg(
                            message=f'{rule} added'
                        )
                    )

            tag_values = [
                value['condition'] for value in values
                if value['column'] == 'tag' and value['relation'] == 'equals'
            ]
            for tag in self.tags.all():
                if tag.name not in tag_values:
                    self.tags.remove(tag)
                    self.save()
                    msgs.append(
                        self.get_update_success_msg(
                            message=f'{tag} removed'
                        )
                    )

            rule_values = [value for value in values]
            for rule in self.rules.all():
                if {
                    'column': rule.column,
                    'relation': rule.relation,
                    'condition': rule.condition
                } not in rule_values:
                    self.rules.remove(rule)
                    self.save()
                    msgs.append(
                        self.get_update_success_msg(
                            message=f'{rule} removed'
                        )
                    )
            return msgs
        except Exception:
            raise

    def update_disjunctive_from_api_data(self, value):
        try:
            value = bool(value)
            if not self.disjunctive == value:
                self.disjunctive = value
                self.save()
            return
        except Exception:
            raise

    def update_sort_order_from_api_data(self, value):
        try:
            if not self.sort_order == value:
                self.sort_order = value
                self.save()
            return
        except Exception:
            raise

    def update_from_api_data(self, data, *fields):
        field_map = {
            'collection_id': {
                'data': 'id',
                'function': 'update_collection_id_from_api_data'
            },
            'title': {
                'data': 'title',
                'function': 'update_title_from_api_data'
            },
            'handle': {
                'data': 'handle',
                'function': 'update_handle_from_api_data'
            },
            'body_html': {
                'data': 'body_html',
                'function': 'update_body_html_from_api_data'
            },
            # 'image_src': {
            #     'data': '',
            #     'function': ''
            # },
            # 'image_alt': {
            #     'data': '',
            #     'function': ''
            # },
            'is_published': {
                'data': 'published_at',
                'function': 'update_is_published_from_api_data'
            },
            'published_scope': {
                'data': 'published_scope',
                'function': 'update_published_scope_from_api_data'
            },
            'rules': {
                'data': 'rules',
                'function': 'update_rules_from_api_data'
            },
            'disjunctive': {
                'data': 'disjunctive',
                'function': 'update_disjunctive_from_api_data'
            },
            'sort_order': {
                'data': 'sort_order',
                'function': 'update_sort_order_from_api_data'
            }
        }

        if fields:
            for field in fields:
                if field not in field_map.keys():
                    raise Exception('Invalid update field')
        else:
            fields = field_map.keys()

        msgs = []
        prev = self.state
        for field in fields:
            try:
                extra_msgs = getattr(
                    self,
                    field_map[field]['function']
                )(data[field_map[field]['data']])

                if extra_msgs:
                    msgs += extra_msgs
            except Exception as err:
                msgs.append(
                    self.get_instance_error_msg(
                        error=f'{field} update error: {err}')
                )
                continue

        self.refresh_from_db()
        new = self.state
        msgs.append(
            self.get_update_success_msg(
                previous_data=prev,
                new_data=new
            )
        )

        if not msgs:
            msgs.append(self.get_instance_up_to_date_msg())
        return msgs
    # </editor-fold>

    # <editor-fold desc="perform properties ...">
    def perform_calculated_fields_update(self):
        return self.calculator.perform_calculated_fields_update()

    def perform_create_to_api(self):
        msgs = []
        if self.collection_id:
            msgs.append(
                self.get_instance_error_msg(error="Already exists in Shopify")
            )
            return msgs

        try:
            data = shopify_client.create_collection(
                collection_data=self.api_formatted_data
            )
            msgs.append(
                self.get_create_success_msg(message="Created in Shopify")
            )
            msgs += self.update_from_api_data(data)

            for metafield in self.metafields.all():
                if metafield.metafield_id:
                    msgs += metafield.perform_update_to_api()
                else:
                    msgs += metafield.perform_create_to_api()
        except Exception as err:
            msgs.append(self.get_instance_error_msg(str(err)))

        if not msgs:
            msgs.append(self.get_instance_up_to_date_msg())
        return msgs

    def perform_update_to_api(self):
        msgs = []
        if not self.collection_id:
            msgs.append(
                self.get_instance_error_msg(error="Doesn't exists in Shopify")
            )
            return msgs

        try:
            formatted_data = self.api_formatted_data
            shopify_client.update_collection(
                collection_data=formatted_data)
            msgs.append(
                self.get_update_success_msg(message="Updated in Shopify")
            )

            for metafield in self.metafields.all():
                if metafield.metafield_id:
                    msgs += metafield.perform_update_to_api()
                else:
                    msgs += metafield.perform_create_to_api()
        except Exception as err:
            msgs.append(self.get_instance_error_msg(str(err)))

        if not msgs:
            msgs.append(self.get_instance_up_to_date_msg())
        return msgs

    def perform_update_from_api(self):
        msgs = []
        if not self.collection_id:
            msgs.append(
                self.get_instance_error_msg(error="Doesn't exists in Shopify")
            )
            return msgs

        try:
            data = shopify_client.retrieve_collection(
                collection_id=self.collection_id
            )
            msgs += self.update_from_api_data(data)

            for metafield in self.metafields.filter(
                    metafield_id__isnull=False):
                msgs += metafield.perform_update_from_api()
        except Exception as err:
            msgs.append(self.get_instance_error_msg(str(err)))

        if not msgs:
            msgs.append(self.get_instance_up_to_date_msg())
        return msgs
    # </editor-fold>

    objects = ShopifyCollectionManager()

    def delete(self, using=None, keep_parents=False):
        if self.collection_id:
            try:
                shopify_client.delete_collection(
                    collection_id=self.collection_id
                )
            except Exception as err:
                raise

        super().delete(using=using, keep_parents=keep_parents)

    def __str__(self):
        return self.title


class ShopifyCollectionCalculator(Model, MessagesMixin):
    CUSTOM_VALUE = 'custom_value'

    collection = OneToOneField(
        ShopifyCollection,
        related_name='calculator',
        on_delete=CASCADE
    )
    title_option = CharField(
        choices=(
            ('sema_category_chained_title_value', 'SEMA Categories'),
            (CUSTOM_VALUE, 'Custom')
        ),
        default='sema_category_chained_title_value',
        max_length=50
    )
    metafields_display_name_option = CharField(
        choices=(
            ('sema_category_display_name_value', 'SEMA Category'),
            (CUSTOM_VALUE, 'Custom')
        ),
        default='sema_category_display_name_value',
        max_length=50
    )
    metafields_subcollections_option = CharField(
        choices=(
            ('shopify_subcollections_value', 'Shopify Subcollections'),
            (CUSTOM_VALUE, 'Custom')
        ),
        default='shopify_subcollections_value',
        max_length=50
    )
    tags_categories_option = CharField(
        choices=(
            ('sema_category_tags_value', 'SEMA Categories'),
            (CUSTOM_VALUE, 'Custom')
        ),
        default='sema_category_tags_value',
        max_length=50
    )

    # <editor-fold desc="internal properties ...">
    @property
    def category_path(self):
        if self.collection.level == '1':
            return self.collection.root_category_paths.first()
        elif self.collection.level == '2':
            return self.collection.branch_category_paths.filter(
                shopify_root_collection=self.collection.parent_collection
            ).first()
        elif self.collection.level == '3':
            return self.collection.leaf_category_paths.filter(
                shopify_root_collection=self.collection.parent_collection.parent_collection,
                shopify_branch_collection=self.collection.parent_collection,
            ).first()
        else:
            return None

    @property
    def shopify_collection(self):
        return self.collection

    @property
    def sema_category(self):
        if self.collection.level == '1':
            return self.category_path.sema_root_category
        elif self.collection.level == '2':
            return self.category_path.sema_branch_category
        elif self.collection.level == '3':
            return self.category_path.sema_leaf_category
        else:
            return None

    @property
    def sema_parent_category(self):
        if self.collection.level == '1':
            return None
        elif self.collection.level == '2':
            return self.category_path.sema_root_category
        elif self.collection.level == '3':
            return self.category_path.sema_branch_category
        else:
            return None

    @property
    def sema_grandparent_category(self):
        if self.collection.level == '1':
            return None
        elif self.collection.level == '2':
            return None
        elif self.collection.level == '3':
            return self.category_path.sema_root_category
        else:
            return None
    # </editor-fold>

    # <editor-fold desc="value properties ...">
    @property
    def custom_value(self):
        return None

    @property
    def sema_category_display_name_value(self):
        if self.shopify_collection.level == '1':
            return None

        return self.sema_category.name

    @property
    def sema_category_chained_title_value(self):
        if self.shopify_collection.level == '1':
            return f'{self.sema_category.name.strip()}'
        elif self.shopify_collection.level == '2':
            return (
                f'{self.sema_parent_category.name.strip()} '
                f'// {self.sema_category.name.strip()}'
            )
        elif self.shopify_collection.level == '3':
            return (
                f'{self.sema_grandparent_category.name.strip()} '
                f'// {self.sema_parent_category.name.strip()} '
                f'// {self.sema_category.name.strip()}'
            )
        else:
            return None

    @property
    def sema_category_tags_value(self):
        if self.shopify_collection.level == '1':
            tags = [self.sema_category.tag_name]
        elif self.shopify_collection.level == '2':
            tags = [
                self.sema_category.tag_name,
                self.sema_parent_category.tag_name
            ]
        elif self.shopify_collection.level == '3':
            tags = [
                self.sema_category.tag_name,
                self.sema_parent_category.tag_name,
                self.sema_grandparent_category.tag_name,
            ]
        else:
            return None

        tags.sort()
        return tags

    @property
    def shopify_subcollections_value(self):
        if self.shopify_collection.level == '1' or self.shopify_collection.level == '2':
            subcollections = []
            for child_collection in self.shopify_collection.child_collections.all():
                if child_collection.collection_id and child_collection.handle:
                    subcollections.append(
                        {
                            'id': child_collection.collection_id,
                            'handle': child_collection.handle
                        }
                    )
            subcollections = sorted(subcollections, key=lambda k: k['handle'])
            return subcollections
        elif self.shopify_collection.level == '3':
            return None
        else:
            return None
    # </editor-fold>

    # <editor-fold desc="preview properties ...">
    @property
    def sema_category_display_name_preview(self):
        return self.sema_category_display_name_value
    sema_category_display_name_preview.fget.short_description = 'SEMA Category'

    @property
    def sema_category_chained_title_preview(self):
        return self.sema_category_chained_title_value
    sema_category_chained_title_preview.fget.short_description = 'SEMA Categories'

    @property
    def sema_category_tags_preview(self):
        if not self.sema_category_tags_value:
            return None

        return str(self.sema_category_tags_value)
    sema_category_tags_preview.fget.short_description = 'SEMA Categories'

    @property
    def shopify_subcollections_preview(self):
        if not self.shopify_subcollections_value:
            return None
        return get_json_preview(json.dumps(self.shopify_subcollections_value))
    shopify_subcollections_preview.fget.short_description = 'Shopify Subcollections'
    # </editor-fold>

    # <editor-fold desc="result properties ...">
    @property
    def title_result(self):
        return getattr(self, self.title_option)
    title_result.fget.short_description = ''

    @property
    def metafields_display_name_result(self):
        value = getattr(self, self.metafields_display_name_option)
        if not value:
            return None

        return {
            'namespace': 'additional',
            'key': 'display_name',
            'owner_resource':
                ShopifyMetafield.COLLECTION_OWNER_RESOURCE,
            'value': value,
            'value_type': ShopifyMetafield.STRING_VALUE_TYPE
        }
    metafields_display_name_result.fget.short_description = ''

    @property
    def metafields_subcollections_result(self):
        subcollections = getattr(self, self.metafields_subcollections_option)
        if not subcollections:
            return None

        return {
            'namespace': 'additional',
            'key': 'subcollections',
            'owner_resource':
                ShopifyMetafield.COLLECTION_OWNER_RESOURCE,
            'value': json.dumps(subcollections),
            'value_type': ShopifyMetafield.JSON_VALUE_TYPE
        }
    metafields_subcollections_result.fget.short_description = ''

    @property
    def metafields_result(self):
        metafields = []
        if self.metafields_display_name_result:
            metafields.append(self.metafields_display_name_result)
        if self.metafields_subcollections_result:
            metafields.append(self.metafields_subcollections_result)
        metafields = sorted(metafields, key=lambda k: k['value'])
        return metafields
    metafields_result.fget.short_description = ''

    @property
    def tags_categories_result(self):
        tag_names = getattr(self, self.tags_categories_option)
        if not tag_names:
            return None

        tags = [
            {'name': tag_name}
            for tag_name in tag_names
        ]
        tags = sorted(tags, key=lambda k: k['name'])
        return tags
    tags_categories_result.fget.short_description = ''

    @property
    def tags_result(self):
        tags = []
        if self.tags_categories_result:
            tags += self.tags_categories_result
        tags = sorted(tags, key=lambda k: k['name'])
        return tags
    tags_result.fget.short_description = ''
    # </editor-fold>

    # <editor-fold desc="match properties ...">
    def title_match(self):
        if not self.title_result:
            return None

        return bool(self.shopify_collection.title == self.title_result)
    title_match.boolean = True
    title_match.short_description = 'Title Match'

    def metafields_match(self):
        if not self.metafields_result:
            return None

        metafields = [
            {
                'namespace': metafield.namespace,
                'key': metafield.key,
                'owner_resource': metafield.owner_resource,
                'value': metafield.value,
                'value_type': metafield.value_type
            }
            for metafield in self.shopify_collection.metafields.all()
        ]
        metafields = sorted(metafields, key=lambda k: k['value'])
        return bool(metafields == self.metafields_result)
    metafields_match.boolean = True
    metafields_match.short_description = 'Metafields Match'

    def tags_match(self):
        if not self.tags_result:
            return None

        tags = [
            {'name': tag.name}
            for tag in self.shopify_collection.tags.all()
        ]
        tags = sorted(tags, key=lambda k: k['name'])
        return bool(tags == self.tags_result)
    tags_match.boolean = True
    tags_match.short_description = 'Tags Match'

    def full_match(self):
        return bool(
            self.title_match() is not False
            and self.metafields_match() is not False
            and self.tags_match() is not False
        )
    full_match.boolean = True
    full_match.short_description = 'Calculator Match'
    # </editor-fold>

    # <editor-fold desc="difference properties ...">
    @property
    def title_difference(self):
        if self.title_match() is not False:
            return ''

        return f'{self.shopify_collection.title} <- {self.title_result}'
    title_difference.fget.short_description = ''

    @property
    def metafields_difference(self):
        if self.metafields_match() is not False:
            return ''

        return (
            f'{self.shopify_collection.metafields.count()} '
            f'<- {len(self.metafields_result)}'
        )
    metafields_difference.fget.short_description = ''

    @property
    def tags_difference(self):
        if self.tags_match() is not False:
            return ''

        return (
            f'{self.shopify_collection.tags.count()} '
            f'<- {len(self.tags_result)}'
        )
    tags_difference.fget.short_description = ''
    # </editor-fold>

    # <editor-fold desc="perform properties ...">
    def perform_calculated_fields_update(self):
        try:
            if self.title_match() is False:
                self.shopify_collection.title = self.title_result
                self.shopify_collection.save()

            if self.metafields_match() is False:
                for metafield_data in self.metafields_result:
                    defaults = {
                        'value': metafield_data.pop('value'),
                        'value_type': metafield_data.pop('value_type')
                    }
                    ShopifyMetafield.objects.update_or_create(
                        object_id=self.shopify_collection.pk,
                        content_type=ContentType.objects.get_for_model(self.shopify_collection),
                        **metafield_data,
                        defaults=defaults
                    )

            if self.tags_match() is False:
                for tag_data in self.tags_result:
                    tag, _ = ShopifyTag.objects.get_or_create(**tag_data)
                    self.shopify_collection.tags.add(tag)
                    self.shopify_collection.save()

            return self.shopify_collection.get_update_success_msg()
        except Exception as err:
            return self.get_instance_error_msg(str(err))
    # </editor-fold>
    
    objects = ShopifyCollectionCalculatorManager()

    def __str__(self):
        return str(self.collection)


class ShopifyProduct(Model, MessagesMixin):
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

    product_id = BigIntegerField(
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
    metafields = GenericRelation(
        ShopifyMetafield,
        related_query_name='product'
    )

    # <editor-fold desc="count properties ...">
    @property
    def variant_count(self):
        return self.variants.count()
    variant_count.fget.short_description = 'variant count'

    @property
    def option_count(self):
        return self.options.count()
    option_count.fget.short_description = 'option count'

    @property
    def image_count(self):
        return self.images.count()
    image_count.fget.short_description = 'image count'

    @property
    def metafield_count(self):
        return self.metafields.count()
    metafield_count.fget.short_description = 'metafield count'

    @property
    def tag_count(self):
        return self.tags.count()
    tag_count.fget.short_description = 'tag count'
    # </editor-fold>

    # <editor-fold desc="error properties ...">
    @property
    def warnings(self):
        """
        Returns a concatenation of warnings.

        :return: warnings
        :rtype: str

        """

        msgs = []
        return ', '.join(msgs)

    @property
    def errors(self):
        """
        Returns a concatenation of errors.

        :return: errors
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
        if not self.tags.all().count() >= 4:
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
    # </editor-fold>

    # <editor-fold desc="format properties ...">
    @property
    def api_formatted_data(self):
        data = {
            'id': self.product_id,
            'title': self.title,
            'body_html': self.api_formatted_body_html,
            'vendor': self.api_formatted_vendor,
            'product_type': self.product_type,
            'published': self.is_published,
            'published_scope': self.published_scope,
            'tags': self.api_formatted_tags,
            'variants': self.api_formatted_variants,
            'options': self.api_formatted_options
        }
        return dict((k, v) for k, v in data.items() if v)

    @property
    def api_formatted_body_html(self):
        if not self.body_html:
            return self.body_html
        return f"<strong>{self.body_html}</strong>"

    @property
    def api_formatted_vendor(self):
        return self.vendor.name

    @property
    def api_formatted_tags(self):
        return ', '.join(self.tags.values_list('name', flat=True))

    @property
    def api_formatted_variants(self):
        variants_data = []
        for variant in self.variants.all():
            variants_data.append(variant.api_formatted_data)
        return variants_data

    @property
    def api_formatted_options(self):
        options_data = []
        for option in self.options.all():
            options_data.append(option.api_formatted_data)
        return options_data
    # </editor-fold>

    # <editor-fold desc="update properties ...">
    @property
    def state(self):
        return {
            'product_id': str(self.product_id),
            'title': self.title,
            'body_html': self.body_html,
            'vendor': str(self.vendor),
            'product_type': self.product_type,
            'published': str(self.is_published),
            'published_scope': self.published_scope,
            'tags': str(self.tags.count()),
            'seo_title': self.seo_title,
            'seo_description': self.seo_description
        }

    def update_product_id_from_api_data(self, value):
        try:
            if not self.product_id == value:
                self.product_id = value
                self.save()
            return
        except Exception:
            raise

    def update_title_from_api_data(self, value):
        try:
            if not self.title == value:
                self.title = value
                self.save()
            return
        except Exception:
            raise

    def update_body_html_from_api_data(self, value):
        try:
            value = value.replace(
                '<strong>', ''
            ).replace(
                '</strong>', ''
            ).replace(
                '&amp;', '&'
            )
            if not self.body_html == value:
                self.body_html = value
                self.save()
            return
        except Exception:
            raise

    def update_vendor_from_api_data(self, value):
        try:
            msgs = []
            if not self.vendor or not self.vendor.name == value:
                vendor, created = ShopifyVendor.objects.get_or_create(
                    name=value
                )
                self.vendor = vendor
                self.save()
                if created:
                    msgs.append(vendor.get_create_success_msg())
            return msgs
        except Exception:
            raise

    def update_product_type_from_api_data(self, value):
        try:
            if not self.product_type == value:
                self.product_type = value
                self.save()
            return
        except Exception:
            raise

    def update_is_published_from_api_data(self, value):
        try:
            value = bool(value)
            if not self.is_published == value:
                self.is_published = value
                self.save()
            return
        except Exception:
            raise

    def update_published_scope_from_api_data(self, value):
        try:
            if not self.published_scope == value:
                self.published_scope = value
                self.save()
            return
        except Exception:
            raise

    def update_tags_from_api_data(self, value):
        try:
            msgs = []
            _msgs = ''
            tag_values = value.split(', ')
            tags = list(self.tags.values_list('name', flat=True))
            for tag_value in tag_values:
                if tag_value not in tags:
                    tag, created = ShopifyTag.objects.get_or_create(
                        name=tag_value
                    )
                    self.tags.add(tag)
                    self.save()
                    if created:
                        msgs.append(tag.get_create_success_msg())
                    _msgs += f'tag {tag} added, '
            for tag in tags:
                if tag not in tag_values:
                    tag = ShopifyTag.objects.get(name=tag)
                    self.tags.remove(tag)
                    self.save()
                    _msgs += f'tag {tag} removed, '

            if _msgs:
                msgs.append(self.get_update_success_msg(message=_msgs))
            return msgs
        except Exception:
            raise

    def update_from_api_data(self, data, *fields):
        field_map = {
            'product_id': {
                'data': 'id',
                'function': 'update_product_id_from_api_data'
            },
            'title': {
                'data': 'title',
                'function': 'update_title_from_api_data'
            },
            'body_html': {
                'data': 'body_html',
                'function': 'update_body_html_from_api_data'
            },
            'vendor': {
                'data': 'vendor',
                'function': 'update_vendor_from_api_data'
            },
            'product_type': {
                'data': 'product_type',
                'function': 'update_product_type_from_api_data'
            },
            'is_published': {
                'data': 'published_at',
                'function': 'update_is_published_from_api_data'
            },
            'published_scope': {
                'data': 'published_scope',
                'function': 'update_published_scope_from_api_data'
            },
            'tags': {
                'data': 'tags',
                'function': 'update_tags_from_api_data'
            }
            # 'seo_title': {
            #     'data': '',
            #     'function': ''
            # },
            # 'seo_description': {
            #     'data': '',
            #     'function': ''
            # }
        }

        if fields:
            for field in fields:
                if field not in field_map.keys():
                    raise Exception('Invalid update field')
        else:
            fields = field_map.keys()

        msgs = []
        prev = self.state
        for field in fields:
            try:
                extra_msgs = getattr(
                    self,
                    field_map[field]['function']
                )(data[field_map[field]['data']])

                if extra_msgs:
                    msgs += extra_msgs
            except Exception as err:
                msgs.append(
                    self.get_instance_error_msg(
                        error=f'{field} update error: {err}')
                )
                continue

        self.refresh_from_db()
        new = self.state
        msgs.append(
            self.get_update_success_msg(
                previous_data=prev,
                new_data=new
            )
        )

        for variant_data in data['variants']:
            try:
                variant = self.variants.get(
                    Q(variant_id=variant_data['id'])
                    | Q(title=variant_data['title'])
                )
                msgs += variant.update_from_api_data(variant_data)
            except ShopifyVariant.DoesNotExist:
                msgs.append(
                    ShopifyVariant.objects.create_from_api_data(
                        product=self,
                        data=variant_data
                    )
                )
            except Exception as err:
                msgs.append(self.get_instance_error_msg(str(err)))

        for option_data in data['options']:
            try:
                option = self.options.get(
                    Q(option_id=option_data['id'])
                    | Q(name=option_data['name'])
                )
                msgs += option.update_from_api_data(option_data)
            except ShopifyOption.DoesNotExist:
                msgs.append(
                    ShopifyOption.objects.create_from_api_data(
                        product=self,
                        data=option_data
                    )
                )
            except Exception as err:
                msgs.append(self.get_instance_error_msg(str(err)))

        if not msgs:
            msgs.append(self.get_instance_up_to_date_msg())
        return msgs
    # </editor-fold>

    # <editor-fold desc="perform properties ...">
    def perform_calculated_fields_update(self):
        return self.calculator.perform_calculated_fields_update()

    def perform_create_to_api(self):
        msgs = []
        if self.product_id:
            msgs.append(
                self.get_instance_error_msg(error="Already exists in Shopify")
            )
            return msgs

        try:
            data = shopify_client.create_product(
                product_data=self.api_formatted_data
            )
            msgs.append(
                self.get_create_success_msg(message="Created in Shopify")
            )
            msgs += self.update_from_api_data(data)

            for metafield in self.metafields.all():
                if metafield.metafield_id:
                    msgs += metafield.perform_update_to_api()
                else:
                    msgs += metafield.perform_create_to_api()

            for image in self.images.all():
                if image.image_id:
                    msgs += image.perform_update_to_api()
                else:
                    msgs += image.perform_create_to_api()
        except Exception as err:
            msgs.append(self.get_instance_error_msg(str(err)))

        if not msgs:
            msgs.append(self.get_instance_up_to_date_msg())
        return msgs

    def perform_update_to_api(self):
        msgs = []
        if not self.product_id:
            msgs.append(
                self.get_instance_error_msg(error="Doesn't exists in Shopify")
            )
            return msgs

        try:
            formatted_data = self.api_formatted_data
            formatted_data.pop('images', [])
            shopify_client.update_product(product_data=formatted_data)
            msgs.append(
                self.get_update_success_msg(message="Updated in Shopify")
            )

            for metafield in self.metafields.all():
                if metafield.metafield_id:
                    msgs += metafield.perform_update_to_api()
                else:
                    msgs += metafield.perform_create_to_api()

            for image in self.images.all():
                if image.image_id:
                    msgs += image.perform_update_to_api()
                else:
                    msgs += image.perform_create_to_api()
        except Exception as err:
            msgs.append(self.get_instance_error_msg(str(err)))

        if not msgs:
            msgs.append(self.get_instance_up_to_date_msg())
        return msgs

    def perform_update_from_api(self):
        msgs = []
        if not self.product_id:
            msgs.append(
                self.get_instance_error_msg(error="Doesn't exists in Shopify")
            )
            return msgs

        try:
            data = shopify_client.retrieve_product(product_id=self.product_id)
            msgs += self.update_from_api_data(data)

            for metafield in self.metafields.filter(
                    metafield_id__isnull=False):
                msgs += metafield.perform_update_from_api()

            for image in self.images.filter(image_id__isnull=False):
                msgs += image.perform_update_from_api()
        except Exception as err:
            msgs.append(self.get_instance_error_msg(str(err)))

        if not msgs:
            msgs.append(self.get_instance_up_to_date_msg())
        return msgs
    # </editor-fold>

    objects = ShopifyProductManager()

    def delete(self, using=None, keep_parents=False):
        if self.product_id:
            try:
                shopify_client.delete_product(
                    product_id=self.product_id
                )
            except Exception as err:
                raise

        super().delete(using=using, keep_parents=keep_parents)

    def __str__(self):
        s = []
        if self.vendor:
            s.append(str(self.vendor))
        if self.title:
            s.append(self.title)
        if not s:
            s.append(str(self.id))
        return ' :: '.join(s)


class ShopifyImage(Model, MessagesMixin):
    image_id = BigIntegerField(
        blank=True,
        help_text='Populated by Shopify',
        null=True,
        unique=True
    )
    product = ForeignKey(
        ShopifyProduct,
        related_name='images',
        on_delete=CASCADE
    )
    link = URLField(
        max_length=250
    )
    src = URLField(
        blank=True,
        help_text='Populated by Shopify',
        max_length=250
    )

    # <editor-fold desc="format properties ...">
    @property
    def api_formatted_data(self):
        data = {
            'id': self.image_id,
            'src': self.src if self.src else self.link
        }
        return dict((k, v) for k, v in data.items() if v)
    # </editor-fold>

    # <editor-fold desc="update properties ...">
    @property
    def state(self):
        return {
            'image_id': str(self.image_id)
        }

    def update_image_id_from_api_data(self, value):
        try:
            if not self.image_id == value:
                self.image_id = value
                self.save()
            return
        except Exception:
            raise

    def update_src_from_api_data(self, value):
        try:
            if not self.src == value:
                self.src = value
                self.save()
            return
        except Exception:
            raise

    def update_from_api_data(self, data, *fields):
        field_map = {
            'image_id': {
                'data': 'id',
                'function': 'update_image_id_from_api_data'
            },
            'src': {
                'data': 'src',
                'function': 'update_src_from_api_data'
            }
        }

        if fields:
            for field in fields:
                if field not in field_map.keys():
                    raise Exception('Invalid update field')
        else:
            fields = field_map.keys()

        msgs = []
        prev = self.state
        for field in fields:
            try:
                extra_msgs = getattr(
                    self,
                    field_map[field]['function']
                )(data[field_map[field]['data']])

                if extra_msgs:
                    msgs += extra_msgs
            except Exception as err:
                msgs.append(
                    self.get_instance_error_msg(
                        error=f'{field} update error: {err}')
                )
                continue

        self.refresh_from_db()
        new = self.state
        msgs.append(
            self.get_update_success_msg(
                previous_data=prev,
                new_data=new
            )
        )

        if not msgs:
            msgs.append(self.get_instance_up_to_date_msg())
        return msgs
    # </editor-fold>

    # <editor-fold desc="perform properties ...">
    def perform_create_to_api(self):
        msgs = []
        if self.image_id:
            msgs.append(
                self.get_instance_error_msg(
                    error="Already exists in Shopify")
            )
            return msgs

        try:
            data = shopify_client.create_product_image(
                product_id=self.product.product_id,
                image_data=self.api_formatted_data
            )

            msgs.append(
                self.get_create_success_msg(message="Created in Shopify")
            )
            msgs += self.update_from_api_data(data)
        except Exception as err:
            msgs.append(self.get_instance_error_msg(str(err)))

        if not msgs:
            msgs.append(self.get_instance_up_to_date_msg())
        return msgs

    def perform_update_to_api(self):
        msgs = []
        if not self.image_id:
            msgs.append(
                self.get_instance_error_msg(
                    error="Doesn't exists in Shopify")
            )
            return msgs

        try:
            data = shopify_client.update_product_image(
                product_id=self.product.product_id,
                image_data=self.api_formatted_data
            )

            msgs.append(
                self.get_update_success_msg(message="Updated in Shopify")
            )
        except Exception as err:
            msgs.append(self.get_instance_error_msg(str(err)))

        if not msgs:
            msgs.append(self.get_instance_up_to_date_msg())
        return msgs

    def perform_update_from_api(self):
        msgs = []
        if not self.image_id:
            msgs.append(
                self.get_instance_error_msg(
                    error="Doesn't exists in Shopify")
            )
            return msgs

        try:
            data = shopify_client.retrieve_product_image(
                product_id=self.product.product_id,
                image_id=self.image_id
            )

            msgs += self.update_from_api_data(data)

        except Exception as err:
            msgs.append(self.get_instance_error_msg(str(err)))

        if not msgs:
            msgs.append(self.get_instance_up_to_date_msg())
        return msgs
    # </editor-fold>

    objects = ShopifyImageManager()

    def delete(self, using=None, keep_parents=False):
        if self.image_id:
            try:
                shopify_client.delete_product_image(
                    product_id=self.product.product_id,
                    image_id=self.image_id
                )
            except Exception as err:
                raise

        super().delete(using=using, keep_parents=keep_parents)

    def __str__(self):
        return str(self.product)


class ShopifyOption(Model, MessagesMixin):
    product = ForeignKey(
        ShopifyProduct,
        related_name='options',
        on_delete=CASCADE
    )
    option_id = BigIntegerField(
        blank=True,
        help_text='Populated by Shopify',
        null=True,
        unique=True
    )
    name = CharField(
        default='Title',
        max_length=100
    )
    values = CharField(
        default="['Default Title']",
        max_length=255
    )

    # <editor-fold desc="format properties ...">
    @property
    def api_formatted_data(self):
        data = {
            'id': self.option_id,
            'name': self.name,
            'values': self.values.split(', ')
        }
        return dict((k, v) for k, v in data.items() if v)
    # </editor-fold>

    # <editor-fold desc="update properties ...">
    @property
    def state(self):
        return {
            'option_id': str(self.option_id),
            'name': self.name,
            'values': self.values
        }

    def update_option_id_from_api_data(self, value):
        try:
            if not self.option_id == value:
                self.option_id = value
                self.save()
            return
        except Exception:
            raise

    def update_name_from_api_data(self, value):
        try:
            if not self.name == value:
                self.name = value
                self.save()
            return
        except Exception:
            raise

    def update_values_from_api_data(self, value):
        try:
            value = str(value)
            if not self.values == value:
                self.values = value
                self.save()
            return
        except Exception:
            raise

    def update_from_api_data(self, data, *fields):
        field_map = {
            'option_id': {
                'data': 'id',
                'function': 'update_option_id_from_api_data'
            },
            'name': {
                'data': 'name',
                'function': 'update_name_from_api_data'
            },
            'values': {
                'data': 'values',
                'function': 'update_values_from_api_data'
            }
        }

        if fields:
            for field in fields:
                if field not in field_map.keys():
                    raise Exception('Invalid update field')
        else:
            fields = field_map.keys()

        msgs = []
        prev = self.state
        for field in fields:
            try:
                extra_msgs = getattr(
                    self,
                    field_map[field]['function']
                )(data[field_map[field]['data']])

                if extra_msgs:
                    msgs += extra_msgs
            except Exception as err:
                msgs.append(
                    self.get_instance_error_msg(
                        error=f'{field} update error: {err}')
                )
                continue

        self.refresh_from_db()
        new = self.state
        msgs.append(
            self.get_update_success_msg(
                previous_data=prev,
                new_data=new
            )
        )

        if not msgs:
            msgs.append(self.get_instance_up_to_date_msg())
        return msgs
    # </editor-fold>

    objects = ShopifyOptionManager()

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
    variant_id = BigIntegerField(
        blank=True,
        help_text='Populated by Shopify',
        null=True,
        unique=True
    )
    title = CharField(
        default='Default Title',
        max_length=30
    )
    grams = IntegerField(
        blank=True,
        null=True
    )
    weight = DecimalField(
        blank=True,
        decimal_places=2,
        max_digits=10,
        null=True
    )
    weight_unit = CharField(
        blank=True,
        choices=WEIGHT_UNIT_CHOICES,
        max_length=3
    )
    inventory_management = CharField(
        blank=True,
        choices=INVENTORY_MANAGEMENT_CHOICES,
        max_length=100
    )
    inventory_policy = CharField(
        blank=True,
        choices=INVENTORY_POLICY_CHOICES,
        max_length=10
    )
    fulfillment_service = CharField(
        blank=True,
        choices=FULFILLMENT_SERVICE_CHOICES,
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
        max_length=50,
        verbose_name='SKU'
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

    # <editor-fold desc="format properties ...">
    @property
    def api_formatted_data(self):
        data = {
            'id': self.variant_id,
            'title': self.title,
            'grams': self.grams,
            'weight': self.weight,
            'weight_unit': self.weight_unit,
            # 'inventory_management': self.inventory_management,
            # 'inventory_policy': self.inventory_policy,
            # 'fulfillment_service': self.fulfillment_service,
            'price': self.price,
            'compare_at_price': self.compare_at_price,
            'cost': self.cost,
            'sku': self.sku,
            'barcode': self.barcode,
            'tax_code': self.tax_code,
            'taxable': self.is_taxable
        }
        return dict((k, v) for k, v in data.items() if v)
    # </editor-fold>

    # <editor-fold desc="update properties ...">
    @property
    def state(self):
        return {
            'variant_id': str(self.variant_id),
            'title': self.title,
            'grams': str(self.grams),
            'weight': str(self.weight),
            'weight_unit': self.weight_unit,
            'inventory_management': self.inventory_management,
            'inventory_policy': self.inventory_policy,
            'fulfillment_service': self.fulfillment_service,
            'price': str(self.price),
            'compare_at_price': str(self.compare_at_price),
            'cost': str(self.cost),
            'sku': self.sku,
            'barcode': self.barcode,
            'taxable': str(self.is_taxable),
            'tax_code': self.tax_code
        }

    def update_variant_id_from_api_data(self, value):
        try:
            if not self.variant_id == value:
                self.variant_id = value
                self.save()
            return
        except Exception:
            raise

    def update_title_from_api_data(self, value):
        try:
            if not self.title == value:
                self.title = value
                self.save()
            return
        except Exception:
            raise

    def update_grams_from_api_data(self, value):
        try:
            if not self.grams == value:
                self.grams = value
                self.save()
            return
        except Exception:
            raise

    def update_weight_from_api_data(self, value):
        try:
            if not self.weight == value:
                self.weight = value
                self.save()
            return
        except Exception:
            raise

    def update_weight_unit_from_api_data(self, value):
        try:
            if not self.weight_unit == value:
                self.weight_unit = value
                self.save()
            return
        except Exception:
            raise

    def update_inventory_management_from_api_data(self, value):
        try:
            value = value or ''
            if not self.inventory_management == value:
                self.inventory_management = value
                self.save()
            return
        except Exception:
            raise

    def update_inventory_policy_from_api_data(self, value):
        try:
            if not self.inventory_policy == value:
                self.inventory_policy = value
                self.save()
            return
        except Exception:
            raise

    def update_fulfillment_service_from_api_data(self, value):
        try:
            if not self.fulfillment_service == value:
                self.fulfillment_service = value
                self.save()
            return
        except Exception:
            raise

    def update_price_from_api_data(self, value):
        try:
            if not self.price == value:
                self.price = value
                self.save()
            return
        except Exception:
            raise

    def update_compare_at_price_from_api_data(self, value):
        try:
            if not self.compare_at_price == value:
                self.compare_at_price = value
                self.save()
            return
        except Exception:
            raise

    def update_sku_from_api_data(self, value):
        try:
            if not self.sku == value:
                self.sku = value
                self.save()
            return
        except Exception:
            raise

    def update_barcode_from_api_data(self, value):
        try:
            if not self.barcode == value:
                self.barcode = value
                self.save()
            return
        except Exception:
            raise

    def update_is_taxable_from_api_data(self, value):
        try:
            if not self.is_taxable == value:
                self.is_taxable = value
                self.save()
            return
        except Exception:
            raise

    def update_from_api_data(self, data, *fields):
        field_map = {
            'variant_id': {
                'data': 'id',
                'function': 'update_variant_id_from_api_data'
            },
            'title': {
                'data': 'title',
                'function': 'update_title_from_api_data'
            },
            'grams': {
                'data': 'grams',
                'function': 'update_grams_from_api_data'
            },
            'weight': {
                'data': 'weight',
                'function': 'update_weight_from_api_data'
            },
            'weight_unit': {
                'data': 'weight_unit',
                'function': 'update_weight_unit_from_api_data'
            },
            'inventory_management': {
                'data': 'inventory_management',
                'function': 'update_inventory_management_from_api_data'
            },
            'inventory_policy': {
                'data': 'inventory_policy',
                'function': 'update_inventory_policy_from_api_data'
            },
            'fulfillment_service': {
                'data': 'fulfillment_service',
                'function': 'update_fulfillment_service_from_api_data'
            },
            'price': {
                'data': 'price',
                'function': 'update_price_from_api_data'
            },
            'compare_at_price': {
                'data': 'compare_at_price',
                'function': 'update_compare_at_price_from_api_data'
            },
            # 'cost': {
            #     'data': '',
            #     'function': ''
            # },
            'sku': {
                'data': 'sku',
                'function': 'update_sku_from_api_data'
            },
            'barcode': {
                'data': 'barcode',
                'function': 'update_barcode_from_api_data'
            },
            'is_taxable': {
                'data': 'taxable',
                'function': 'update_is_taxable_from_api_data'
            }
            # 'tax_code': {
            #     'data': '',
            #     'function': ''
            # }
        }

        if fields:
            for field in fields:
                if field not in field_map.keys():
                    raise Exception('Invalid update field')
        else:
            fields = field_map.keys()

        msgs = []
        prev = self.state
        for field in fields:
            try:
                extra_msgs = getattr(
                    self,
                    field_map[field]['function']
                )(data[field_map[field]['data']])

                if extra_msgs:
                    msgs += extra_msgs
            except Exception as err:
                msgs.append(
                    self.get_instance_error_msg(
                        error=f'{field} update error: {err}')
                )
                continue

        self.refresh_from_db()
        new = self.state
        msgs.append(
            self.get_update_success_msg(
                previous_data=prev,
                new_data=new
            )
        )

        if not msgs:
            msgs.append(self.get_instance_up_to_date_msg())
        return msgs
    # </editor-fold>

    objects = ShopifyVariantManager()

    def __str__(self):
        s = str(self.product)
        if self.title:
            s += f' :: {self.title}'
        return s


class ShopifyProductCalculator(Model, MessagesMixin):
    product = OneToOneField(
        ShopifyProduct,
        related_name='calculator',
        on_delete=CASCADE
    )
    title_choice = CharField(
        choices=(
            ('sema_description_def_value', 'SEMA PIES Description'),
            ('sema_description_des_value', 'SEMA DES Description'),
            ('sema_description_inv_value', 'SEMA INV Description'),
            ('sema_description_ext_value', 'SEMA EXT Description'),
            ('sema_description_tle_value', 'SEMA TLE Description'),
            ('sema_description_sho_value', 'SEMA SHO Description'),
            ('sema_description_mkt_value', 'SEMA MKT Description'),
            ('sema_description_key_value', 'SEMA KEY Description'),
            ('sema_description_asc_value', 'SEMA ASC Description'),
            ('sema_description_asm_value', 'SEMA ASM Description'),
            ('sema_description_fab_value', 'SEMA FAB Description'),
            ('sema_description_lab_value', 'SEMA LAB Description'),
            ('sema_description_shp_value', 'SEMA SHP Description'),
            ('sema_description_oth_value', 'SEMA OTH Description'),
            ('premier_description_value', 'Premier Description'),
            ('custom_title_value', 'Custom Title')
        ),
        default='sema_description_sho_value',
        max_length=50
    )
    title_custom_value = CharField(
        blank=True,
        max_length=100
    )
    body_html_choice = CharField(
        choices=(
            ('sema_description_def_value', 'SEMA DEF Description'),
            ('sema_description_des_value', 'SEMA DES Description'),
            ('sema_description_inv_value', 'SEMA INV Description'),
            ('sema_description_ext_value', 'SEMA EXT Description'),
            ('sema_description_tle_value', 'SEMA TLE Description'),
            ('sema_description_sho_value', 'SEMA SHO Description'),
            ('sema_description_mkt_value', 'SEMA MKT Description'),
            ('sema_description_key_value', 'SEMA KEY Description'),
            ('sema_description_asc_value', 'SEMA ASC Description'),
            ('sema_description_asm_value', 'SEMA ASM Description'),
            ('sema_description_fab_value', 'SEMA FAB Description'),
            ('sema_description_lab_value', 'SEMA LAB Description'),
            ('sema_description_shp_value', 'SEMA SHP Description'),
            ('sema_description_oth_value', 'SEMA OTH Description'),
            ('premier_description_value', 'Premier Description'),
            ('custom_body_html_value', 'Custom Body HTML')
        ),
        default='sema_description_ext_value',
        max_length=50
    )
    body_html_custom_value = TextField(
        blank=True
    )
    variant_weight_choice = CharField(
        choices=(
            ('premier_weight_value', 'Premier Weight'),
            ('custom_variant_weight_value', 'Custom Weight')
        ),
        default='premier_weight_value',
        max_length=50
    )
    variant_weight_custom_value = DecimalField(
        blank=True,
        decimal_places=2,
        max_digits=10,
        null=True
    )
    variant_weight_unit_choice = CharField(
        choices=(
            (ShopifyVariant.G_UNIT, ShopifyVariant.G_UNIT),
            (ShopifyVariant.KG_UNIT, ShopifyVariant.KG_UNIT),
            (ShopifyVariant.OZ_UNIT, ShopifyVariant.OZ_UNIT),
            (ShopifyVariant.LB_UNIT, ShopifyVariant.LB_UNIT)
        ),
        default=ShopifyVariant.LB_UNIT,
        max_length=5
    )
    variant_cost_choice = CharField(
        choices=(
            ('premier_cost_cad_value', 'Premier Cost CAD'),
            ('premier_cost_usd_value', 'Premier Cost USD'),
            ('custom_variant_cost_value', 'Custom Cost')
        ),
        default='premier_cost_cad_value',
        max_length=50
    )
    variant_cost_custom_value = DecimalField(
        blank=True,
        decimal_places=2,
        max_digits=10,
        null=True
    )
    variant_price_base_choice = CharField(
        choices=(
            ('premier_cost_cad_value', 'Premier Cost CAD'),
            ('premier_cost_usd_value', 'Premier Cost USD'),
            ('custom_variant_price_base_value', 'Custom Price Base')
        ),
        default='premier_cost_cad_value',
        max_length=50
    )
    variant_price_base_custom_value = DecimalField(
        blank=True,
        decimal_places=2,
        max_digits=10,
        null=True
    )
    variant_price_markup_choice = CharField(
        choices=(
            ('0.00', '0%'),
            ('0.05', '5%'),
            ('0.10', '10%'),
            ('0.15', '15%'),
            ('0.20', '20%'),
            ('0.25', '25%'),
            ('0.30', '30%'),
            ('0.35', '35%'),
            ('0.40', '40%')
        ),
        default='0.20',
        max_length=5
    )
    variant_sku_choice = CharField(
        choices=(
            ('premier_premier_part_number_value', 'Premier Part Number'),
            ('custom_variant_sku_value', 'Custom SKU')
        ),
        default='premier_premier_part_number_value',
        max_length=50
    )
    variant_sku_custom_value = CharField(
        blank=True,
        max_length=50
    )
    variant_barcode_choice = CharField(
        choices=(
            ('premier_upc_value', 'Premier UPC'),
            ('custom_variant_barcode_value', 'Custom Barcode')
        ),
        default='premier_upc_value',
        max_length=50
    )
    variant_barcode_custom_value = CharField(
        blank=True,
        max_length=50
    )
    metafield_value_packaging_choice = CharField(
        choices=(
            ('sema_html_value', 'SEMA HTML'),
            ('custom_packaging_metafield_value_value', 'Custom Packaging Metafield Value')
        ),
        default='sema_html_value',
        max_length=50
    )
    metafield_value_packaging_custom_value = TextField(
        blank=True,
        help_text='format: <html>...</html>'
    )
    metafield_value_fitments_choice = CharField(
        choices=(
            ('sema_vehicles_value', 'SEMA Vehicles'),
            ('custom_fitments_metafield_value_value', 'Custom Fitments Metafield Value')
        ),
        default='sema_vehicles_value',
        max_length=50
    )
    metafield_value_fitments_custom_value = TextField(
        blank=True,
        help_text='format: [{"year", "make", "model", "submodel"}]',
        verbose_name='Custom Fitments Metafields'
    )
    metafields_choice = CharField(
        choices=(
            ('metafields_dict_all_value', 'All Metafields'),
            ('metafields_dict_packaging_value', 'Packaging Metafields'),
            ('metafields_dict_fitments_value', 'Fitments Metafields'),
            ('metafields_dict_custom_value', 'Custom Metafields')
        ),
        default='metafields_dict_all_value',
        max_length=50
    )
    metafields_custom_value = TextField(
        blank=True,
        help_text=(
            'format: '
            '[{"namespace", "key": "owner_resource", "value", "value_type"}]'),
    )
    tag_names_vendor_choice = CharField(
        choices=(
            ('sema_brand_tag_names_value', 'SEMA Brand Tag Names'),
            ('custom_vendor_tag_names_value', 'Custom Vendor Tag Names')
        ),
        default='sema_brand_tag_names_value',
        max_length=50
    )
    tag_names_vendor_custom_value = TextField(
        blank=True,
        help_text='format: [""]'
    )
    tag_names_collection_choice = CharField(
        choices=(
            ('sema_category_tag_names_value', 'SEMA Category Tag Names'),
            ('custom_collection_tag_names_value', 'Custom Collection Tag Names')
        ),
        default='sema_category_tag_names_value',
        max_length=50
    )
    tag_names_collection_custom_value = TextField(
        blank=True,
        help_text='format: [""]'
    )
    tags_choice = CharField(
        choices=(
            ('tags_dict_all_value', 'All Tags'),
            ('tags_dict_vendor_value', 'Vendor Tags'),
            ('tags_dict_collection_value', 'Collection Tags'),
            ('tags_dict_custom_value', 'Custom Tags')
        ),
        default='tags_dict_all_value',
        max_length=50
    )
    tags_custom_value = TextField(
        blank=True,
        help_text='format: [{"name"}]'
    )
    image_urls_sema_choice = CharField(
        choices=(
            ('sema_filtered_image_urls_value', 'SEMA Filtered Image URLs'),
            ('custom_sema_image_urls_value', 'Custom SEMA Image URLs')
        ),
        default='sema_filtered_image_urls_value',
        max_length=50
    )
    image_urls_sema_custom_value = TextField(
        blank=True,
        help_text='format: [""]'
    )
    image_urls_premier_choice = CharField(
        choices=(
            ('premier_primary_image_urls_value', 'Premier Primary Image URLs'),
            ('custom_premier_image_urls_value', 'Custom Premier Image URLs')
        ),
        default='premier_primary_image_urls_value',
        max_length=50
    )
    image_urls_premier_custom_value = TextField(
        blank=True,
        help_text='format: [""]'
    )
    images_choice = CharField(
        choices=(
            ('images_dict_all_value', 'All Images'),
            ('images_dict_sema_value', 'SEMA Images'),
            ('images_dict_premier_value', 'Premier Images'),
            ('images_dict_custom_value', 'Custom Images')
        ),
        default='images_dict_sema_value',
        max_length=50
    )
    images_custom_value = TextField(
        blank=True,
        help_text='[{"link"}]'
    )

    # <editor-fold desc="internal properties ...">
    @property
    def has_premier_product(self):
        return bool(
            self.product.item
            and self.product.item.premier_product
        )

    @property
    def has_sema_product(self):
        return bool(
            self.product.item
            and self.product.item.sema_product
        )

    @property
    def sema_product(self):
        return (
            self.product.item.sema_product
            if self.has_sema_product else None
        )

    @property
    def sema_brand(self):
        return (
            self.sema_product.dataset.brand
            if self.has_sema_product
            and self.sema_product.dataset.brand.is_relevant
            else None
        )

    @property
    def sema_categories(self):
        return (
            self.sema_product.categories.filter(
                is_relevant=True
            )
            if self.has_sema_product else None
        )

    @property
    def sema_vehicles(self):
        return (
            self.sema_product.vehicles.filter(
                is_relevant=True
            ).order_by(
                'base_vehicle__make_year__make__name',
                'base_vehicle__model__name',
                'submodel__name',
                'base_vehicle__make_year__year__year'
            )
            if self.has_sema_product else None
        )

    @property
    def sema_description_pies_attributes(self):
        return (
            self.sema_product.description_pies_attributes.all()
            if self.has_sema_product else None
        )

    @property
    def sema_digital_assets_pies_attributes(self):
        return (
            self.sema_product.digital_assets_pies_attributes.all()
            if self.has_sema_product else None
        )

    @property
    def premier_product(self):
        return (
            self.product.item.premier_product
            if self.has_premier_product else None
        )

    @property
    def shopify_product(self):
        return self.product

    @property
    def shopify_variant(self):
        return self.product.variants.first()

    @property
    def shopify_tags(self):
        return self.product.tags.all()

    @property
    def shopify_metafields(self):
        return self.product.metafields.all()

    @property
    def shopify_images(self):
        return self.product.images.all()

    def get_premier_product_attr_value(self, attr):
        if not self.premier_product:
            return None

        value = getattr(self.premier_product, attr)
        if not value:
            return None

        return value

    def get_sema_product_attr_value(self, attr):
        if not self.sema_product:
            return None

        value = getattr(self.sema_product, attr)
        if not value:
            return None

        return value

    def get_shopify_product_attr_value(self, attr):
        value = getattr(self.shopify_product, attr)
        if not value:
            return None

        return value

    def get_shopify_variant_attr_value(self, attr):
        value = getattr(self.shopify_variant, attr)
        if not value:
            return None

        return value

    def get_sema_description_pies_attribute_value(self, segment):
        if not self.sema_description_pies_attributes:
            return None

        pies_attrs = self.sema_description_pies_attributes.filter(
            segment__startswith=segment
        )

        if pies_attrs.count() == 0:
            return None
        elif pies_attrs.count() == 1:
            return pies_attrs.first().value.strip()
        else:
            values = []
            for index, pies_attr in enumerate(pies_attrs, start=1):
                values.append(f'{index}: {pies_attr.value.strip()}')
            return ', '.join(values)

    def get_short_text_preview(self, value):
        max_length = 20

        if not value:
            return None

        value_length = len(value)

        if value_length <= max_length:
            return value

        return f'{value[:max_length]} (+{value_length - max_length})'

    def get_short_images_preview(self, values):
        max_length = 5

        if not values:
            return None

        value_length = len(values)

        if value_length <= max_length:
            return get_images_preview(values)

        return (
            get_images_preview(values[:max_length], width="50")
            + mark_safe(f'+({len(values) - max_length})')
        )
    # </editor-fold>

    # <editor-fold desc="value properties ...">
    @property
    def premier_description_value(self):
        field = 'description'

        value = self.get_premier_product_attr_value(field)
        if not value:
            return None

        return value.strip()

    @property
    def premier_weight_value(self):
        field = 'weight'

        value = self.get_premier_product_attr_value(field)
        if not value:
            return None

        return round(value, 2)

    @property
    def premier_cost_cad_value(self):
        field = 'cost_cad'

        value = self.get_premier_product_attr_value(field)
        if not value:
            return None

        return round(value, 2)

    @property
    def premier_cost_usd_value(self):
        field = 'cost_usd'

        value = self.get_premier_product_attr_value(field)
        if not value:
            return None

        return round(value, 2)

    @property
    def premier_premier_part_number_value(self):
        field = 'premier_part_number'

        value = self.get_premier_product_attr_value(field)
        if not value:
            return None

        return value.strip()

    @property
    def premier_upc_value(self):
        field = 'upc'

        value = self.get_premier_product_attr_value(field)
        if not value:
            return None

        return value.strip()

    @property
    def premier_primary_image_urls_value(self):
        field = 'primary_image'

        value = self.get_premier_product_attr_value(field)
        if not value:
            return None

        return [settings.COMPANY_HOST + value.url]

    @property
    def sema_description_def_value(self):
        segment = 'C10_DEF'
        return self.get_sema_description_pies_attribute_value(segment)

    @property
    def sema_description_des_value(self):
        segment = 'C10_DES'
        return self.get_sema_description_pies_attribute_value(segment)

    @property
    def sema_description_inv_value(self):
        segment = 'C10_INV'
        return self.get_sema_description_pies_attribute_value(segment)

    @property
    def sema_description_ext_value(self):
        segment = 'C10_EXT'
        return self.get_sema_description_pies_attribute_value(segment)

    @property
    def sema_description_tle_value(self):
        segment = 'C10_TLE'
        return self.get_sema_description_pies_attribute_value(segment)

    @property
    def sema_description_sho_value(self):
        segment = 'C10_SHO'
        return self.get_sema_description_pies_attribute_value(segment)

    @property
    def sema_description_mkt_value(self):
        segment = 'C10_MKT'
        return self.get_sema_description_pies_attribute_value(segment)

    @property
    def sema_description_key_value(self):
        segment = 'C10_KEY'
        return self.get_sema_description_pies_attribute_value(segment)

    @property
    def sema_description_asc_value(self):
        segment = 'C10_ASC'
        return self.get_sema_description_pies_attribute_value(segment)

    @property
    def sema_description_asm_value(self):
        segment = 'C10_ASM'
        return self.get_sema_description_pies_attribute_value(segment)

    @property
    def sema_description_fab_value(self):
        segment = 'C10_FAB'
        return self.get_sema_description_pies_attribute_value(segment)

    @property
    def sema_description_lab_value(self):
        segment = 'C10_LAB'
        return self.get_sema_description_pies_attribute_value(segment)

    @property
    def sema_description_shp_value(self):
        segment = 'C10_SHP'
        return self.get_sema_description_pies_attribute_value(segment)

    @property
    def sema_description_oth_value(self):
        if not self.sema_description_pies_attributes:
            return None

        pies_attrs = self.sema_description_pies_attributes.exclude(
            Q(segment__startswith='C10_DEF')
            | Q(segment__startswith='C10_DES')
            | Q(segment__startswith='C10_INV')
            | Q(segment__startswith='C10_EXT')
            | Q(segment__startswith='C10_TLE')
            | Q(segment__startswith='C10_SHO')
            | Q(segment__startswith='C10_MKT')
            | Q(segment__startswith='C10_KEY')
            | Q(segment__startswith='C10_ASC')
            | Q(segment__startswith='C10_ASM')
            | Q(segment__startswith='C10_FAB')
            | Q(segment__startswith='C10_LAB')
            | Q(segment__startswith='C10_SHP')
        )

        if pies_attrs.count() == 0:
            return None
        elif pies_attrs.count() == 1:
            return pies_attrs.first().value.strip()
        else:
            values = []
            for index, pies_attr in enumerate(pies_attrs, start=1):
                values.append(f'{index}: {pies_attr.value.strip()}')
            return ', '.join(values)

    @property
    def sema_html_value(self):
        attr = 'clean_html'

        if not self.sema_product:
            return None

        value = self.get_sema_product_attr_value(attr)
        if not value:
            return None

        return value.strip()

    @property
    def sema_vehicles_value(self):
        vehicles = self.sema_vehicles
        if not vehicles:
            return None

        values = []
        for vehicle in vehicles:
            values.append(
                {
                    'year': vehicle.base_vehicle.make_year.year.year,
                    'make': vehicle.base_vehicle.make_year.make.name,
                    'model': vehicle.base_vehicle.model.name,
                    'submodel': vehicle.submodel.name
                }
            )
        return values

    @property
    def sema_brand_tag_names_value(self):
        brand = self.sema_brand
        if not brand:
            return None

        return [brand.tag_name]

    @property
    def sema_category_tag_names_value(self):
        categories = self.sema_categories
        if not categories:
            return None

        return [category.tag_name for category in categories]

    @property
    def sema_filtered_image_urls_value(self):
        pies_attrs = self.sema_digital_assets_pies_attributes
        if not pies_attrs:
            return None

        pies_attrs = pies_attrs.exclude(
            Q(value__endswith='.pdf')
            | Q(value__contains='logo')
        )
        if not pies_attrs:
            return None

        return [pies_attr.value for pies_attr in pies_attrs]

    @property
    def custom_title_value(self):
        field = 'title_custom_value'

        value = getattr(self, field)
        if not value:
            return None

        return value.strip()

    @property
    def custom_body_html_value(self):
        field = 'body_html_custom_value'

        value = getattr(self, field)
        if not value:
            return None

        return value.strip()

    @property
    def custom_variant_weight_value(self):
        field = 'variant_weight_custom_value'

        value = getattr(self, field)
        if not value:
            return None

        return round(value, 2)

    @property
    def custom_variant_cost_value(self):
        field = 'variant_cost_custom_value'

        value = getattr(self, field)
        if not value:
            return None

        return round(value, 2)

    @property
    def custom_variant_price_base_value(self):
        field = 'variant_price_base_custom_value'

        value = getattr(self, field)
        if not value:
            return None

        return round(value, 2)

    @property
    def custom_variant_sku_value(self):
        field = 'variant_sku_custom_value'

        value = getattr(self, field)
        if not value:
            return None

        return value.strip()

    @property
    def custom_variant_barcode_value(self):
        field = 'variant_barcode_custom_value'

        value = getattr(self, field)
        if not value:
            return None

        return value.strip()

    @property
    def custom_packaging_metafield_value_value(self):
        field = 'metafield_value_packaging_custom_value'

        value = getattr(self, field)
        if not value:
            return None

        return value.strip()

    @property
    def custom_fitments_metafield_value_value(self):
        field = 'metafield_value_fitments_custom_value'

        values = getattr(self, field)
        if not values:
            return None

        return json.loads(values.strip())

    @property
    def custom_vendor_tag_names_value(self):
        field = 'tag_names_vendor_custom_value'

        values = getattr(self, field)
        if not values:
            return None

        return json.loads(values.strip())

    @property
    def custom_collection_tag_names_value(self):
        attr = 'tag_names_collection_custom_value'

        values = getattr(self, attr)
        if not values:
            return None

        return json.loads(values.strip())

    @property
    def custom_sema_image_urls_value(self):
        attr = 'image_urls_sema_custom_value'

        values = getattr(self, attr)
        if not values:
            return None

        return json.loads(values.strip())

    @property
    def custom_premier_image_urls_value(self):
        attr = 'image_urls_premier_custom_value'

        values = getattr(self, attr)
        if not values:
            return None

        return json.loads(values.strip())

    @property
    def metafields_dict_packaging_value(self):
        choice_field = 'metafield_value_packaging_choice'

        value = getattr(self, getattr(self, choice_field))
        if not value:
            return None

        return [
            {
                'namespace': 'additional',
                'key': 'packaging',
                'owner_resource': ShopifyMetafield.PRODUCT_OWNER_RESOURCE,
                'value': value,
                'value_type': ShopifyMetafield.STRING_VALUE_TYPE
            }
        ]

    @property
    def metafields_dict_fitments_value(self):
        choice_field = 'metafield_value_fitments_choice'

        values = getattr(self, getattr(self, choice_field))
        if not values:
            return None

        return [
            {
                'namespace': 'additional',
                'key': 'fitments',
                'owner_resource': ShopifyMetafield.PRODUCT_OWNER_RESOURCE,
                'value': json.dumps(values),
                'value_type': ShopifyMetafield.STRING_VALUE_TYPE
            }
        ]

    @property
    def metafields_dict_custom_value(self):
        attr = 'metafields_custom_value'

        values = getattr(self, attr)
        if not values:
            return None

        return sorted(
            json.loads(values.strip()),
            key=lambda k: k['value']
        )

    @property
    def metafields_dict_all_value(self):
        attrs = [
            'metafields_dict_packaging_value',
            'metafields_dict_fitments_value',
            'metafields_dict_custom_value'
        ]

        metafields = []
        for attr in attrs:
            values = getattr(self, attr)
            if values:
                metafields += values

        if not metafields:
            return None

        return sorted(metafields, key=lambda k: k['value'])

    @property
    def tags_dict_vendor_value(self):
        choice_field = 'tag_names_vendor_choice'

        values = getattr(self, getattr(self, choice_field))
        if not values:
            return None

        return sorted(
            [
                {'name': tag_name}
                for tag_name in values
            ],
            key=lambda k: k['name']
        )

    @property
    def tags_dict_collection_value(self):
        choice_field = 'tag_names_collection_choice'

        values = getattr(self, getattr(self, choice_field))
        if not values:
            return None

        return sorted(
            [
                {'name': tag_name}
                for tag_name in values
            ],
            key=lambda k: k['name']
        )

    @property
    def tags_dict_custom_value(self):
        attr = 'tags_custom_value'

        values = getattr(self, attr)
        if not values:
            return None

        return sorted(
            json.loads(values.strip()),
            key=lambda k: k['name']
        )

    @property
    def tags_dict_all_value(self):
        attrs = [
            'tags_dict_vendor_value',
            'tags_dict_collection_value',
            'tags_dict_custom_value'
        ]

        tags = []
        for attr in attrs:
            values = getattr(self, attr)
            if values:
                tags += values

        if not tags:
            return None

        return sorted(tags, key=lambda k: k['name'])

    @property
    def images_dict_sema_value(self):
        choice_field = 'image_urls_sema_choice'

        values = getattr(self, getattr(self, choice_field))
        if not values:
            return None

        return sorted(
            [
                {'link': image_url}
                for image_url in values
            ],
            key=lambda k: k['link']
        )

    @property
    def images_dict_premier_value(self):
        choice_field = 'image_urls_premier_choice'

        values = getattr(self, getattr(self, choice_field))
        if not values:
            return None

        return sorted(
            [
                {'link': image_url}
                for image_url in values
            ],
            key=lambda k: k['link']
        )

    @property
    def images_dict_custom_value(self):
        attr = 'images_custom_value'

        values = getattr(self, attr)
        if not values:
            return None

        return sorted(
            json.loads(values.strip()),
            key=lambda k: k['link']
        )

    @property
    def images_dict_all_value(self):
        attrs = [
            'images_dict_sema_value',
            'images_dict_premier_value',
            'images_dict_custom_value'
        ]

        images = []
        for attr in attrs:
            values = getattr(self, attr)
            if values:
                images += values

        if not images:
            return None

        return sorted(images, key=lambda k: k['link'])
    # </editor-fold>

    # <editor-fold desc="value preview properties ...">
    @property
    def premier_description_value_short_preview(self):
        value_attr = 'premier_description_value'
        return self.get_short_text_preview(getattr(self, value_attr))
    premier_description_value_short_preview.fget.short_description = (
        'Premier Description'
    )

    @property
    def premier_description_value_preview(self):
        value_attr = 'premier_description_value'
        return getattr(self, value_attr)
    premier_description_value_preview.fget.short_description = (
        'Premier Description'
    )

    @property
    def premier_weight_value_preview(self):
        value_attr = 'premier_weight_value'
        return getattr(self, value_attr)
    premier_weight_value_preview.fget.short_description = 'Premier Weight'

    @property
    def premier_cost_cad_value_preview(self):
        value_attr = 'premier_cost_cad_value'
        return getattr(self, value_attr)
    premier_cost_cad_value_preview.fget.short_description = 'Premier Cost CAD'

    @property
    def premier_cost_usd_value_preview(self):
        value_attr = 'premier_cost_usd_value'
        return getattr(self, value_attr)
    premier_cost_usd_value_preview.fget.short_description = 'Premier Cost USD'

    @property
    def premier_premier_part_number_value_preview(self):
        value_attr = 'premier_premier_part_number_value'
        return getattr(self, value_attr)
    premier_premier_part_number_value_preview.fget.short_description = (
        'Premier Part Number'
    )

    @property
    def premier_upc_value_preview(self):
        value_attr = 'premier_upc_value'
        return getattr(self, value_attr)
    premier_upc_value_preview.fget.short_description = 'Premier UPC'

    @property
    def premier_primary_image_urls_value_preview(self):
        value_attr = 'premier_primary_image_urls_value'
        values = getattr(self, value_attr)
        if not values:
            return None

        return get_json_preview(json.dumps(values))
    premier_primary_image_urls_value_preview.fget.short_description = (
        'Premier Primary Images'
    )

    @property
    def premier_primary_images_short_preview(self):
        value_attr = 'premier_primary_image_urls_value'
        values = getattr(self, value_attr)
        if not values:
            return None

        return self.get_short_images_preview(values)
    premier_primary_images_short_preview.fget.short_description = (
        'Premier Primary Images'
    )

    @property
    def premier_primary_images_preview(self):
        value_attr = 'premier_primary_image_urls_value'
        values = getattr(self, value_attr)
        if not values:
            return None

        return get_images_preview(values)
    premier_primary_images_preview.fget.short_description = (
        'Premier Primary Images'
    )

    @property
    def sema_description_def_value_short_preview(self):
        value_attr = 'sema_description_def_value'
        return self.get_short_text_preview(getattr(self, value_attr))
    sema_description_def_value_short_preview.fget.short_description = (
        'SEMA DEF Description'
    )

    @property
    def sema_description_def_value_preview(self):
        value_attr = 'sema_description_def_value'
        return getattr(self, value_attr)
    sema_description_def_value_preview.fget.short_description = (
        'SEMA DEF Description'
    )

    @property
    def sema_description_des_value_short_preview(self):
        value_attr = 'sema_description_des_value'
        return self.get_short_text_preview(getattr(self, value_attr))
    sema_description_des_value_short_preview.fget.short_description = (
        'SEMA DES Description'
    )

    @property
    def sema_description_des_value_preview(self):
        value_attr = 'sema_description_des_value'
        return getattr(self, value_attr)
    sema_description_des_value_preview.fget.short_description = (
        'SEMA DES Description'
    )

    @property
    def sema_description_inv_value_short_preview(self):
        value_attr = 'sema_description_inv_value'
        return self.get_short_text_preview(getattr(self, value_attr))
    sema_description_inv_value_short_preview.fget.short_description = (
        'SEMA INV Description'
    )

    @property
    def sema_description_inv_value_preview(self):
        value_attr = 'sema_description_inv_value'
        return getattr(self, value_attr)
    sema_description_inv_value_preview.fget.short_description = (
        'SEMA INV Description'
    )

    @property
    def sema_description_ext_value_short_preview(self):
        value_attr = 'sema_description_ext_value'
        return self.get_short_text_preview(getattr(self, value_attr))
    sema_description_ext_value_short_preview.fget.short_description = (
        'SEMA EXT Description'
    )

    @property
    def sema_description_ext_value_preview(self):
        value_attr = 'sema_description_ext_value'
        return getattr(self, value_attr)
    sema_description_ext_value_preview.fget.short_description = (
        'SEMA EXT Description'
    )

    @property
    def sema_description_tle_value_short_preview(self):
        value_attr = 'sema_description_tle_value'
        return self.get_short_text_preview(getattr(self, value_attr))
    sema_description_tle_value_short_preview.fget.short_description = (
        'SEMA TLE Description'
    )

    @property
    def sema_description_tle_value_preview(self):
        value_attr = 'sema_description_tle_value'
        return getattr(self, value_attr)
    sema_description_tle_value_preview.fget.short_description = (
        'SEMA TLE Description'
    )

    @property
    def sema_description_sho_value_short_preview(self):
        value_attr = 'sema_description_sho_value'
        return self.get_short_text_preview(getattr(self, value_attr))
    sema_description_sho_value_short_preview.fget.short_description = (
        'SEMA SHO Description'
    )

    @property
    def sema_description_sho_value_preview(self):
        value_attr = 'sema_description_sho_value'
        return getattr(self, value_attr)
    sema_description_sho_value_preview.fget.short_description = (
        'SEMA SHO Description'
    )

    @property
    def sema_description_mkt_value_short_preview(self):
        value_attr = 'sema_description_mkt_value'
        return self.get_short_text_preview(getattr(self, value_attr))
    sema_description_mkt_value_short_preview.fget.short_description = (
        'SEMA MKT Description'
    )

    @property
    def sema_description_mkt_value_preview(self):
        value_attr = 'sema_description_mkt_value'
        return getattr(self, value_attr)
    sema_description_mkt_value_preview.fget.short_description = (
        'SEMA MKT Description'
    )

    @property
    def sema_description_key_value_short_preview(self):
        value_attr = 'sema_description_key_value'
        return self.get_short_text_preview(getattr(self, value_attr))
    sema_description_mkt_value_short_preview.fget.short_description = (
        'SEMA KEY Description'
    )

    @property
    def sema_description_key_value_preview(self):
        value_attr = 'sema_description_key_value'
        return getattr(self, value_attr)
    sema_description_mkt_value_preview.fget.short_description = (
        'SEMA KEY Description'
    )

    @property
    def sema_description_asc_value_short_preview(self):
        value_attr = 'sema_description_asc_value'
        return self.get_short_text_preview(getattr(self, value_attr))
    sema_description_asc_value_short_preview.fget.short_description = (
        'SEMA ASC Description'
    )

    @property
    def sema_description_asc_value_preview(self):
        value_attr = 'sema_description_asc_value'
        return getattr(self, value_attr)
    sema_description_asc_value_preview.fget.short_description = (
        'SEMA ASC Description'
    )

    @property
    def sema_description_asm_value_short_preview(self):
        value_attr = 'sema_description_asm_value'
        return self.get_short_text_preview(getattr(self, value_attr))
    sema_description_asm_value_short_preview.fget.short_description = (
        'SEMA ASM Description'
    )

    @property
    def sema_description_asm_value_preview(self):
        value_attr = 'sema_description_asm_value'
        return getattr(self, value_attr)
    sema_description_asm_value_preview.fget.short_description = (
        'SEMA ASM Description'
    )

    @property
    def sema_description_fab_value_short_preview(self):
        value_attr = 'sema_description_fab_value'
        return self.get_short_text_preview(getattr(self, value_attr))
    sema_description_fab_value_short_preview.fget.short_description = (
        'SEMA FAB Description'
    )

    @property
    def sema_description_fab_value_preview(self):
        value_attr = 'sema_description_fab_value'
        return getattr(self, value_attr)
    sema_description_fab_value_preview.fget.short_description = (
        'SEMA FAB Description'
    )

    @property
    def sema_description_lab_value_short_preview(self):
        value_attr = 'sema_description_lab_value'
        return self.get_short_text_preview(getattr(self, value_attr))
    sema_description_lab_value_short_preview.fget.short_description = (
        'SEMA LAB Description'
    )

    @property
    def sema_description_lab_value_preview(self):
        value_attr = 'sema_description_lab_value'
        return getattr(self, value_attr)
    sema_description_lab_value_preview.fget.short_description = (
        'SEMA LAB Description'
    )

    @property
    def sema_description_shp_value_short_preview(self):
        value_attr = 'sema_description_shp_value'
        return self.get_short_text_preview(getattr(self, value_attr))
    sema_description_shp_value_short_preview.fget.short_description = (
        'SEMA SHP Description'
    )

    @property
    def sema_description_shp_value_preview(self):
        value_attr = 'sema_description_shp_value'
        return getattr(self, value_attr)
    sema_description_shp_value_preview.fget.short_description = (
        'SEMA SHP Description'
    )

    @property
    def sema_description_oth_value_short_preview(self):
        value_attr = 'sema_description_oth_value'
        return self.get_short_text_preview(getattr(self, value_attr))
    sema_description_oth_value_short_preview.fget.short_description = (
        'SEMA OTH Description'
    )

    @property
    def sema_description_oth_value_preview(self):
        value_attr = 'sema_description_oth_value'
        return getattr(self, value_attr)
    sema_description_oth_value_preview.fget.short_description = (
        'SEMA OTH Description'
    )

    @property
    def sema_html_value_preview(self):
        value_attr = 'sema_html_value'
        return getattr(self, value_attr)
    sema_html_value_preview.fget.short_description = 'SEMA HTML'

    @property
    def sema_html_preview(self):
        value_attr = 'sema_html_value'
        value = getattr(self, value_attr)
        if not value:
            return None

        return get_html_preview(value)
    sema_html_preview.fget.short_description = 'SEMA HTML'

    @property
    def sema_vehicles_value_preview(self):
        value_attr = 'sema_vehicles_value'
        values = getattr(self, value_attr)
        if not values:
            return None

        return get_json_preview(json.dumps(values))
    sema_vehicles_value_preview.fget.short_description = 'SEMA Vehicles'

    @property
    def sema_brand_tag_names_value_preview(self):
        value_attr = 'sema_brand_tag_names_value'
        values = getattr(self, value_attr)
        if not values:
            return None

        return get_json_preview(json.dumps(values))
    sema_brand_tag_names_value_preview.fget.short_description = (
        'SEMA Brand Tag Names'
    )

    @property
    def sema_category_tag_names_value_preview(self):
        value_attr = 'sema_category_tag_names_value'
        values = getattr(self, value_attr)
        if not values:
            return None

        return get_json_preview(json.dumps(values))
    sema_category_tag_names_value_preview.fget.short_description = (
        'SEMA Category Tag Names'
    )

    @property
    def sema_filtered_image_urls_value_preview(self):
        value_attr = 'sema_filtered_image_urls_value'
        values = getattr(self, value_attr)
        if not values:
            return None

        return get_images_preview(values)
    sema_filtered_image_urls_value_preview.fget.short_description = (
        'SEMA Filtered Images'
    )

    @property
    def sema_filtered_images_short_preview(self):
        value_attr = 'sema_filtered_image_urls_value'
        values = getattr(self, value_attr)
        if not values:
            return None

        return self.get_short_images_preview(values)
    sema_filtered_images_short_preview.fget.short_description = (
        'SEMA Filtered Images'
    )

    @property
    def sema_filtered_images_preview(self):
        value_attr = 'sema_filtered_image_urls_value'
        values = getattr(self, value_attr)
        if not values:
            return None

        return get_images_preview(values)
    sema_filtered_images_preview.fget.short_description = (
        'SEMA Filtered Images'
    )
    # </editor-fold>

    # <editor-fold desc="result properties ...">
    @property
    def title_result(self):
        choice_field = 'title_choice'
        return getattr(self, getattr(self, choice_field))
    title_result.fget.short_description = ''

    @property
    def body_html_result(self):
        choice_field = 'body_html_choice'
        return getattr(self, getattr(self, choice_field))
    body_html_result.fget.short_description = ''

    @property
    def variant_weight_result(self):
        choice_field = 'variant_weight_choice'
        return getattr(self, getattr(self, choice_field))
    variant_weight_result.fget.short_description = ''

    @property
    def variant_weight_unit_result(self):
        choice_field = 'variant_weight_unit_choice'
        return getattr(self, choice_field)
    variant_weight_unit_result.fget.short_description = ''

    @property
    def variant_cost_result(self):
        choice_field = 'variant_cost_choice'
        return getattr(self, getattr(self, choice_field))
    variant_cost_result.fget.short_description = ''

    @property
    def variant_price_result(self):
        price_base_choice_field = 'variant_price_base_choice'
        price_markup_choice_field = 'variant_price_markup_choice'

        price_base = getattr(self, getattr(self, price_base_choice_field))
        price_markup = Decimal(getattr(self, price_markup_choice_field))

        if not price_base:
            return None

        return round(price_base + (price_base * price_markup), 2)
    variant_price_result.fget.short_description = ''

    @property
    def variant_sku_result(self):
        choice_field = 'variant_sku_choice'
        return getattr(self, getattr(self, choice_field))
    variant_sku_result.fget.short_description = ''

    @property
    def variant_barcode_result(self):
        choice_field = 'variant_barcode_choice'
        return getattr(self, getattr(self, choice_field))
    variant_barcode_result.fget.short_description = ''

    @property
    def metafields_result(self):
        choice_field = 'metafields_choice'
        return getattr(self, getattr(self, choice_field))
    metafields_result.fget.short_description = ''

    @property
    def tags_result(self):
        choice_field = 'tags_choice'
        return getattr(self, getattr(self, choice_field))
    tags_result.fget.short_description = ''

    @property
    def images_result(self):
        choice_field = 'images_choice'
        return getattr(self, getattr(self, choice_field))
    images_result.fget.short_description = ''
    # </editor-fold>

    # <editor-fold desc="result preview properties ...">
    @property
    def title_result_preview(self):
        result_attr = 'title_result'
        return getattr(self, result_attr)

    @property
    def body_html_result_preview(self):
        result_attr = 'body_html_result'
        result = getattr(self, result_attr)
        if not result:
            return None

        return get_html_preview(result)

    @property
    def variant_weight_result_preview(self):
        result_attr = 'variant_weight_result'
        return getattr(self, result_attr)

    @property
    def variant_weight_unit_result_preview(self):
        result_attr = 'variant_weight_unit_result'
        return getattr(self, result_attr)

    @property
    def variant_cost_result_preview(self):
        result_attr = 'variant_cost_result'
        return getattr(self, result_attr)

    @property
    def variant_price_result_preview(self):
        result_attr = 'variant_price_result'
        return getattr(self, result_attr)

    @property
    def variant_sku_result_preview(self):
        result_attr = 'variant_sku_result'
        return getattr(self, result_attr)

    @property
    def variant_barcode_result_preview(self):
        result_attr = 'variant_barcode_result'
        return getattr(self, result_attr)

    @property
    def metafields_result_preview(self):
        result_attr = 'metafields_result'
        values = getattr(self, result_attr)
        if not values:
            return None

        return get_json_preview(json.dumps(values))

    @property
    def tags_result_preview(self):
        result_attr = 'tags_result'
        values = getattr(self, result_attr)
        if not values:
            return None

        return get_json_preview(json.dumps(values))

    @property
    def images_result_preview(self):
        result_attr = 'images_result'
        values = getattr(self, result_attr)
        if not values:
            return None

        return get_json_preview(json.dumps(values))
    # </editor-fold>

    # <editor-fold desc="current properties ...">
    @property
    def title_current(self):
        field = 'title'
        return self.get_shopify_product_attr_value(field)
    title_current.fget.short_description = ''

    @property
    def body_html_current(self):
        field = 'body_html'
        return self.get_shopify_product_attr_value(field)
    body_html_current.fget.short_description = ''

    @property
    def variant_weight_current(self):
        field = 'weight'
        return self.get_shopify_variant_attr_value(field)
    variant_weight_current.fget.short_description = ''

    @property
    def variant_weight_unit_current(self):
        field = 'weight_unit'
        return self.get_shopify_variant_attr_value(field)
    variant_weight_unit_current.fget.short_description = ''

    @property
    def variant_cost_current(self):
        field = 'cost'
        return self.get_shopify_variant_attr_value(field)
    variant_cost_current.fget.short_description = ''

    @property
    def variant_price_current(self):
        field = 'price'
        return self.get_shopify_variant_attr_value(field)
    variant_price_current.fget.short_description = ''

    @property
    def variant_sku_current(self):
        field = 'sku'
        return self.get_shopify_variant_attr_value(field)
    variant_sku_current.fget.short_description = ''

    @property
    def variant_barcode_current(self):
        field = 'barcode'
        return self.get_shopify_variant_attr_value(field)
    variant_barcode_current.fget.short_description = ''

    @property
    def metafields_current(self):
        metafields = self.shopify_metafields
        if not metafields:
            return None

        return sorted(
            [
                {
                    'namespace': metafield.namespace,
                    'key': metafield.key,
                    'owner_resource': metafield.owner_resource,
                    'value': metafield.value,
                    'value_type': metafield.value_type
                }
                for metafield in metafields
            ],
            key=lambda k: k['value']
        )
    metafields_current.fget.short_description = ''

    @property
    def tags_current(self):
        tags = self.shopify_tags
        if not tags:
            return None

        return sorted(
            [{'name': tag.name} for tag in tags],
            key=lambda k: k['name']
        )
    tags_current.fget.short_description = ''

    @property
    def images_current(self):
        images = self.shopify_images
        if not images:
            return None

        return sorted(
            [{'link': image.link} for image in images],
            key=lambda k: k['link']
        )
    images_current.fget.short_description = ''
    # </editor-fold>

    # <editor-fold desc="current preview properties ...">
    @property
    def title_current_preview(self):
        current_attr = 'title_current'
        return getattr(self, current_attr)

    @property
    def body_html_current_preview(self):
        current_attr = 'body_html_current'
        current = getattr(self, current_attr)
        if not current:
            return None

        return get_html_preview(current)

    @property
    def variant_weight_current_preview(self):
        current_attr = 'variant_weight_current'
        return getattr(self, current_attr)

    @property
    def variant_weight_unit_current_preview(self):
        current_attr = 'variant_weight_unit_current'
        return getattr(self, current_attr)

    @property
    def variant_cost_current_preview(self):
        current_attr = 'variant_cost_current'
        return getattr(self, current_attr)

    @property
    def variant_price_current_preview(self):
        current_attr = 'variant_price_current'
        return getattr(self, current_attr)

    @property
    def variant_sku_current_preview(self):
        current_attr = 'variant_sku_current'
        return getattr(self, current_attr)

    @property
    def variant_barcode_current_preview(self):
        current_attr = 'variant_barcode_current'
        return getattr(self, current_attr)

    @property
    def metafields_current_preview(self):
        current_attr = 'metafields_current'
        values = getattr(self, current_attr)
        if not values:
            return None

        return get_json_preview(json.dumps(values))

    @property
    def tags_current_preview(self):
        current_attr = 'tags_current'
        values = getattr(self, current_attr)
        if not values:
            return None

        return get_json_preview(json.dumps(values))

    @property
    def images_current_preview(self):
        current_attr = 'images_current'
        values = getattr(self, current_attr)
        if not values:
            return None

        return get_json_preview(json.dumps(values))
    # </editor-fold>

    # <editor-fold desc="match properties ...">
    def title_match(self):
        current_attr = 'title_current'
        result_attr = 'title_result'

        current = getattr(self, current_attr)
        result = getattr(self, result_attr)
        if not result:
            return None

        return bool(current == result)
    title_match.boolean = True
    title_match.short_description = 'Title Match'

    def body_html_match(self):
        current_attr = 'body_html_current'
        result_attr = 'body_html_result'

        current = getattr(self, current_attr)
        result = getattr(self, result_attr)
        if not result:
            return None

        return bool(current == result)
    body_html_match.boolean = True
    body_html_match.short_description = 'Body HTML Match'

    def variant_weight_match(self):
        current_attr = 'variant_weight_current'
        result_attr = 'variant_weight_result'

        current = getattr(self, current_attr)
        result = getattr(self, result_attr)
        if not result:
            return None

        return bool(current == result)
    variant_weight_match.boolean = True
    variant_weight_match.short_description = 'Weight Match'

    def variant_weight_unit_match(self):
        current_attr = 'variant_weight_unit_current'
        result_attr = 'variant_weight_unit_result'

        current = getattr(self, current_attr)
        result = getattr(self, result_attr)

        return bool(current == result)
    variant_weight_unit_match.boolean = True
    variant_weight_unit_match.short_description = 'Weight Unit Match'

    def variant_cost_match(self):
        current_attr = 'variant_cost_current'
        result_attr = 'variant_cost_result'

        current = getattr(self, current_attr)
        result = getattr(self, result_attr)
        if not result:
            return None

        return bool(current == result)
    variant_cost_match.boolean = True
    variant_cost_match.short_description = 'Cost Match'

    def variant_price_match(self):
        current_attr = 'variant_price_current'
        result_attr = 'variant_price_result'

        current = getattr(self, current_attr)
        result = getattr(self, result_attr)
        if not result:
            return None

        return bool(current == result)
    variant_price_match.boolean = True
    variant_price_match.short_description = 'Price Match'

    def variant_sku_match(self):
        current_attr = 'variant_sku_current'
        result_attr = 'variant_sku_result'

        current = getattr(self, current_attr)
        result = getattr(self, result_attr)
        if not result:
            return None

        return bool(current == result)
    variant_sku_match.boolean = True
    variant_sku_match.short_description = 'SKU Match'

    def variant_barcode_match(self):
        current_attr = 'variant_barcode_current'
        result_attr = 'variant_barcode_result'

        current = getattr(self, current_attr)
        result = getattr(self, result_attr)
        if not result:
            return None

        return bool(current == result)
    variant_barcode_match.boolean = True
    variant_barcode_match.short_description = 'Barcode Match'

    def metafields_match(self):
        current_attr = 'metafields_current'
        result_attr = 'metafields_result'

        current = getattr(self, current_attr)
        result = getattr(self, result_attr)
        if not result:
            return None

        return bool(current == result)
    metafields_match.boolean = True
    metafields_match.short_description = 'Metafields Match'

    def tags_match(self):
        current_attr = 'tags_current'
        result_attr = 'tags_result'

        current = getattr(self, current_attr)
        result = getattr(self, result_attr)
        if not result:
            return None

        return bool(current == result)
    tags_match.boolean = True
    tags_match.short_description = 'Tags Match'

    def images_match(self):
        current_attr = 'images_current'
        result_attr = 'images_result'

        current = getattr(self, current_attr)
        result = getattr(self, result_attr)
        if not result:
            return None

        return bool(current == result)
    images_match.boolean = True
    images_match.short_description = 'Images Match'

    def full_match(self):
        return bool(
            self.title_match() is not False
            and self.body_html_match() is not False
            and self.variant_weight_match() is not False
            and self.variant_weight_unit_match() is not False
            and self.variant_cost_match() is not False
            and self.variant_price_match() is not False
            and self.variant_sku_match() is not False
            and self.variant_barcode_match() is not False
            and self.metafields_match() is not False
            and self.tags_match() is not False
            and self.images_match() is not False
        )
    full_match.boolean = True
    full_match.short_description = 'Calculator Match'
    # </editor-fold>

    # <editor-fold desc="difference properties ...">
    @property
    def title_difference(self):
        current_preview_attr = 'title_current_preview'
        result_preview_attr = 'title_result_preview'
        match_attr = 'title_match'

        if getattr(self, match_attr)() is not False:
            return ''

        current_preview = getattr(self, current_preview_attr)
        result_preview = getattr(self, result_preview_attr)

        return f'{current_preview} <- {result_preview}'
    title_difference.fget.short_description = ''

    @property
    def body_html_difference(self):
        current_preview_attr = 'body_html_current_preview'
        result_preview_attr = 'body_html_result_preview'
        match_attr = 'body_html_match'

        if getattr(self, match_attr)() is not False:
            return ''

        current_preview = getattr(self, current_preview_attr)
        result_preview = getattr(self, result_preview_attr)

        return f'{current_preview} <- {result_preview}'
    body_html_difference.fget.short_description = ''

    @property
    def variant_weight_difference(self):
        current_preview_attr = 'variant_weight_current_preview'
        result_preview_attr = 'variant_weight_result_preview'
        match_attr = 'variant_weight_match'

        if getattr(self, match_attr)() is not False:
            return ''

        current_preview = getattr(self, current_preview_attr)
        result_preview = getattr(self, result_preview_attr)

        return f'{current_preview} <- {result_preview}'
    variant_weight_difference.fget.short_description = ''

    @property
    def variant_weight_unit_difference(self):
        current_preview_attr = 'variant_weight_unit_current_preview'
        result_preview_attr = 'variant_weight_unit_result_preview'
        match_attr = 'variant_weight_unit_match'

        if getattr(self, match_attr)() is not False:
            return ''

        current_preview = getattr(self, current_preview_attr)
        result_preview = getattr(self, result_preview_attr)

        return f'{current_preview} <- {result_preview}'
    variant_weight_unit_difference.fget.short_description = ''

    @property
    def variant_cost_difference(self):
        current_preview_attr = 'variant_cost_current_preview'
        result_preview_attr = 'variant_cost_result_preview'
        match_attr = 'variant_cost_match'

        if getattr(self, match_attr)() is not False:
            return ''

        current_preview = getattr(self, current_preview_attr)
        result_preview = getattr(self, result_preview_attr)

        return f'{current_preview} <- {result_preview}'
    variant_cost_difference.fget.short_description = ''

    @property
    def variant_price_difference(self):
        current_preview_attr = 'variant_price_current_preview'
        result_preview_attr = 'variant_price_result_preview'
        match_attr = 'variant_price_match'

        if getattr(self, match_attr)() is not False:
            return ''

        current_preview = getattr(self, current_preview_attr)
        result_preview = getattr(self, result_preview_attr)

        return f'{current_preview} <- {result_preview}'
    variant_price_difference.fget.short_description = ''

    @property
    def variant_sku_difference(self):
        current_preview_attr = 'variant_sku_current_preview'
        result_preview_attr = 'variant_sku_result_preview'
        match_attr = 'variant_sku_match'

        if getattr(self, match_attr)() is not False:
            return ''

        current_preview = getattr(self, current_preview_attr)
        result_preview = getattr(self, result_preview_attr)

        return f'{current_preview} <- {result_preview}'
    variant_sku_difference.fget.short_description = ''

    @property
    def variant_barcode_difference(self):
        current_preview_attr = 'variant_barcode_current_preview'
        result_preview_attr = 'variant_barcode_result_preview'
        match_attr = 'variant_barcode_match'

        if getattr(self, match_attr)() is not False:
            return ''

        current_preview = getattr(self, current_preview_attr)
        result_preview = getattr(self, result_preview_attr)

        return f'{current_preview} <- {result_preview}'
    variant_barcode_difference.fget.short_description = ''

    @property
    def metafields_difference(self):
        current_attr = 'metafields_current'
        result_attr = 'metafields_result'
        match_attr = 'metafields_match'

        if getattr(self, match_attr)() is not False:
            return ''

        current = getattr(self, current_attr)
        result = getattr(self, result_attr)

        return get_json_preview(
            json.dumps(
                diff(
                    current,
                    result,
                    syntax='symmetric'
                )
            )
        )
    metafields_difference.fget.short_description = ''

    @property
    def tags_difference(self):
        current_attr = 'tags_current'
        result_attr = 'tags_result'
        match_attr = 'tags_match'

        if getattr(self, match_attr)() is not False:
            return ''

        current = getattr(self, current_attr)
        result = getattr(self, result_attr)

        return get_json_preview(
            json.dumps(
                diff(
                    current,
                    result,
                    syntax='symmetric'
                )
            )
        )
    tags_difference.fget.short_description = ''

    @property
    def images_difference(self):
        current_attr = 'images_current'
        result_attr = 'images_result'
        match_attr = 'images_match'

        if getattr(self, match_attr)() is not False:
            return ''

        current = getattr(self, current_attr)
        result = getattr(self, result_attr)

        return get_json_preview(
            json.dumps(
                diff(
                    current,
                    result,
                    syntax='symmetric'
                )
            )
        )
    images_difference.fget.short_description = ''
    # </editor-fold>

    # <editor-fold desc="perform properties ...">
    def perform_calculated_fields_update(self):
        try:
            if self.title_match() is False:
                self.shopify_product.title = self.title_result
                self.shopify_product.save()

            if self.body_html_match() is False:
                self.shopify_product.body_html = self.body_html_result
                self.shopify_product.save()

            if self.variant_weight_match() is False:
                self.shopify_variant.weight = self.variant_weight_result
                self.shopify_variant.save()

            if self.variant_weight_unit_match() is False:
                self.shopify_variant.weight_unit = self.variant_weight_unit_result
                self.shopify_variant.save()

            if self.variant_cost_match() is False:
                self.shopify_variant.cost = self.variant_cost_result
                self.shopify_variant.save()

            if self.variant_price_match() is False:
                self.shopify_variant.price = self.variant_price_result
                self.shopify_variant.save()

            if self.variant_sku_match() is False:
                self.shopify_variant.sku = self.variant_sku_result
                self.shopify_variant.save()

            if self.variant_barcode_match() is False:
                self.shopify_variant.barcode = self.variant_barcode_result
                self.shopify_variant.save()

            if self.metafields_match() is False:
                for metafield_data in self.metafields_result:
                    defaults = {
                        'value': metafield_data.pop('value'),
                        'value_type': metafield_data.pop('value_type')
                    }
                    ShopifyMetafield.objects.update_or_create(
                        object_id=self.shopify_product.pk,
                        content_type=ContentType.objects.get_for_model(self.shopify_product),
                        **metafield_data,
                        defaults=defaults
                    )

            if self.tags_match() is False:
                for tag_data in self.tags_result:
                    tag, _ = ShopifyTag.objects.get_or_create(**tag_data)
                    self.shopify_product.tags.add(tag)
                    self.shopify_product.save()

            if self.images_match() is False:
                for image_data in self.images_result:
                    ShopifyImage.objects.get_or_create(
                        product=self.shopify_product,
                        **image_data
                    )

            return self.shopify_product.get_update_success_msg()
        except Exception as err:
            return self.get_instance_error_msg(str(err))
    # </editor-fold>
    
    objects = ShopifyProductCalculatorManager()

    def __str__(self):
        return str(self.product)
