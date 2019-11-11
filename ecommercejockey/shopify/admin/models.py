from django_object_actions import BaseDjangoObjectActions as ObjectActions

from django.contrib import admin
from django.contrib.admin import ModelAdmin
# from django.utils.safestring import mark_safe

from core.admin.utils import (
    get_change_view_link,
    # get_image_preview
)
from ..models import (
    ShopifyCollection,
    ShopifyCollectionRule,
    ShopifyImage,
    ShopifyMetafield,
    ShopifyOption,
    ShopifyProduct,
    ShopifyTag,
    ShopifyVariant,
    ShopifyVendor
)
from .actions import (
    ShopifyCollectionActions,
    ShopifyCollectionRuleActions,
    ShopifyImageActions,
    ShopifyMetafieldActions,
    ShopifyOptionActions,
    ShopifyProductActions,
    ShopifyTagActions,
    ShopifyVariantActions,
    ShopifyVendorActions
)
from .inlines import (
    ShopifyCollectionRulesManyToManyTabularInline,
    ShopifyCollectionTagsManyToManyTabularInline,
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
        'name'
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
    )

    inlines = (
        ShopifyVendorProductsTabularInline,
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


@admin.register(ShopifyCollection)
class ShopifyCollectionModelAdmin(ObjectActions, ModelAdmin,
                                  ShopifyCollectionActions):
    actions = (
        'export_to_api_queryset_action',
        'mark_as_relevant_queryset_action',
        'mark_as_irrelevant_queryset_action'
    )

    change_actions = (
        'export_to_api_object_action',
    )

    search_fields = (
        'id',
        'collection_id',
        'title',
        'body_html'
    )

    list_display = (
        'details_link',
        'id',
        'collection_id',
        'title',
        'is_published',
        'may_be_relevant_flag',
        'is_relevant',
        'relevancy_errors',
        'notes'
    )

    list_display_links = (
        'details_link',
    )

    list_editable = (
        'is_published',
        'is_relevant'
    )

    list_filter = (
        'is_relevant',
        'is_published',
        'published_scope',
        'disjunctive',
        'sort_order',
        'tags'
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    'is_relevant',
                    'relevancy_errors'
                )
            }
        ),
        (
            'Collection', {
                'fields': (
                    'id',
                    'collection_id',
                    'title',
                    'is_published',
                    'published_scope',
                    'disjunctive',
                    'sort_order',
                    'body_html'
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
        ),
        (
            'Notes', {
                'fields': (
                    'notes',
                )
            }
        )
    )

    readonly_fields = (
        'id',
        'may_be_relevant_flag',
        'relevancy_errors',
        'details_link'
    )

    inlines = (
        ShopifyCollectionRulesManyToManyTabularInline,
        ShopifyCollectionTagsManyToManyTabularInline
    )

    def details_link(self, obj):
        if not obj:
            return None
        return get_change_view_link(obj, 'Details')
    details_link.short_description = ''

    def may_be_relevant_flag(self, obj):
        if obj.is_relevant != obj.may_be_relevant:
            return '~'
        else:
            return ''
    may_be_relevant_flag.short_description = ''

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if not request.user.is_superuser:
            readonly_fields += (
                'collection_id',
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
        'mark_as_relevant_queryset_action',
        'mark_as_irrelevant_queryset_action'
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
        'may_be_relevant_flag',
        'is_relevant',
        'relevancy_errors',
        'notes',
        'all_match__'
    )

    list_display_links = (
        'details_link',
    )

    list_editable = (
        'is_published',
        'is_relevant'
    )

    list_filter = (
        'is_relevant',
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
                    'is_relevant',
                    'relevancy_errors'
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
                    ('title', 'title_match__', 'title__'),
                    'is_published',
                    'published_scope',
                    ('body_html', 'body_html_match__', 'body_html__')
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
        ),
        (
            'Other Calculated', {
                'fields': (
                    ('tags__', 'tags_match__'),
                    ('images__', 'images_match__'),
                    ('metafields__', 'metafields_match__')
                )
            }
        ),
        (
            'Notes', {
                'fields': (
                    'notes',
                )
            }
        )
    )

    readonly_fields = (
        'id',
        'may_be_relevant_flag',
        'relevancy_errors',
        'details_link',
        'item_link',
        'premier_product_link',
        'sema_product_link',
        'vendor_link',
        'title__',
        'title_match__',
        'body_html__',
        'body_html_match__',
        'tags__',
        'tags_match__',
        'images__',
        'images_match__',
        'metafields__',
        'metafields_match__',
        'all_match__'
    )

    autocomplete_fields = (
        'vendor',
    )

    inlines = (
        ShopifyProductVariantsStackedInline,
        ShopifyProductMetafieldsTabularInline,
        ShopifyProductImagesTabularInline,
        ShopifyProductOptionsTabularInline,
        ShopifyProductTagsManyToManyTabularInline
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

    def may_be_relevant_flag(self, obj):
        if obj.is_relevant != obj.may_be_relevant:
            return '~'
        else:
            return ''
    may_be_relevant_flag.short_description = ''

    def title_match__(self, obj):
        return bool(obj.title == obj.calculator.title_)
    title_match__.boolean = True
    title_match__.short_description = ''

    def title__(self, obj):
        if self.title_match__(obj):
            return ''
        return obj.calculator.title_
    title__.short_description = ''

    def body_html_match__(self, obj):
        return bool(obj.body_html == obj.calculator.body_html_)
    body_html_match__.boolean = True
    body_html_match__.short_description = ''

    def body_html__(self, obj):
        if self.body_html_match__(obj):
            return ''
        return obj.calculator.body_html_
    body_html__.short_description = ''

    def tags_match__(self, obj):
        return bool(
            list(obj.tags.values_list('name', flat=True)).sort()
            == obj.calculator.tags_.sort()
        )
    tags_match__.boolean = True
    tags_match__.short_description = ''

    def tags__(self, obj):
        if self.tags_match__(obj):
            return ''
        return str(obj.calculator.tags_)
    tags__.short_description = 'tags'

    def images_match__(self, obj):
        return bool(
            list(obj.images.values_list('src', flat=True)).sort()
            == obj.calculator.images_.sort()
        )
    images_match__.boolean = True
    images_match__.short_description = ''

    def images__(self, obj):
        if self.images_match__(obj):
            return ''
        return str(obj.calculator.images_)
    images__.short_description = 'images'

    def metafields_match__(self, obj):
        from ..models import ShopifyMetafield
        try:
            sema_html_metafield = obj.metafields.get(
                owner_resource=ShopifyMetafield.PRODUCT_OWNER_RESOURCE,
                namespace='sema',
                key='html',
                value_type=ShopifyMetafield.STRING_VALUE_TYPE
            ).value
        except ShopifyMetafield.DoesNotExist:
            sema_html_metafield = ''
        return bool(sema_html_metafield == obj.calculator.metafield_sema_html_)
    metafields_match__.boolean = True
    metafields_match__.short_description = ''

    def metafields__(self, obj):
        if self.metafields_match__(obj):
            return ''
        return str(obj.calculator.metafield_sema_html_[:10])
    metafields__.short_description = 'metafields'

    def all_match__(self, obj):
        self_match = bool(
            self.title_match__(obj)
            and self.body_html_match__(obj)
            and self.tags_match__(obj)
            and self.images_match__(obj)
            and self.metafields_match__(obj)
        )
        for variant in obj.variants.all():
            if not bool(
                    variant.sku == obj.calculator.sku_
                    and variant.barcode == obj.calculator.barcode_
                    and variant.weight == obj.calculator.weight_
                    and variant.weight_unit == obj.calculator.weight_unit_
                    and variant.price == obj.calculator.price_
                    and variant.cost == obj.calculator.cost_):
                return False
        return self_match
    all_match__.boolean = True
    all_match__.short_description = 'calculated'

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
        'src'
    )

    list_display = (
        'details_link',
        'id',
        'product'
    )

    list_display_links = (
        'details_link',
    )

    fieldsets = (
        (
            'Image', {
                'fields': (
                    'id',
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
        'metafield_id',
        'value'
    )

    list_display = (
        'details_link',
        'id',
        'metafield_id',
        'product',
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
                'metafield_id',
            )
        return readonly_fields
