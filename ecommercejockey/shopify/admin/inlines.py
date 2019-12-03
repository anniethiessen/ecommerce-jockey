from django.contrib.admin import (
    StackedInline,
    TabularInline
)
from django.contrib.contenttypes.admin import GenericTabularInline

from core.admin.utils import (
    get_change_view_link,
    get_changelist_view_link,
    get_image_preview
)
from ..models import (
    ShopifyCollection,
    ShopifyCollectionCalculator,
    ShopifyImage,
    ShopifyMetafield,
    ShopifyOption,
    ShopifyProduct,
    ShopifyProductCalculator,
    ShopifyVariant
)
from .forms import LimitedInlineFormSet


class ShopifyMetafieldBaseTabularInline(GenericTabularInline):
    model = ShopifyMetafield
    verbose_name_plural = 'metafields'
    extra = 0
    classes = (
        'collapse',
    )

    fields = (
        'all_link',
        'details_link',
        'id',
        'metafield_id',
        'owner_resource',
        'namespace',
        'value_type',
        'key',
        'value_item_count'
    )

    readonly_fields = (
        'id',
        'details_link',
        'all_link',
        'value_item_count'
    )

    def all_link(self, obj):
        if not obj or not obj.pk or not obj.object_id or not obj.content_type:
            return None

        query = (
            f'object_id__exact={obj.object_id}'
            f'&content_type_id__exact={obj.content_type.pk}'
        )
        return get_changelist_view_link(obj, 'See All', query)
    all_link.short_description = ''

    def details_link(self, obj):
        if not obj or not obj.pk:
            return None

        return get_change_view_link(obj, 'Details')
    details_link.short_description = ''

    def get_queryset(self, request):
        return super().get_queryset(request).with_admin_data()

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'content_type':
            formfield.choices = formfield.choices
        return formfield

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if not request.user.is_superuser:
            readonly_fields += (
                'metafield_id',
            )
        return readonly_fields


class ShopifyVendorProductsTabularInline(TabularInline):
    model = ShopifyProduct
    fk_name = 'vendor'
    formset = LimitedInlineFormSet
    verbose_name_plural = 'products (top 10)'
    all_link_query = 'vendor__id__exact'
    extra = 0
    ordering = (
        'title',
    )
    classes = (
        'collapse',
    )

    fields = (
        'all_link',
        'details_link',
        'id',
        'product_id',
        'title',
        'vendor',
        'is_published',
        'variant_count',
        'option_count',
        'image_count',
        'metafield_count',
        'tag_count',
        'errors',
        'full_match'
    )

    readonly_fields = (
        'id',
        'errors',
        'full_match',
        'details_link',
        'all_link',
        'variant_count',
        'option_count',
        'image_count',
        'tag_count',
        'metafield_count'
    )

    def get_rel_obj(self, obj):
        return getattr(obj, self.fk_name)

    def all_link(self, obj):
        if not obj:
            return None
        query = f'{self.all_link_query}={getattr(self.get_rel_obj(obj), "pk")}'
        return get_changelist_view_link(obj, 'See All', query)
    all_link.short_description = ''

    def details_link(self, obj):
        if not obj:
            return None
        return get_change_view_link(obj, 'Details')
    details_link.short_description = ''

    def variant_count(self, obj):
        if not obj or not obj.pk:
            return None

        return obj._variant_count
    variant_count.admin_order_field = '_variant_count'
    variant_count.short_description = 'variant count'

    def option_count(self, obj):
        if not obj or not obj.pk:
            return None

        return obj._option_count
    option_count.admin_order_field = '_option_count'
    option_count.short_description = 'option count'

    def image_count(self, obj):
        if not obj or not obj.pk:
            return None

        return obj._image_count
    image_count.admin_order_field = '_image_count'
    image_count.short_description = 'image count'

    def tag_count(self, obj):
        if not obj or not obj.pk:
            return None

        return obj._tag_count
    tag_count.admin_order_field = '_tag_count'
    tag_count.short_description = 'tag count'

    def metafield_count(self, obj):
        if not obj or not obj.pk:
            return None

        return obj._metafield_count
    metafield_count.admin_order_field = '_metafield_count'
    metafield_count.short_description = 'metafield count'

    def full_match(self, obj):
        return obj.calculator.full_match()
    full_match.boolean = True
    full_match.short_description = 'calculated'

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'vendor':
            formfield.choices = formfield.choices
        return formfield

    def get_queryset(self, request):
        return super().get_queryset(request).with_admin_data()

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if not request.user.is_superuser:
            readonly_fields += (
                'product_id',
            )
        return readonly_fields


class ShopifyProductImagesTabularInline(TabularInline):
    model = ShopifyImage
    fk_name = 'product'
    verbose_name_plural = 'images'
    all_link_query = 'product__id__exact'
    extra = 0
    classes = (
        'collapse',
    )

    fields = (
        'all_link',
        'details_link',
        'id',
        'image_id',
        'product',
        'link',
        'image_preview'
    )

    readonly_fields = (
        'id',
        'image_preview',
        'details_link',
        'all_link'
    )

    def get_rel_obj(self, obj):
        return getattr(obj, self.fk_name)

    def all_link(self, obj):
        query = f'{self.all_link_query}={getattr(self.get_rel_obj(obj), "pk")}'
        return get_changelist_view_link(obj, 'See All', query)
    all_link.short_description = ''

    def details_link(self, obj):
        if not obj.pk:
            return None
        return get_change_view_link(obj, 'Details')
    details_link.short_description = ''

    def image_preview(self, obj):
        if not obj or not obj.pk or not obj.link:
            return None

        return get_image_preview(obj.link)
    image_preview.short_description = ''

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'product':
            formfield.choices = formfield.choices
        return formfield

    def get_queryset(self, request):
        return super().get_queryset(request).with_admin_data()

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if not request.user.is_superuser:
            readonly_fields += [
                'image_id',
                'src'
            ]
        return readonly_fields


class ShopifyProductOptionsTabularInline(TabularInline):
    model = ShopifyOption
    fk_name = 'product'
    verbose_name_plural = 'options'
    all_link_query = 'product__id__exact'
    extra = 0
    classes = (
        'collapse',
    )

    fields = (
        'all_link',
        'details_link',
        'id',
        'option_id',
        'product',
        'name',
        'values'
    )

    readonly_fields = (
        'id',
        'all_link',
        'details_link'
    )

    def get_rel_obj(self, obj):
        return getattr(obj, self.fk_name)

    def all_link(self, obj):
        if not obj or not obj.pk:
            return None

        query = f'{self.all_link_query}={getattr(self.get_rel_obj(obj), "pk")}'
        return get_changelist_view_link(obj, 'See All', query)
    all_link.short_description = ''

    def details_link(self, obj):
        if not obj or not obj.pk:
            return None

        return get_change_view_link(obj, 'Details')
    details_link.short_description = ''

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'product':
            formfield.choices = formfield.choices
        return formfield

    def get_queryset(self, request):
        return super().get_queryset(request).with_admin_data()

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if not request.user.is_superuser:
            readonly_fields += (
                'option_id',
            )
        return readonly_fields


class ShopifyProductVariantsStackedInline(StackedInline):
    model = ShopifyVariant
    verbose_name_plural = 'variants'
    extra = 0

    fieldsets = (
        (
            None, {
                'fields': (
                    'details_link',
                    'variant_id',
                    'title',
                    'sku',
                    'barcode'
                )
            }
        ),
        (
            'Weight', {
                'fields': (
                    'grams',
                    'weight',
                    'weight_unit'
                )
            }
        ),
        (
            'Pricing', {
                'fields': (
                    'cost',
                    'price',
                    'compare_at_price'
                )
            }
        ),
        (
            'Taxes', {
                'fields': (
                    'is_taxable',
                    'tax_code'
                )
            }
        ),
        (
            'Inventory & Fulfillment', {
                'fields': (
                    'inventory_management',
                    'inventory_policy',
                    'fulfillment_service'
                )
            }
        )
    )

    readonly_fields = (
        'details_link',
    )

    def details_link(self, obj):
        if not obj or not obj.pk:
            return None

        return get_change_view_link(obj, 'See Full Variant')
    details_link.short_description = ''

    def get_queryset(self, request):
        return super().get_queryset(request).with_admin_data()

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if not request.user.is_superuser:
            readonly_fields += (
                'variant_id',
            )
        return readonly_fields


class ShopifyProductCalculatorStackedInline(StackedInline):
    model = ShopifyProductCalculator
    verbose_name_plural = 'calculator'
    extra = 0
    classes = (
        'collapse',
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    'details_link',
                    ('title_match', 'title_difference'),
                    'title_option',
                    ('body_html_match', 'body_html_difference'),
                    'body_html_option',
                    ('variant_weight_match', 'variant_weight_difference'),
                    'variant_weight_option',
                    ('variant_weight_unit_match', 'variant_weight_unit_difference'),
                    'variant_weight_unit_option',
                    ('variant_cost_match', 'variant_cost_difference'),
                    'variant_cost_option',
                    ('variant_price_match', 'variant_price_difference'),
                    'variant_price_base_option',
                    'variant_price_markup_option',
                    ('variant_sku_match', 'variant_sku_difference'),
                    'variant_sku_option',
                    ('variant_barcode_match', 'variant_barcode_difference'),
                    'variant_barcode_option',
                    ('metafields_match', 'metafields_difference'),
                    'metafields_packaging_option',
                    'metafields_fitments_option',
                    ('tags_match', 'tags_difference'),
                    'tags_vendor_option',
                    'tags_categories_option',
                    ('images_match', 'images_difference'),
                    'images_option'
                )
            }
        ),
    )

    readonly_fields = (
        'details_link',
        'title_match',
        'body_html_match',
        'variant_weight_match',
        'variant_weight_unit_match',
        'variant_cost_match',
        'variant_price_match',
        'variant_sku_match',
        'variant_barcode_match',
        'metafields_match',
        'tags_match',
        'images_match',
        'title_difference',
        'body_html_difference',
        'variant_weight_difference',
        'variant_weight_unit_difference',
        'variant_cost_difference',
        'variant_price_difference',
        'variant_sku_difference',
        'variant_barcode_difference',
        'metafields_difference',
        'tags_difference',
        'images_difference'
    )

    def details_link(self, obj):
        if not obj:
            return None
        return get_change_view_link(obj, 'See Full Calculator')
    details_link.short_description = ''

    def get_queryset(self, request):
        return super().get_queryset(request).with_admin_data()


class ShopifyProductMetafieldsTabularInline(ShopifyMetafieldBaseTabularInline):
    pass


class ShopifyProductTagsManyToManyTabularInline(TabularInline):
    model = ShopifyProduct.tags.through
    verbose_name_plural = 'tags'
    fk_name = 'shopifyproduct'
    extra = 0
    classes = (
        'collapse',
    )


class ShopifyCollectionCalculatorStackedInline(StackedInline):
    model = ShopifyCollectionCalculator
    verbose_name_plural = 'calculator'
    extra = 0
    classes = (
        'collapse',
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    'details_link',
                    ('title_match', 'title_difference'),
                    'title_option',
                    ('metafields_match', 'metafields_difference'),
                    'metafields_display_name_option',
                    'metafields_subcollections_option',
                    ('tags_match', 'tags_difference'),
                    'tags_categories_option'
                )
            }
        ),
    )

    readonly_fields = (
        'details_link',
        'title_match',
        'metafields_match',
        'tags_match',
        'title_difference',
        'metafields_difference',
        'tags_difference'
    )

    def details_link(self, obj):
        if not obj:
            return None
        return get_change_view_link(obj, 'See Full Calculator')
    details_link.short_description = ''

    def get_queryset(self, request):
        return super().get_queryset(request).with_admin_data()


class ShopifyCollectionChildCollectionsTabularInline(TabularInline):
    model = ShopifyCollection
    fk_name = 'parent_collection'
    verbose_name_plural = 'child collections'
    all_link_query = 'parent_collection__id__exact'
    extra = 0
    classes = (
        'collapse',
    )

    fields = (
        'all_link',
        'details_link',
        'id',
        'collection_id',
        'title',
        'handle',
        'level',
        'is_published',
        'tag_count',
        'metafield_count',
        'rule_count',
        'child_collection_count',
        'errors',
        'full_match'
    )

    readonly_fields = (
        'id',
        'level',
        'errors',
        'full_match',
        'details_link',
        'all_link',
        'rule_count',
        'tag_count',
        'metafield_count',
        'child_collection_count'
    )

    def get_rel_obj(self, obj):
        return getattr(obj, self.fk_name)

    def all_link(self, obj):
        query = f'{self.all_link_query}={getattr(self.get_rel_obj(obj), "pk")}'
        return get_changelist_view_link(obj, 'See All', query)
    all_link.short_description = ''

    def details_link(self, obj):
        if not obj.pk:
            return None
        return get_change_view_link(obj, 'Details')
    details_link.short_description = ''

    def rule_count(self, obj):
        if not obj or not obj.pk:
            return None

        return obj._rule_count
    rule_count.admin_order_field = '_rule_count'
    rule_count.short_description = 'rule count'

    def tag_count(self, obj):
        if not obj or not obj.pk:
            return None

        return obj._tag_count
    tag_count.admin_order_field = '_tag_count'
    tag_count.short_description = 'tag count'

    def metafield_count(self, obj):
        if not obj or not obj.pk:
            return None

        return obj._metafield_count
    metafield_count.admin_order_field = '_metafield_count'
    metafield_count.short_description = 'metafield count'

    def child_collection_count(self, obj):
        if not obj or not obj.pk:
            return None

        return (
            f'{obj._child_collection_published_count}'
            f'/{obj._child_collection_count}'
        )
    child_collection_count.admin_order_field = (
        '_child_collection_published_count'
    )
    child_collection_count.short_description = 'child count'

    def full_match(self, obj):
        if not obj or not obj.pk or not hasattr(obj, 'calculator'):
            return None

        return obj.calculator.full_match()
    full_match.boolean = True
    full_match.short_description = 'calculated'

    def get_queryset(self, request):
        return super().get_queryset(request).with_admin_data()

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if not request.user.is_superuser:
            readonly_fields += (
                'collection_id',
                'handle'
            )
        return readonly_fields


class ShopifyCollectionTagsManyToManyTabularInline(TabularInline):
    model = ShopifyCollection.tags.through
    verbose_name_plural = 'tags'
    fk_name = 'shopifycollection'
    extra = 0
    classes = (
        'collapse',
    )


class ShopifyCollectionRulesManyToManyTabularInline(TabularInline):
    model = ShopifyCollection.rules.through
    verbose_name_plural = 'rules'
    fk_name = 'shopifycollection'
    extra = 0
    classes = (
        'collapse',
    )


class ShopifyCollectionMetafieldsTabularInline(ShopifyMetafieldBaseTabularInline):
    pass


class ShopifyTagProductsManyToManyTabularInline(TabularInline):
    model = ShopifyProduct.tags.through
    verbose_name_plural = 'products'
    fk_name = 'shopifytag'
    extra = 0
    classes = (
        'collapse',
    )


class ShopifyTagCollectionsManyToManyTabularInline(TabularInline):
    model = ShopifyCollection.tags.through
    verbose_name_plural = 'collections'
    fk_name = 'shopifytag'
    extra = 0
    classes = (
        'collapse',
    )


class ShopifyRuleCollectionsManyToManyTabularInline(TabularInline):
    model = ShopifyCollection.rules.through
    verbose_name_plural = 'collections'
    fk_name = 'shopifycollectionrule'
    extra = 0
    classes = (
        'collapse',
    )
