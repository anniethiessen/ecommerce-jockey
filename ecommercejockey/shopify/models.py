import json
from decimal import Decimal

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

from core.mixins import MessagesMixin
from core.models import (
    NotesBaseModel,
    RelevancyBaseModel
)
from .clients import shopify_client
from .managers import (
    ShopifyCollectionManager,
    ShopifyOptionManager,
    ShopifyProductManager,
    ShopifyVariantManager
)


class ShopifyVendor(Model, MessagesMixin):
    name = CharField(
        max_length=255,
        unique=True
    )

    def __str__(self):
        return self.name


class ShopifyTag(Model, MessagesMixin):
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

    class Meta:
        unique_together = [
            'content_type',
            'object_id',
            'owner_resource',
            'namespace',
            'key'
        ]

    def __str__(self):
        return f'{self.content_object} :: {self.namespace} :: {self.key}'


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
    # </editor-fold>

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

        return True

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
                else:
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
            rule_values = [
                value for value in values
                if value['column'] != 'tag' or value['relation'] != 'equals'
            ]
            for rule in self.rules.all():
                if {
                    'column': rule.column,
                    'relation': rule.relation,
                    'condition': rule.condition
                } not in tag_values:
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
        try:
            if self.calculator.title_:
                self.title = self.calculator.title_
            for tag_name in self.calculator.tags_:
                tag, _ = ShopifyTag.objects.get_or_create(name=tag_name)
                self.tags.add(tag)
            self.save()
            for metafield_data in self.calculator.metafields_:
                defaults = {
                    'value': metafield_data.pop('value'),
                    'value_type': metafield_data.pop('value_type')
                }
                metafield, _ = ShopifyMetafield.objects.update_or_create(
                    object_id=self.pk,
                    content_type=ContentType.objects.get_for_model(self),
                    **metafield_data,
                    defaults=defaults
                )
            return self.get_update_success_msg()
        except Exception as err:
            return self.get_instance_error_msg(str(err))

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
            'options': self.api_formatted_options,
            'images': self.api_formatted_images
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

    @property
    def api_formatted_images(self):
        images_data = []
        for image in self.images.all():
            images_data.append(image.api_formatted_data)
        return images_data
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
            for metafield_data in self.calculator.metafields_:
                defaults = {
                    'value': metafield_data.pop('value'),
                    'value_type': metafield_data.pop('value_type')
                }
                metafield, _ = ShopifyMetafield.objects.update_or_create(
                    object_id=self.pk,
                    content_type=ContentType.objects.get_for_model(self),
                    **metafield_data,
                    defaults=defaults
                )
            return self.get_update_success_msg()
        except Exception as err:
            return self.get_instance_error_msg(str(err))

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
        except Exception as err:
            msgs.append(self.get_instance_error_msg(str(err)))

        if not msgs:
            msgs.append(self.get_instance_up_to_date_msg())
        return msgs
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
    src = URLField(
        max_length=250
    )

    # <editor-fold desc="format properties ...">
    @property
    def api_formatted_data(self):
        data = {
            'src': self.src,
        }
        return dict((k, v) for k, v in data.items() if v)
    # </editor-fold>

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


class ShopifyProductCalculator(Model):
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
    def metafields_(self):
        metafields = []
        if self.__has_sema_product and self.sema_product.html:
            metafields.append(
                {
                    'namespace': 'sema',
                    'key': 'html',
                    'owner_resource': ShopifyMetafield.PRODUCT_OWNER_RESOURCE,
                    'value': self.sema_product.clean_html,
                    'value_type': ShopifyMetafield.STRING_VALUE_TYPE
                }
            )
        return metafields
    metafields_.fget.short_description = ''

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
            )
            for category in categories:
                tags.append(category.tag_name)
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
            return round(self.premier_product.weight, 2)
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
            return self.premier_product.upc.strip()
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


class ShopifyCollectionCalculator(Model):
    collection = OneToOneField(
        ShopifyCollection,
        related_name='calculator',
        on_delete=CASCADE
    )

    # <editor-fold desc="update logic properties ...">
    @property
    def category_paths(self):
        if self.collection.level == '1':
            return self.collection.root_category_paths.all()
        elif self.collection.level == '2':
            return self.collection.branch_category_paths.filter(
                shopify_root_collection=self.collection.parent_collection
            )
        elif self.collection.level == '3':
            return self.collection.leaf_category_paths.filter(
                shopify_branch_collection=self.collection.parent_collection,
                shopify_root_collection=self.collection.parent_collection.parent_collection,
            )

    @property
    def sema_category(self):
        if self.collection.level == '1':
            return self.category_paths.first().sema_root_category
        elif self.collection.level == '2':
            return self.category_paths.first().sema_branch_category
        elif self.collection.level == '3':
            return self.category_paths.first().sema_leaf_category

    @property
    def title_(self):
        title = self.sema_category.name

        if self.collection.level == '2':
            title = (
                f'{self.category_paths.first().sema_root_category.name} '
                f'// {title}'
            )

        if self.collection.level == '3':
            title = (
                f'{self.category_paths.first().sema_root_category.name} '
                f'// {self.category_paths.first().sema_branch_category.name} '
                f'// {title}'
            )
        return title
    title_.fget.short_description = ''

    @property
    def tags_(self):
        tags = [self.sema_category.tag_name]

        if int(self.collection.level) > 1:
            tags.append(
                self.category_paths.first().sema_root_category.tag_name
            )

        if int(self.collection.level) > 2:
            tags.append(
                self.category_paths.first().sema_branch_category.tag_name
            )

        return tags
    tags_.fget.short_description = ''

    @property
    def metafields_(self):
        metafields = []

        if int(self.collection.level) > 1:
            metafields.append(
                {
                    'namespace': 'title',
                    'key': 'display_name',
                    'owner_resource':
                        ShopifyMetafield.COLLECTION_OWNER_RESOURCE,
                    'value': self.sema_category.name,
                    'value_type': ShopifyMetafield.STRING_VALUE_TYPE
                }
            )

        if int(self.collection.level) < 3:
            subcollections = []
            for child_collection in self.collection.child_collections.all():
                if child_collection.collection_id and child_collection.handle:
                    subcollections.append(
                        {
                            'id': child_collection.collection_id,
                            'handle': child_collection.handle
                        }
                    )
            if subcollections:
                metafields.append(
                    {
                        'namespace': 'category',
                        'key': 'subcollections',
                        'owner_resource':
                            ShopifyMetafield.COLLECTION_OWNER_RESOURCE,
                        'value': json.dumps(subcollections),
                        'value_type': ShopifyMetafield.JSON_VALUE_TYPE
                    }
                )

        return metafields
    metafields_.fget.short_description = ''
    # </editor-fold>

    def __str__(self):
        return str(self.collection)
