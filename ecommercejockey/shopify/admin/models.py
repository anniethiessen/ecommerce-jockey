from django_object_actions import BaseDjangoObjectActions as ObjectActions

from django.contrib import admin
from django.contrib.admin import ModelAdmin

from core.admin.utils import (
    get_change_view_link,
)
from ..models import (
    ShopifyCollection,
    ShopifyCollectionCalculator,
    ShopifyCollectionRule,
    ShopifyImage,
    ShopifyMetafield,
    ShopifyOption,
    ShopifyProduct,
    ShopifyProductCalculator,
    ShopifyTag,
    ShopifyVariant,
    ShopifyVendor
)
from .actions import (
    ShopifyCollectionActions,
    ShopifyCollectionCalculatorActions,
    ShopifyCollectionRuleActions,
    ShopifyImageActions,
    ShopifyMetafieldActions,
    ShopifyOptionActions,
    ShopifyProductActions,
    ShopifyProductCalculatorActions,
    ShopifyTagActions,
    ShopifyVariantActions,
    ShopifyVendorActions
)
from .filters import ByCollectionLevel
from .inlines import (
    ShopifyCollectionCalculatorStackedInline,
    ShopifyCollectionMetafieldsTabularInline,
    ShopifyCollectionRulesManyToManyTabularInline,
    ShopifyCollectionTagsManyToManyTabularInline,
    ShopifyProductCalculatorStackedInline,
    ShopifyProductImagesTabularInline,
    ShopifyProductMetafieldsTabularInline,
    ShopifyProductOptionsTabularInline,
    ShopifyProductTagsManyToManyTabularInline,
    ShopifyProductVariantsStackedInline,
    ShopifyRuleCollectionsManyToManyTabularInline,
    ShopifyTagCollectionsManyToManyTabularInline,
    ShopifyTagProductsManyToManyTabularInline,
    ShopifyVendorProductsTabularInline
)


@admin.register(ShopifyVendor)
class ShopifyVendorModelAdmin(ObjectActions, ModelAdmin, ShopifyVendorActions):
    search_fields = (
        'id',
        'name'
    )

    list_display = (
        'details_link',
        'id',
        'name',
        'product_count_a'
    )

    list_display_links = (
        'details_link',
    )

    fieldsets = (
        (
            'Vendor', {
                'fields': (
                    'id',
                    'name'
                )
            }
        ),
    )

    readonly_fields = (
        'id',
        'product_count_a'
    )

    inlines = (
        ShopifyVendorProductsTabularInline,
    )

    def details_link(self, obj):
        if not obj:
            return None
        return get_change_view_link(obj, 'Details')
    details_link.short_description = ''

    def product_count_a(self, obj):
        return f'{obj.product_published_count}/{obj.product_count}'
    product_count_a.short_description = 'product_count'

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return ()
        return super().get_inline_instances(request, obj)


@admin.register(ShopifyCollection)
class ShopifyCollectionModelAdmin(ObjectActions, ModelAdmin,
                                  ShopifyCollectionActions):
    actions = (
        'update_calculated_fields_queryset_action',
        'import_from_api_queryset_action',
        'export_to_api_queryset_action',
        'mark_as_published_queryset_action',
        'mark_as_unpublished_queryset_action'
    )

    change_actions = (
        'update_calculated_fields_object_action',
        'export_to_api_object_action',
        'import_from_api_object_action'
    )

    search_fields = (
        'id',
        'collection_id',
        'title',
        'handle',
        'body_html'
    )

    list_display = (
        'details_link',
        'id',
        'collection_id',
        'title',
        'handle',
        'tag_count',
        'rule_count',
        'is_published',
        'errors',
        'full_match'
    )

    list_display_links = (
        'details_link',
    )

    list_editable = (
        'is_published',
    )

    list_filter = (
        'is_published',
        ByCollectionLevel,
        'published_scope',
        'disjunctive',
        'sort_order',
        'tags'
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    'errors',
                )
            }
        ),
        (
            'Collection', {
                'fields': (
                    'id',
                    'collection_id',
                    'title',
                    'handle',
                    'is_published',
                    'published_scope',
                    'disjunctive',
                    'sort_order',
                    'body_html'
                )
            }
        ),
        (
            'Parent Collection', {
                'fields': (
                    'parent_collection',
                )
            }
        ),
        (
            'Image', {
                'fields': (
                    'image_src',
                    'image_alt'
                )
            }
        )
    )

    readonly_fields = (
        'id',
        'tag_count',
        'rule_count',
        'errors',
        'full_match',
        'details_link'
    )

    autocomplete_fields = (
        'parent_collection',
    )

    inlines = (
        ShopifyCollectionRulesManyToManyTabularInline,
        ShopifyCollectionTagsManyToManyTabularInline,
        ShopifyCollectionMetafieldsTabularInline,
        ShopifyCollectionCalculatorStackedInline
    )

    def details_link(self, obj):
        if not obj:
            return None
        return get_change_view_link(obj, 'Details')
    details_link.short_description = ''

    def full_match(self, obj):
        return obj.calculator.full_match()
    full_match.boolean = True
    full_match.short_description = 'calculated'

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if not request.user.is_superuser:
            readonly_fields += (
                'collection_id',
                'handle'
            )
        return readonly_fields

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return ()
        return super().get_inline_instances(request, obj)


@admin.register(ShopifyCollectionRule)
class ShopifyCollectionRuleModelAdmin(ObjectActions, ModelAdmin,
                                      ShopifyCollectionRuleActions):
    search_fields = (
        'id',
        'column',
        'relation',
        'condition'
    )

    list_display = (
        'details_link',
        'id',
        'column',
        'relation',
        'condition'
    )

    list_display_links = (
        'details_link',
    )

    list_filter = (
        'column',
        'relation',
        'condition'
    )

    fieldsets = (
        (
            'Rule', {
                'fields': (
                    'id',
                    'column',
                    'relation',
                    'condition'
                )
            }
        ),
    )

    readonly_fields = (
        'id',
        'details_link'
    )

    inlines = (
        ShopifyRuleCollectionsManyToManyTabularInline,
    )

    def details_link(self, obj):
        if not obj:
            return None
        return get_change_view_link(obj, 'Details')
    details_link.short_description = ''

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return ()
        return super().get_inline_instances(request, obj)


@admin.register(ShopifyTag)
class ShopifyTagModelAdmin(ObjectActions, ModelAdmin, ShopifyTagActions):
    search_fields = (
        'id',
        'name'
    )

    list_display = (
        'details_link',
        'id',
        'name'
    )

    list_display_links = (
        'details_link',
    )

    fieldsets = (
        (
            'Tag', {
                'fields': (
                    'id',
                    'name'
                )
            }
        ),
    )

    readonly_fields = (
        'id',
        'details_link'
    )

    inlines = (
        ShopifyTagCollectionsManyToManyTabularInline,
        ShopifyTagProductsManyToManyTabularInline
    )

    def details_link(self, obj):
        if not obj:
            return None
        return get_change_view_link(obj, 'Details')
    details_link.short_description = ''

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return ()
        return super().get_inline_instances(request, obj)


@admin.register(ShopifyProduct)
class ShopifyProductModelAdmin(ObjectActions, ModelAdmin,
                               ShopifyProductActions):
    actions = (
        'update_calculated_fields_queryset_action',
        'export_to_api_queryset_action',
        'import_from_api_queryset_action',
        'mark_as_published_queryset_action',
        'mark_as_unpublished_queryset_action'
    )

    change_actions = (
        'update_calculated_fields_object_action',
        'export_to_api_object_action',
        'import_from_api_object_action'
    )

    list_select_related = (
        'vendor',
        'calculator'
    )

    search_fields = (
        'id',
        'product_id',
        'title',
        'body_html',
        'vendor__name',
        'seo_title',
        'seo_description'
    )

    list_display = (
        'details_link',
        'id',
        'product_id',
        'title',
        'body_html',
        'vendor',
        'is_published',
        'errors',
        'full_match'
    )

    list_display_links = (
        'details_link',
    )

    list_editable = (
        'is_published',
    )

    list_filter = (
        'is_published',
        'product_type',
        'vendor',
        'published_scope',
        'tags'
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    'errors',
                )
            }
        ),
        (
            'Product', {
                'fields': (
                    'item_link',
                    'premier_product_link',
                    'sema_product_link',
                    'id',
                    'product_id',
                    'product_type',
                    'title',
                    'is_published',
                    'published_scope',
                    'body_html'
                )
            }
        ),
        (
            'Vendor', {
                'fields': (
                    'vendor_link',
                    'vendor'
                )
            }
        ),
        (
            'SEO', {
                'fields': (
                    'seo_title',
                    'seo_description'
                )
            }
        )
    )

    readonly_fields = (
        'id',
        'errors',
        'details_link',
        'item_link',
        'premier_product_link',
        'sema_product_link',
        'vendor_link',
        'full_match'
    )

    autocomplete_fields = (
        'vendor',
    )

    inlines = (
        ShopifyProductVariantsStackedInline,
        ShopifyProductMetafieldsTabularInline,
        ShopifyProductImagesTabularInline,
        ShopifyProductOptionsTabularInline,
        ShopifyProductTagsManyToManyTabularInline,
        ShopifyProductCalculatorStackedInline
    )

    def details_link(self, obj):
        if not obj:
            return None
        return get_change_view_link(obj, 'Details')
    details_link.short_description = ''

    def item_link(self, obj):
        if not hasattr(obj, 'item'):
            return '-----'
        return get_change_view_link(obj.item, 'See full item')
    item_link.short_description = ''

    def premier_product_link(self, obj):
        if not hasattr(obj, 'item') or not obj.item.premier_product:
            return '-----'
        return get_change_view_link(
            obj.item.premier_product,
            'See Premier product'
        )
    premier_product_link.short_description = ''

    def sema_product_link(self, obj):
        if not hasattr(obj, 'item') or not obj.item.sema_product:
            return '-----'
        return get_change_view_link(
            obj.item.sema_product,
            'See SEMA product'
        )
    sema_product_link.short_description = ''

    def vendor_link(self, obj):
        if not obj.vendor:
            return None
        return get_change_view_link(obj.vendor, 'See full vendor')
    vendor_link.short_description = ''

    def full_match(self, obj):
        return obj.calculator.full_match()
    full_match.boolean = True
    full_match.short_description = 'calculated'

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if not request.user.is_superuser:
            readonly_fields += (
                'product_id',
            )
        return readonly_fields

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return ()
        return super().get_inline_instances(request, obj)


@admin.register(ShopifyImage)
class ShopifyImageModelAdmin(ObjectActions, ModelAdmin, ShopifyImageActions):
    actions = (
        'export_to_api_queryset_action',
        'import_from_api_queryset_action'
    )

    change_actions = (
        'export_to_api_object_action',
        'import_from_api_object_action'
    )

    list_select_related = (
        'product',
    )

    search_fields = (
        'product__id',
        'product__product_id',
        'product__title',
        'product__product_html',
        'product__vendor__name',
        'product__seo_title',
        'product__seo_description',
        'id',
        'link',
        'src'
    )

    list_display = (
        'details_link',
        'id',
        'image_id',
        'product',
        'link',
        'src'
    )

    list_display_links = (
        'details_link',
    )

    fieldsets = (
        (
            'Image', {
                'fields': (
                    'id',
                    'image_id',
                    'link',
                    'src'
                )
            }
        ),
        (
            'Product', {
                'fields': (
                    'product_link',
                    'product'
                )
            }
        )
    )

    readonly_fields = (
        'id',
        'details_link',
        'product_link'
    )

    autocomplete_fields = (
        'product',
    )

    def details_link(self, obj):
        if not obj:
            return None
        return get_change_view_link(obj, 'Details')
    details_link.short_description = ''

    def product_link(self, obj):
        if not obj.product:
            return None
        return get_change_view_link(obj.product, 'See full product')
    product_link.short_description = ''

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if not request.user.is_superuser:
            readonly_fields += [
                'image_id',
                'src'
            ]
        return readonly_fields


@admin.register(ShopifyOption)
class ShopifyOptionModelAdmin(ObjectActions, ModelAdmin, ShopifyOptionActions):
    list_select_related = (
        'product',
    )

    search_fields = (
        'product__id',
        'product__product_id',
        'product__title',
        'product__product_html',
        'product__vendor__name',
        'product__seo_title',
        'product__seo_description',
        'id',
        'option_id',
        'name',
        'values'
    )

    list_display = (
        'details_link',
        'id',
        'option_id',
        'product',
        'name',
        'values'
    )

    list_display_links = (
        'details_link',
    )

    fieldsets = (
        (
            'Option', {
                'fields': (
                    'id',
                    'option_id',
                    'name',
                    'values'
                )
            }
        ),
        (
            'Product', {
                'fields': (
                    'product_link',
                    'product'
                )
            }
        )
    )

    readonly_fields = (
        'id',
        'details_link',
        'product_link'
    )

    autocomplete_fields = (
        'product',
    )

    def details_link(self, obj):
        if not obj:
            return None
        return get_change_view_link(obj, 'Details')
    details_link.short_description = ''

    def product_link(self, obj):
        if not obj.product:
            return None
        return get_change_view_link(obj.product, 'See full product')
    product_link.short_description = ''

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if not request.user.is_superuser:
            readonly_fields += (
                'option_id',
            )
        return readonly_fields


@admin.register(ShopifyVariant)
class ShopifyVariantModelAdmin(ObjectActions, ModelAdmin,
                               ShopifyVariantActions):
    list_select_related = (
        'product',
    )

    search_fields = (
        'product__id',
        'product__product_id',
        'product__title',
        'product__body_html',
        'product__vendor__name',
        'product__seo_title',
        'product__seo_description',
        'id',
        'variant_id',
        'title',
        'sku',
        'barcode'
    )

    list_display = (
        'details_link',
        'id',
        'variant_id',
        'product',
        'title'
    )

    list_display_links = (
        'details_link',
    )

    fieldsets = (
        (
            'Variant', {
                'fields': (
                    'id',
                    'variant_id',
                    'title',
                    'sku',
                    'barcode'
                )
            }
        ),
        (
            'Product', {
                'fields': (
                    'product_link',
                    'product'
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
                    'price',
                    'compare_at_price',
                    'cost',
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
        'id',
        'details_link',
        'product_link'
    )

    autocomplete_fields = (
        'product',
    )

    def details_link(self, obj):
        if not obj:
            return None
        return get_change_view_link(obj, 'Details')
    details_link.short_description = ''

    def product_link(self, obj):
        if not obj.product:
            return None
        return get_change_view_link(obj.product, 'See full product')
    product_link.short_description = ''

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if not request.user.is_superuser:
            readonly_fields += (
                'variant_id',
            )
        return readonly_fields


@admin.register(ShopifyMetafield)
class ShopifyMetafieldModelAdmin(ObjectActions, ModelAdmin,
                                 ShopifyMetafieldActions):
    list_select_related = (
        'content_type',
    )

    search_fields = (
        'product__id',
        'product__product_id',
        'product__title',
        'product__body_html',
        'product__vendor__name',
        'product__seo_title',
        'product__seo_description',
        'collection__id',
        'collection__collection_id',
        'collection__title',
        'collection__body_html',
        'id',
        'metafield_id',
        'value'
    )

    list_display = (
        'details_link',
        'id',
        'metafield_id',
        'content_object',
        'namespace',
        'key',
        'value_type'
    )

    list_display_links = (
        'details_link',
    )

    list_filter = (
        'owner_resource',
        'namespace',
        'key',
        'value_type'
    )

    fieldsets = (
        (
            'Metafield', {
                'fields': (
                    'id',
                    'metafield_id',
                    'owner_resource',
                    'namespace',
                    'value_type',
                    'key',
                    'value'
                )
            }
        ),
        (
            'Related Object', {
                'fields': (
                    'content_object_link',
                    'content_object_a',
                    'content_type',
                    'object_id'
                )
            }
        )
    )

    readonly_fields = (
        'id',
        'details_link',
        'content_object_link',
        'content_object_a'
    )

    def details_link(self, obj):
        if not obj:
            return None
        return get_change_view_link(obj, 'Details')
    details_link.short_description = ''

    def content_object_a(self, obj):
        if not obj.content_object:
            return '----'
        return str(obj.content_object)
    content_object_a.short_description = ''

    def content_object_link(self, obj):
        if not obj.content_object:
            return None
        return get_change_view_link(obj.content_object, 'See full object')
    content_object_link.short_description = ''

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if not request.user.is_superuser:
            readonly_fields += (
                'metafield_id',
            )
        return readonly_fields


@admin.register(ShopifyProductCalculator)
class ShopifyProductCalculatorModelAdmin(ObjectActions, ModelAdmin,
                                         ShopifyProductCalculatorActions):
    actions = (
        'update_calculated_fields_queryset_action',
    )

    change_actions = (
        'update_calculated_fields_object_action',
    )

    list_select_related = (
        'product',
    )

    search_fields = (
        'product__id',
        'product__product_id',
        'product__title',
        'product__body_html',
        'product__vendor__name',
        'product__seo_title',
        'product__seo_description'
    )

    list_display = (
        'details_link',
        'product',
        'full_match',
        'sema_description_def_preview',
        'sema_description_des_preview',
        'sema_description_inv_preview',
        'sema_description_ext_preview',
        'sema_description_tle_preview',
        'sema_description_sho_preview',
        'sema_description_asc_preview',
        'sema_description_mkt_preview',
        'premier_description_preview',
        'title_option',
        'body_html_option',
        'premier_cost_cad_preview',
        'variant_price_markup_option',
        'sema_images_preview',
        'premier_images_preview',
        'images_option'
    )

    list_display_links = (
        'details_link',
    )

    list_editable = (
        'title_option',
        'body_html_option',
        'variant_price_markup_option',
        'images_option'
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    'item_link',
                    'shopify_product_link',
                    'premier_product_link',
                    'sema_product_link'
                )
            }
        ),
        (
            'Text Previews', {
                'fields': (
                    'sema_description_def_preview',
                    'sema_description_des_preview',
                    'sema_description_inv_preview',
                    'sema_description_ext_preview',
                    'sema_description_tle_preview',
                    'sema_description_sho_preview',
                    'sema_description_asc_preview',
                    'sema_description_mkt_preview',
                    'premier_description_preview'
                ),
                'classes': (
                    'collapse',
                )
            }
        ),
        (
            'Title', {
                'fields': (
                    ('title_match', 'title_difference'),
                    'title_option'
                )
            }
        ),
        (
            'Body HTML', {
                'fields': (
                    ('body_html_match', 'body_html_difference'),
                    'body_html_option'
                )
            }
        ),
        (
            'Weight Previews', {
                'fields': (
                    'premier_weight_preview',
                ),
                'classes': (
                    'collapse',
                )
            }
        ),
        (
            'Variant Weight', {
                'fields': (
                    ('variant_weight_match', 'variant_weight_difference'),
                    'variant_weight_option'
                )
            }
        ),
        (
            'Variant Weight Unit', {
                'fields': (
                    ('variant_weight_unit_match',
                     'variant_weight_unit_difference'),
                    'variant_weight_unit_option'
                )
            }
        ),
        (
            'Cost Previews', {
                'fields': (
                    'premier_cost_cad_preview',
                    'premier_cost_usd_preview'
                ),
                'classes': (
                    'collapse',
                )
            }
        ),
        (
            'Variant Cost', {
                'fields': (
                    ('variant_cost_match', 'variant_cost_difference'),
                    'variant_cost_option'
                )
            }
        ),
        (
            'Variant Price', {
                'fields': (
                    ('variant_price_match', 'variant_price_difference'),
                    'variant_price_base_option',
                    'variant_price_markup_option'
                )
            }
        ),
        (
            'Identifier Previews', {
                'fields': (
                    'premier_premier_part_number_preview',
                    'premier_upc_preview'
                ),
                'classes': (
                    'collapse',
                )
            }
        ),
        (
            'Variant SKU', {
                'fields': (
                    ('variant_sku_match', 'variant_sku_difference'),
                    'variant_sku_option'
                )
            }
        ),
        (
            'Variant Barcode', {
                'fields': (
                    ('variant_barcode_match', 'variant_barcode_difference'),
                    'variant_barcode_option'
                )
            }
        ),
        (
            'Metafield Previews', {
                'fields': (
                    'sema_html_packaging_preview',
                    'sema_vehicle_fitments_preview'
                ),
                'classes': (
                    'collapse',
                )
            }
        ),
        (
            'Metafields', {
                'fields': (
                    ('metafields_match', 'metafields_difference'),
                    'metafields_packaging_option',
                    'metafields_fitments_option'
                )
            }
        ),
        (
            'Tag Previews', {
                'fields': (
                    'sema_brand_tags_preview',
                    'sema_category_tags_preview'
                ),
                'classes': (
                    'collapse',
                )
            }
        ),
        (
            'Tags', {
                'fields': (
                    ('tags_match', 'tags_difference'),
                    'tags_vendor_option',
                    'tags_categories_option'
                )
            }
        ),
        (
            'Image Previews', {
                'fields': (
                    'sema_images_preview',
                    'premier_images_preview'
                ),
                'classes': (
                    'collapse',
                )
            }
        ),
        (
            'Images', {
                'fields': (
                    ('images_match', 'images_difference'),
                    'images_option'
                )
            }
        )
    )

    readonly_fields = (
        'item_link',
        'details_link',
        'shopify_product_link',
        'premier_product_link',
        'sema_product_link',
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
        'full_match',
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
        'images_difference',
        'sema_description_def_preview',
        'sema_description_des_preview',
        'sema_description_inv_preview',
        'sema_description_ext_preview',
        'sema_description_tle_preview',
        'sema_description_sho_preview',
        'sema_description_asc_preview',
        'sema_description_mkt_preview',
        'sema_html_packaging_preview',
        'sema_vehicle_fitments_preview',
        'sema_brand_tags_preview',
        'sema_category_tags_preview',
        'sema_images_preview',
        'premier_description_preview',
        'premier_weight_preview',
        'premier_cost_cad_preview',
        'premier_cost_usd_preview',
        'premier_premier_part_number_preview',
        'premier_upc_preview',
        'premier_images_preview'
    )

    def details_link(self, obj):
        if not obj:
            return None
        return get_change_view_link(obj, 'Details')
    details_link.short_description = ''

    def item_link(self, obj):
        if not hasattr(obj.product, 'item'):
            return '-----'
        return get_change_view_link(obj.product.item, 'See full item')
    item_link.short_description = ''

    def shopify_product_link(self, obj):
        if not obj.product:
            return '-----'
        return get_change_view_link(obj.product, 'See full Shopify Product')
    shopify_product_link.short_description = ''

    def premier_product_link(self, obj):
        if (not hasattr(obj.product, 'item')
                or not obj.product.item.premier_product):
            return '-----'
        return get_change_view_link(
            obj.product.item.premier_product,
            'See full Premier product'
        )
    premier_product_link.short_description = ''

    def sema_product_link(self, obj):
        if (not hasattr(obj.product, 'item')
                or not obj.product.item.sema_product):
            return '-----'
        return get_change_view_link(
            obj.product.item.sema_product,
            'See full SEMA product'
        )
    sema_product_link.short_description = ''


@admin.register(ShopifyCollectionCalculator)
class ShopifyCollectionCalculatorModelAdmin(ObjectActions, ModelAdmin,
                                            ShopifyCollectionCalculatorActions):
    actions = (
        'update_calculated_fields_queryset_action',
    )

    change_actions = (
        'update_calculated_fields_object_action',
    )

    list_select_related = (
        'collection',
    )

    search_fields = (
        'collection__id',
        'collection__collection_id',
        'collection__title',
        'collection__handle',
        'collection__body_html'
    )

    list_display = (
        'details_link',
        'id',
        'collection',
        'full_match'
    )

    list_display_links = (
        'details_link',
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    'shopify_collection_link',
                )
            }
        ),
        (
            'Text Previews', {
                'fields': (
                    'sema_category_chained_title_preview',
                ),
                'classes': (
                    'collapse',
                )
            }
        ),
        (
            'Title', {
                'fields': (
                    ('title_match', 'title_difference'),
                    'title_option'
                )
            }
        ),
        (
            'Metafield Previews', {
                'fields': (
                    'sema_category_display_name_preview',
                    'shopify_subcollections_preview'
                ),
                'classes': (
                    'collapse',
                )
            }
        ),
        (
            'Metafields', {
                'fields': (
                    ('metafields_match', 'metafields_difference'),
                    'metafields_display_name_option',
                    'metafields_subcollections_option'
                )
            }
        ),
        (
            'Tag Previews', {
                'fields': (
                    'sema_category_tags_preview',
                ),
                'classes': (
                    'collapse',
                )
            }
        ),
        (
            'Tags', {
                'fields': (
                    ('tags_match', 'tags_difference'),
                    'tags_categories_option'
                )
            }
        )
    )

    readonly_fields = (
        'shopify_collection_link',
        'details_link',
        'title_match',
        'metafields_match',
        'tags_match',
        'full_match',
        'title_difference',
        'metafields_difference',
        'tags_difference',
        'sema_category_chained_title_preview',
        'sema_category_display_name_preview',
        'shopify_subcollections_preview',
        'sema_category_tags_preview'
    )

    def details_link(self, obj):
        if not obj:
            return None
        return get_change_view_link(obj, 'Details')
    details_link.short_description = ''

    def shopify_collection_link(self, obj):
        if not obj.collection:
            return '-----'
        return get_change_view_link(obj.collection, 'See full Shopify Collection')
    shopify_collection_link.short_description = ''
