from django.contrib.admin import (
    StackedInline,
    TabularInline
)
from django.contrib.contenttypes.admin import GenericTabularInline
from django.db.models import CharField, TextField
from django.forms import TextInput, Textarea

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
        'detail_link',
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
        'detail_link',
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
        return get_changelist_view_link(obj._meta.model, 'See All', query)
    all_link.short_description = ''

    def detail_link(self, obj):
        if not obj or not obj.pk:
            return None

        return get_change_view_link(obj, 'Details')
    detail_link.short_description = ''

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
        'detail_link',
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
        'detail_link',
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
        return get_changelist_view_link(obj._meta.model, 'See All', query)
    all_link.short_description = ''

    def detail_link(self, obj):
        if not obj:
            return None
        return get_change_view_link(obj, 'Details')
    detail_link.short_description = ''

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
        'detail_link',
        'id',
        'image_id',
        'product',
        'link',
        'image_preview'
    )

    readonly_fields = (
        'id',
        'image_preview',
        'detail_link',
        'all_link'
    )

    def get_rel_obj(self, obj):
        return getattr(obj, self.fk_name)

    def all_link(self, obj):
        query = f'{self.all_link_query}={getattr(self.get_rel_obj(obj), "pk")}'
        return get_changelist_view_link(obj._meta.model, 'See All', query)
    all_link.short_description = ''

    def detail_link(self, obj):
        if not obj.pk:
            return None
        return get_change_view_link(obj, 'Details')
    detail_link.short_description = ''

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
        'detail_link',
        'id',
        'option_id',
        'product',
        'name',
        'values'
    )

    readonly_fields = (
        'id',
        'all_link',
        'detail_link'
    )

    def get_rel_obj(self, obj):
        return getattr(obj, self.fk_name)

    def all_link(self, obj):
        if not obj or not obj.pk:
            return None

        query = f'{self.all_link_query}={getattr(self.get_rel_obj(obj), "pk")}'
        return get_changelist_view_link(obj._meta.model, 'See All', query)
    all_link.short_description = ''

    def detail_link(self, obj):
        if not obj or not obj.pk:
            return None

        return get_change_view_link(obj, 'Details')
    detail_link.short_description = ''

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
                    'detail_link',
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
        'detail_link',
    )

    def detail_link(self, obj):
        if not obj or not obj.pk:
            return None

        return get_change_view_link(obj, 'See Full Variant')
    detail_link.short_description = ''

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
                    'detail_link',
                )
            }
        ),
        (
            'Title', {
                'fields': (
                    'title_match',
                    'title_current_preview',
                    'title_result_preview',
                    'title_choice',
                    'title_custom_value'
                )
            }
        ),
        (
            'Body HTML', {
                'fields': (
                    'body_html_match',
                    'body_html_current_preview',
                    'body_html_result_preview',
                    'body_html_choice',
                    'body_html_custom_value'
                )
            }
        ),
        (
            'Variant Weight', {
                'fields': (
                    'variant_weight_match',
                    'variant_weight_current_preview',
                    'variant_weight_result_preview',
                    'variant_weight_choice',
                    'variant_weight_custom_value'
                )
            }
        ),
        (
            'Variant Weight Unit', {
                'fields': (
                    'variant_weight_unit_match',
                    'variant_weight_unit_current_preview',
                    'variant_weight_unit_result_preview',
                    'variant_weight_unit_choice'
                )
            }
        ),
        (
            'Variant Cost', {
                'fields': (
                    'variant_cost_match',
                    'variant_cost_current_preview',
                    'variant_cost_result_preview',
                    'variant_cost_custom_value'
                )
            }
        ),
        (
            'Variant Price', {
                'fields': (
                    'variant_price_match',
                    'variant_price_current_preview',
                    'variant_price_result_preview',
                    'variant_price_base_choice',
                    'variant_price_base_custom_value',
                    'variant_price_markup_choice'
                )
            }
        ),
        (
            'Variant SKU', {
                'fields': (
                    'variant_sku_match',
                    'variant_sku_current_preview',
                    'variant_sku_result_preview',
                    'variant_sku_choice',
                    'variant_sku_custom_value'
                )
            }
        ),
        (
            'Variant Barcode', {
                'fields': (
                    'variant_barcode_match',
                    'variant_barcode_current_preview',
                    'variant_barcode_result_preview',
                    'variant_barcode_choice',
                    'variant_barcode_custom_value'
                )
            }
        ),
        (
            'Metafields', {
                'fields': (
                    'metafields_match',
                    'metafields_difference',
                    'metafield_value_packaging_choice',
                    'metafield_value_packaging_custom_value',
                    'metafield_value_fitments_choice',
                    'metafield_value_fitments_custom_value',
                    'metafields_choice',
                    'metafields_custom_value'
                )
            }
        ),
        (
            'Tags', {
                'fields': (
                    'tags_match',
                    'tags_difference',
                    'tag_names_vendor_choice',
                    'tag_names_vendor_custom_value',
                    'tag_names_collection_choice',
                    'tag_names_collection_custom_value',
                    'tags_choice',
                    'tags_custom_value'
                )
            }
        ),
        (
            'Images', {
                'fields': (
                    'images_match',
                    'images_difference',
                    'image_urls_sema_choice',
                    'image_urls_sema_custom_value',
                    'image_urls_premier_choice',
                    'image_urls_premier_custom_value',
                    'images_choice',
                    'images_custom_value'
                )
            }
        ),
    )

    readonly_fields = (
        'detail_link',
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
        'title_current_preview',
        'title_result_preview',
        'body_html_current_preview',
        'body_html_result_preview',
        'variant_weight_current_preview',
        'variant_weight_result_preview',
        'variant_weight_unit_current_preview',
        'variant_weight_unit_result_preview',
        'variant_cost_current_preview',
        'variant_cost_result_preview',
        'variant_price_current_preview',
        'variant_price_result_preview',
        'variant_sku_current_preview',
        'variant_sku_result_preview',
        'variant_barcode_current_preview',
        'variant_barcode_result_preview',
        'metafields_difference',
        'tags_difference',
        'images_difference'
    )

    formfield_overrides = {
        CharField: {'widget': TextInput(attrs={'size': '40'})},
        TextField: {'widget': Textarea(attrs={'rows': 3, 'cols': 40})},
    }

    def detail_link(self, obj):
        if not obj:
            return None
        return get_change_view_link(obj, 'See Full Calculator')
    detail_link.short_description = ''

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
                    'detail_link',
                )
            }
        ),
        (
            'Title', {
                'fields': (
                    'title_match',
                    'title_current_preview',
                    'title_result_preview',
                    'title_choice',
                    'title_custom_value'
                )
            }
        ),
        (
            'Metafields', {
                'fields': (
                    'metafields_match',
                    'metafields_difference',
                    'metafield_value_display_name_choice',
                    'metafield_value_display_name_custom_value',
                    'metafield_value_collection_family_choice',
                    'metafield_value_collection_family_custom_value',
                    'metafields_choice',
                    'metafields_custom_value'
                )
            }
        ),
        (
            'Tags', {
                'fields': (
                    'tags_match',
                    'tags_difference',
                    'tag_names_collection_choice',
                    'tag_names_collection_custom_value',
                    'tags_choice',
                    'tags_custom_value'
                )
            }
        ),
    )

    readonly_fields = (
        'title_match',
        'tags_match',
        'metafields_match',
        'title_current_preview',
        'title_result_preview',
        'metafields_difference',
        'tags_difference',
        'detail_link'
    )

    formfield_overrides = {
        CharField: {'widget': TextInput(attrs={'size': '40'})},
        TextField: {'widget': Textarea(attrs={'rows': 3, 'cols': 40})},
    }

    def detail_link(self, obj):
        if not obj:
            return None
        return get_change_view_link(obj, 'See Full Calculator')
    detail_link.short_description = ''

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
        'detail_link',
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
        'detail_link',
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
        return get_changelist_view_link(obj._meta.model, 'See All', query)
    all_link.short_description = ''

    def detail_link(self, obj):
        if not obj.pk:
            return None
        return get_change_view_link(obj, 'Details')
    detail_link.short_description = ''

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
