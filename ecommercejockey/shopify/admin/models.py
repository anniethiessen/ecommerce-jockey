from django_object_actions import BaseDjangoObjectActions as ObjectActions

from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.db.models import CharField, TextField
from django.forms import TextInput, Textarea

from core.admin.utils import (
    get_change_view_link,
    get_changelist_view_link,
    get_html_preview,
    get_image_preview,
    get_json_preview
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
from .filters import (
    ByCollectionLevel,
    ByTagLevel,
    HasCategoryPath,
    HasItem,
    HasPremierManufacturer,
    HasPremierProduct,
    HasSemaBrand,
    HasSemaCategory,
    HasSemaProduct,
    HasVendor
)
from .inlines import (
    ShopifyCollectionCalculatorStackedInline,
    ShopifyCollectionChildCollectionsTabularInline,
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
        'detail_link',
        'id',
        'name',
        'product_count',
        'warnings',
        'errors'
    )

    list_display_links = (
        'detail_link',
    )

    list_filter = (
        HasVendor,
        HasPremierManufacturer,
        HasSemaBrand
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    'vendor_link',
                    'premier_manufacturer_link',
                    'sema_brand_link',
                    'warnings',
                    'errors',
                    'id'
                )
            }
        ),
        (
            'Vendor', {
                'fields': (
                    'name',
                )
            }
        )
    )

    readonly_fields = (
        'id',
        'warnings',
        'errors',
        'detail_link',
        'vendor_link',
        'premier_manufacturer_link',
        'sema_brand_link',
        'product_count'
    )

    inlines = (
        ShopifyVendorProductsTabularInline,
    )

    def detail_link(self, obj):
        if not obj or not obj.pk:
            return None
        return get_change_view_link(obj, 'Details')
    detail_link.short_description = ''

    def vendor_link(self, obj):
        if not obj or not obj.pk or not hasattr(obj, 'vendor'):
            return None
        return get_change_view_link(obj.vendor, 'See Vendor')
    vendor_link.short_description = ''

    def premier_manufacturer_link(self, obj):
        if (not obj or not obj.pk or not hasattr(obj, 'vendor')
                or not obj.vendor.premier_manufacturer):
            return None

        return get_change_view_link(
            obj.vendor.premier_manufacturer,
            'See Premier Manufacturer'
        )
    premier_manufacturer_link.short_description = ''

    def sema_brand_link(self, obj):
        if (not obj or not obj.pk or not hasattr(obj, 'vendor')
                or not obj.vendor.sema_brand):
            return None

        return get_change_view_link(
            obj.vendor.sema_brand,
            'See SEMA Brand'
        )
    sema_brand_link.short_description = ''

    def product_count(self, obj):
        if not obj or not obj.pk:
            return None

        return f'{obj._product_published_count}/{obj._product_count}'
    product_count.admin_order_field = '_product_published_count'
    product_count.short_description = 'product count'
    
    def get_queryset(self, request):
        return super().get_queryset(request).with_admin_data()

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return (
                (
                    None, {
                        'fields': (
                            'name',
                        )
                    }
                ),
            )

        return super().get_fieldsets(request, obj)

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []

        return super().get_inline_instances(request, obj)


@admin.register(ShopifyCollection)
class ShopifyCollectionModelAdmin(ObjectActions, ModelAdmin,
                                  ShopifyCollectionActions):
    list_select_related = (
        'calculator',
        'parent_collection'
    )

    actions = (
        'update_calculated_fields_queryset_action',
        'mark_as_published_queryset_action',
        'mark_as_unpublished_queryset_action',
        'import_from_api_queryset_action',
        'export_to_api_queryset_action'
    )

    search_fields = (
        'id',
        'collection_id',
        'title',
        'handle',
        'body_html',
        'parent_collection__id',
        'parent_collection__collection_id',
        'parent_collection__title',
        'parent_collection__handle',
        'parent_collection__body_html'
    )

    list_display = (
        'detail_link',
        'id',
        'collection_id',
        'title',
        'handle',
        'body_html',
        'level',
        'is_published',
        'tag_count',
        'metafield_count',
        'rule_count',
        'child_collection_count',
        'warnings',
        'errors',
        'full_match'
    )

    list_display_links = (
        'detail_link',
    )

    list_editable = (
        'is_published',
    )

    list_filter = (
        'is_published',
        ByCollectionLevel,
        HasCategoryPath,
        HasSemaCategory,
        'published_scope',
        'disjunctive',
        'sort_order'
    )

    change_actions = (
        'update_calculated_fields_object_action',
        'import_from_api_object_action',
        'export_to_api_object_action'
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    'category_paths_link',
                    'sema_category_link',
                    'warnings',
                    'errors',
                    'id'
                )
            }
        ),
        (
            'Collection', {
                'fields': (
                    'collection_id',
                    'handle',
                    'title',
                    'body_html',
                    'is_published',
                    'published_scope',
                    'disjunctive',
                    'sort_order',
                )
            }
        ),
        (
            'Parent Collection', {
                'fields': (
                    'parent_collection_link',
                    'parent_collection'
                ),
                'classes': (
                    'collapse',
                )
            }
        ),
        (
            'Image', {
                'fields': (
                    ('image_src', 'image_preview'),
                    'image_alt'
                )
            }
        )
    )

    readonly_fields = (
        'id',
        'level',
        'warnings',
        'errors',
        'full_match',
        'image_preview',
        'detail_link',
        'category_paths_link',
        'sema_category_link',
        'parent_collection_link',
        'rule_count',
        'tag_count',
        'metafield_count',
        'child_collection_count'
    )

    autocomplete_fields = (
        'parent_collection',
    )

    inlines = (
        ShopifyCollectionRulesManyToManyTabularInline,
        ShopifyCollectionTagsManyToManyTabularInline,
        ShopifyCollectionMetafieldsTabularInline,
        ShopifyCollectionChildCollectionsTabularInline,
        ShopifyCollectionCalculatorStackedInline
    )

    def detail_link(self, obj):
        if not obj or not obj.pk:
            return None

        return get_change_view_link(obj, 'Details')
    detail_link.short_description = ''

    def category_paths_link(self, obj):
        if not obj or not obj.pk:
            return None

        if obj.level == '1':
            category_path_model = obj.root_category_paths.first()._meta.model
            query = f'shopify_root_collection={obj.pk}'
        elif obj.level == '2':
            category_path_model = obj.branch_category_paths.first()._meta.model
            query = f'shopify_branch_collection={obj.pk}'
        else:
            category_path_model = obj.leaf_category_paths.first()._meta.model
            query = f'shopify_leaf_collection={obj.pk}'

        return get_changelist_view_link(
            category_path_model,
            'See Category Paths',
            query=query
        )
    category_paths_link.short_description = ''

    def sema_category_link(self, obj):
        if not obj or not obj.pk:
            return None

        if obj.level == '1':
            o = obj.root_category_paths.first().sema_root_category
        elif obj.level == '2':
            o = obj.branch_category_paths.first().sema_branch_category
        else:
            o = obj.leaf_category_paths.first().sema_leaf_category

        return get_change_view_link(
            o,
            'See SEMA Category'
        )
    sema_category_link.short_description = ''

    def parent_collection_link(self, obj):
        if not obj or not obj.pk or not obj.parent_collection:
            return None

        return get_change_view_link(
            obj.parent_collection,
            'See Full Parent Collection'
        )
    parent_collection_link.short_description = ''
    
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

    def image_preview(self, obj):
        if not obj or not obj.pk or not obj.image_src:
            return None

        return get_image_preview(obj.image_src)
    image_preview.short_description = ''

    def get_queryset(self, request):
        return super().get_queryset(request).with_admin_data()

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return (
                (
                    None, {
                        'fields': (
                            'title',
                            'is_published',
                            'published_scope',
                            'disjunctive',
                            'sort_order',
                            'body_html',
                            'parent_collection',
                            'image_src',
                            'image_alt'
                        )
                    }
                ),
            )

        return super().get_fieldsets(request, obj)

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
            return []

        return super().get_inline_instances(request, obj)


@admin.register(ShopifyCollectionRule)
class ShopifyCollectionRuleModelAdmin(ObjectActions, ModelAdmin,
                                      ShopifyCollectionRuleActions):
    search_fields = (
        'id',
        'condition'
    )

    list_display = (
        'detail_link',
        'id',
        'column',
        'relation',
        'condition',
        'collection_count'
    )

    list_display_links = (
        'detail_link',
    )

    list_filter = (
        'column',
        'relation'
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    'id',
                )
            }
        ),
        (
            'Rule', {
                'fields': (
                    'column',
                    'relation',
                    'condition'
                )
            }
        )
    )

    readonly_fields = (
        'id',
        'detail_link',
        'collection_count'
    )

    inlines = (
        ShopifyRuleCollectionsManyToManyTabularInline,
    )

    def detail_link(self, obj):
        if not obj or not obj.pk:
            return None

        return get_change_view_link(obj, 'Details')
    detail_link.short_description = ''

    def collection_count(self, obj):
        if not obj or not obj.pk:
            return None

        return f'{obj._collection_published_count}/{obj._collection_count}'
    collection_count.admin_order_field = '_collection_published_count'
    collection_count.short_description = 'collection count'

    def get_queryset(self, request):
        return super().get_queryset(request).with_admin_data()

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return (
                (
                    None, {
                        'fields': (
                            'column',
                            'relation',
                            'condition'
                        )
                    }
                ),
            )

        return super().get_fieldsets(request, obj)

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []

        return super().get_inline_instances(request, obj)


@admin.register(ShopifyTag)
class ShopifyTagModelAdmin(ObjectActions, ModelAdmin, ShopifyTagActions):
    search_fields = (
        'id',
        'name'
    )

    list_display = (
        'detail_link',
        'id',
        'name',
        'product_count',
        'collection_count'
    )

    list_display_links = (
        'detail_link',
    )

    list_filter = (
        ByTagLevel,
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    'id',
                )
            }
        ),
        (
            'Tag', {
                'fields': (
                    'name',
                )
            }
        )
    )

    readonly_fields = (
        'id',
        'detail_link',
        'product_count',
        'collection_count'
    )

    inlines = (
        ShopifyTagProductsManyToManyTabularInline,
        ShopifyTagCollectionsManyToManyTabularInline
    )

    def detail_link(self, obj):
        if not obj or not obj.pk:
            return None

        return get_change_view_link(obj, 'Details')
    detail_link.short_description = ''

    def product_count(self, obj):
        if not obj or not obj.pk:
            return None

        return f'{obj._product_published_count}/{obj._product_count}'
    product_count.admin_order_field = '_product_published_count'
    product_count.short_description = 'product count'

    def collection_count(self, obj):
        if not obj or not obj.pk:
            return None

        return f'{obj._collection_published_count}/{obj._collection_count}'
    collection_count.admin_order_field = '_collection_published_count'
    collection_count.short_description = 'collection count'

    def get_queryset(self, request):
        return super().get_queryset(request).with_admin_data()

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return (
                (
                    None, {
                        'fields': (
                            'name',
                        )
                    }
                ),
            )

        return super().get_fieldsets(request, obj)

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []

        return super().get_inline_instances(request, obj)


@admin.register(ShopifyProduct)
class ShopifyProductModelAdmin(ObjectActions, ModelAdmin,
                               ShopifyProductActions):
    list_select_related = (
        'calculator',
        'vendor'
    )

    actions = (
        'update_calculated_fields_queryset_action',
        'mark_as_published_queryset_action',
        'mark_as_unpublished_queryset_action',
        'import_from_api_queryset_action',
        'export_to_api_queryset_action'
    )

    search_fields = (
        'id',
        'product_id',
        'title',
        'body_html',
        'seo_title',
        'seo_description',
        'vendor__id',
        'vendor__name'
    )

    list_display = (
        'detail_link',
        'id',
        'product_id',
        'title',
        'body_html',
        'vendor',
        'is_published',
        'variant_count',
        'option_count',
        'image_count',
        'metafield_count',
        'tag_count',
        'warnings',
        'errors',
        'full_match'
    )

    list_display_links = (
        'detail_link',
    )

    list_editable = (
        'is_published',
    )

    list_filter = (
        'is_published',
        HasItem,
        HasPremierProduct,
        HasSemaProduct,
        'published_scope',
        'product_type',
        'vendor'
    )

    change_actions = (
        'update_calculated_fields_object_action',
        'import_from_api_object_action',
        'export_to_api_object_action'
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    'item_link',
                    'premier_product_link',
                    'sema_product_link',
                    'warnings',
                    'errors',
                    'id'
                )
            }
        ),
        (
            'Product', {
                'fields': (
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
                ),
                'classes': (
                    'collapse',
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
        'warnings',
        'errors',
        'full_match',
        'detail_link',
        'item_link',
        'premier_product_link',
        'sema_product_link',
        'vendor_link',
        'variant_count',
        'option_count',
        'image_count',
        'tag_count',
        'metafield_count'
    )

    autocomplete_fields = (
        'vendor',
    )

    inlines = (
        ShopifyProductVariantsStackedInline,
        ShopifyProductOptionsTabularInline,
        ShopifyProductImagesTabularInline,
        ShopifyProductTagsManyToManyTabularInline,
        ShopifyProductMetafieldsTabularInline,
        ShopifyProductCalculatorStackedInline
    )

    def detail_link(self, obj):
        if not obj or not obj.pk:
            return None

        return get_change_view_link(obj, 'Details')
    detail_link.short_description = ''

    def item_link(self, obj):
        if not obj or not obj.pk or not hasattr(obj, 'item'):
            return None

        return get_change_view_link(obj.item, 'See Item')
    item_link.short_description = ''

    def premier_product_link(self, obj):
        if (not obj or not obj.pk or not hasattr(obj, 'item')
                or not obj.item.premier_product):
            return None

        return get_change_view_link(
            obj.item.premier_product,
            'See Premier Product'
        )
    premier_product_link.short_description = ''

    def sema_product_link(self, obj):
        if (not obj or not obj.pk or not hasattr(obj, 'item')
                or not obj.item.sema_product):
            return None

        return get_change_view_link(
            obj.item.sema_product,
            'See SEMA Product'
        )
    sema_product_link.short_description = ''

    def vendor_link(self, obj):
        if not obj or not obj.pk or not obj.vendor:
            return None

        return get_change_view_link(obj.vendor, 'See Full Vendor')
    vendor_link.short_description = ''

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
        if not obj or not obj.pk or not hasattr(obj, 'calculator'):
            return None

        return obj.calculator.full_match()
    full_match.boolean = True
    full_match.short_description = 'calculated'

    def get_queryset(self, request):
        return super().get_queryset(request).with_admin_data()

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return (
                (
                    None, {
                        'fields': (
                            'product_type',
                            'title',
                            'is_published',
                            'published_scope',
                            'body_html',
                            'vendor',
                            'seo_title',
                            'seo_description'
                        )
                    }
                ),
            )

        return super().get_fieldsets(request, obj)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)

        if not request.user.is_superuser:
            readonly_fields += (
                'product_id',
            )

        return readonly_fields

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []

        return super().get_inline_instances(request, obj)


@admin.register(ShopifyImage)
class ShopifyImageModelAdmin(ObjectActions, ModelAdmin, ShopifyImageActions):
    list_select_related = (
        'product',
    )

    actions = (
        'import_from_api_queryset_action',
        'export_to_api_queryset_action'
    )

    search_fields = (
        'id',
        'image_id',
        'link',
        'src',
        'product__id',
        'product__product_id',
        'product__title',
        'product__body_html',
        'product__seo_title',
        'product__seo_description',
        'product__vendor__id',
        'product__vendor__name'
    )

    list_display = (
        'detail_link',
        'id',
        'image_id',
        'product',
        'link',
        'image_preview'
    )

    list_display_links = (
        'detail_link',
    )

    change_actions = (
        'import_from_api_object_action',
        'export_to_api_object_action'
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    'id',
                )
            }
        ),
        (
            'Product', {
                'fields': (
                    'product_link',
                    'product'
                ),
                'classes': (
                    'collapse',
                )
            }
        ),
        (
            'Image', {
                'fields': (
                    'image_id',
                    ('link', 'image_preview'),
                    'src'
                )
            }
        )
    )

    readonly_fields = (
        'id',
        'image_preview',
        'detail_link',
        'product_link'
    )

    autocomplete_fields = (
        'product',
    )

    def detail_link(self, obj):
        if not obj or not obj.pk:
            return None
        return get_change_view_link(obj, 'Details')
    detail_link.short_description = ''

    def product_link(self, obj):
        if not obj or not obj.pk or not obj.product:
            return None

        return get_change_view_link(obj.product, 'See Full Product')
    product_link.short_description = ''

    def image_preview(self, obj):
        if not obj or not obj.pk or not obj.link:
            return None

        return get_image_preview(obj.link)
    image_preview.short_description = ''
    
    def get_queryset(self, request):
        return super().get_queryset(request).with_admin_data()

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return (
                (
                    None, {
                        'fields': (
                            'product',
                            'link'
                        )
                    }
                ),
            )

        return super().get_fieldsets(request, obj)

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
        'id',
        'option_id',
        'name',
        'values',
        'product__id',
        'product__product_id',
        'product__title',
        'product__body_html',
        'product__seo_title',
        'product__seo_description',
        'product__vendor__id',
        'product__vendor__name'
    )

    list_display = (
        'detail_link',
        'id',
        'option_id',
        'product',
        'name',
        'values'
    )

    list_display_links = (
        'detail_link',
    )

    list_filter = (
        'name',
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    'id',
                )
            }
        ),
        (
            'Product', {
                'fields': (
                    'product_link',
                    'product'
                ),
                'classes': (
                    'collapse',
                )
            }
        ),
        (
            'Option', {
                'fields': (
                    'option_id',
                    'name',
                    'values'
                )
            }
        )
    )

    readonly_fields = (
        'id',
        'detail_link',
        'product_link'
    )

    autocomplete_fields = (
        'product',
    )

    def detail_link(self, obj):
        if not obj or not obj.pk:
            return None

        return get_change_view_link(obj, 'Details')
    detail_link.short_description = ''

    def product_link(self, obj):
        if not obj or not obj.pk or not obj.product:
            return None
        return get_change_view_link(obj.product, 'See Full Product')
    product_link.short_description = ''
    
    def get_queryset(self, request):
        return super().get_queryset(request).with_admin_data()

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return (
                (
                    None, {
                        'fields': (
                            'product',
                            'name',
                            'values'
                        )
                    }
                ),
            )

        return super().get_fieldsets(request, obj)

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
        'id',
        'variant_id',
        'title',
        'sku',
        'barcode',
        'product__id',
        'product__product_id',
        'product__title',
        'product__body_html',
        'product__seo_title',
        'product__seo_description',
        'product__vendor__id',
        'product__vendor__name'
    )

    list_display = (
        'detail_link',
        'id',
        'variant_id',
        'product',
        'title',
        'sku',
        'barcode',
        'grams',
        'weight',
        'weight_unit',
        'cost',
        'price',
        'is_taxable',
        'tax_code'
    )

    list_display_links = (
        'detail_link',
    )

    list_filter = (
        'weight_unit',
        'inventory_management',
        'inventory_policy',
        'fulfillment_service',
        'is_taxable',
        'tax_code'
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    'id',
                )
            }
        ),
        (
            'Product', {
                'fields': (
                    'product_link',
                    'product'
                ),
                'classes': (
                    'collapse',
                )
            }
        ),
        (
            'Variant', {
                'fields': (
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
        'id',
        'detail_link',
        'product_link'
    )

    autocomplete_fields = (
        'product',
    )

    def detail_link(self, obj):
        if not obj or not obj.pk:
            return None

        return get_change_view_link(obj, 'Details')
    detail_link.short_description = ''

    def product_link(self, obj):
        if not obj or not obj.pk or not obj.product:
            return None

        return get_change_view_link(obj.product, 'See Full Product')
    product_link.short_description = ''
    
    def get_queryset(self, request):
        return super().get_queryset(request).with_admin_data()

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return (
                (
                    None, {
                        'fields': (
                            'product',
                            'title',
                            'sku',
                            'barcode',
                            'grams',
                            'weight',
                            'weight_unit',
                            'price',
                            'compare_at_price',
                            'cost',
                            'is_taxable',
                            'tax_code',
                            'inventory_management',
                            'inventory_policy',
                            'fulfillment_service'
                        )
                    }
                ),
            )

        return super().get_fieldsets(request, obj)

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

    actions = (
        'import_from_api_queryset_action',
        'export_to_api_queryset_action'
    )

    search_fields = (
        'id',
        'metafield_id',
        'value',
        'product__id',
        'product__product_id',
        'product__title',
        'product__body_html',
        'product__seo_title',
        'product__seo_description',
        'product__vendor__id',
        'product__vendor__name',
        'collection__id',
        'collection__collection_id',
        'collection__title',
        'collection__handle',
        'collection__body_html',
        'collection__parent_collection__id',
        'collection__parent_collection__collection_id',
        'collection__parent_collection__title',
        'collection__parent_collection__handle',
        'collection__parent_collection__body_html'
    )

    list_display = (
        'detail_link',
        'id',
        'metafield_id',
        'content_object',
        'owner_resource',
        'namespace',
        'value_type',
        'key',
        'value_item_count'
    )

    list_display_links = (
        'detail_link',
    )

    list_filter = (
        'content_type',
        'owner_resource',
        'namespace',
        'key',
        'value_type'
    )

    change_actions = (
        'import_from_api_object_action',
        'export_to_api_object_action'
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    'id',
                )
            }
        ),
        (
            'Related Object', {
                'fields': (
                    'content_object_link',
                    'content_object_str',
                    'content_type',
                    'object_id'
                ),
                'classes': (
                    'collapse',
                )
            }
        ),
        (
            'Metafield', {
                'fields': (
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
            'Preview', {
                'fields': (
                    'value_preview',
                ),
                'classes': (
                    'collapse',
                )
            }
        )
    )

    readonly_fields = (
        'id',
        'content_object_str',
        'value_preview',
        'detail_link',
        'content_object_link',
        'value_item_count'
    )

    def detail_link(self, obj):
        if not obj:
            return None

        return get_change_view_link(obj, 'Details')
    detail_link.short_description = ''

    def content_object_link(self, obj):
        if not obj or not obj.pk or not obj.content_object:
            return None

        return get_change_view_link(obj.content_object, 'See Full Object')
    content_object_link.short_description = ''

    def content_object_str(self, obj):
        if not obj or not obj.pk or not obj.content_object:
            return None

        return str(obj.content_object)
    content_object_str.short_description = ''

    def value_preview(self, obj):
        if not obj or not obj.pk:
            return None

        if (obj.value_type == obj._meta.model.STRING_VALUE_TYPE
                and obj.value[:6].lower() == '<html>'):
            return get_html_preview(obj.value)
        elif obj.value_type == obj._meta.model.JSON_VALUE_TYPE:
            return get_json_preview(obj.value)
        else:
            return None
    value_preview.short_description = ''
    
    def get_queryset(self, request):
        return super().get_queryset(request).with_admin_data()

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return (
                (
                    None, {
                        'fields': (
                            'content_type',
                            'object_id',
                            'owner_resource',
                            'namespace',
                            'value_type',
                            'key',
                            'value'
                        )
                    }
                ),
            )

        return super().get_fieldsets(request, obj)

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
    list_select_related = (
        'product',
    )

    actions = (
        'update_calculated_fields_queryset_action',
    )

    search_fields = (
        'id',
        'product__id',
        'product__product_id',
        'product__title',
        'product__body_html',
        'product__seo_title',
        'product__seo_description',
        'product__vendor__id',
        'product__vendor__name'
    )

    list_display = (
        'detail_link',
        'id',
        'product',
        'full_match',
        'sema_description_def_value_short_preview',
        'sema_description_des_value_short_preview',
        'sema_description_inv_value_short_preview',
        'sema_description_ext_value_short_preview',
        'sema_description_tle_value_short_preview',
        'sema_description_sho_value_short_preview',
        'sema_description_mkt_value_short_preview',
        'sema_description_key_value_short_preview',
        'sema_description_asc_value_short_preview',
        'sema_description_asm_value_short_preview',
        'sema_description_fab_value_short_preview',
        'sema_description_lab_value_short_preview',
        'sema_description_shp_value_short_preview',
        'sema_description_oth_value_short_preview',
        'premier_description_value_short_preview',
        'title_choice',
        'body_html_choice',
        'premier_cost_cad_value_preview',
        'variant_price_markup_choice',
        'sema_filtered_images_short_preview',
        'premier_primary_images_short_preview',
        'images_choice'
    )

    list_display_links = (
        'detail_link',
    )

    list_editable = (
        'title_choice',
        'body_html_choice',
        'variant_price_markup_choice',
        'images_choice'
    )

    change_actions = (
        'update_calculated_fields_object_action',
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    'item_link',
                    'premier_product_link',
                    'sema_product_link',
                    'id',
                )
            }
        ),
        (
            'Product', {
                'fields': (
                    'product_link',
                    'product'
                ),
                'classes': (
                    'collapse',
                )
            }
        ),
        (
            'Text Previews', {
                'fields': (
                    'sema_description_def_value_preview',
                    'sema_description_des_value_preview',
                    'sema_description_inv_value_preview',
                    'sema_description_ext_value_preview',
                    'sema_description_tle_value_preview',
                    'sema_description_sho_value_preview',
                    'sema_description_mkt_value_preview',
                    'sema_description_key_value_preview',
                    'sema_description_asc_value_preview',
                    'sema_description_asm_value_preview',
                    'sema_description_fab_value_preview',
                    'sema_description_lab_value_preview',
                    'sema_description_shp_value_preview',
                    'sema_description_oth_value_preview',
                    'premier_description_value_preview'
                ),
                'classes': (
                    'collapse',
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
            'Weight Previews', {
                'fields': (
                    'premier_weight_value_preview',
                ),
                'classes': (
                    'collapse',
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
            'Cost Previews', {
                'fields': (
                    'premier_cost_cad_value_preview',
                    'premier_cost_usd_value_preview'
                ),
                'classes': (
                    'collapse',
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
            'Identifier Previews', {
                'fields': (
                    'premier_premier_part_number_value_preview',
                    'premier_upc_value_preview'
                ),
                'classes': (
                    'collapse',
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
            'Metafield Packaging Previews', {
                'fields': (
                    'sema_html_value_preview',
                    'sema_html_preview'
                ),
                'classes': (
                    'collapse',
                )
            }
        ),
        (
            'Metafield Fitments Previews', {
                'fields': (
                    'sema_vehicles_value_preview',
                ),
                'classes': (
                    'collapse',
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
            'Tag Vendor Previews', {
                'fields': (
                    'sema_brand_tag_names_value_preview',
                ),
                'classes': (
                    'collapse',
                )
            }
        ),
        (
            'Tag Collection Previews', {
                'fields': (
                    'sema_category_tag_names_value_preview',
                ),
                'classes': (
                    'collapse',
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
            'Image Previews', {
                'fields': (
                    'sema_filtered_images_preview',
                    'premier_primary_images_preview'
                ),
                'classes': (
                    'collapse',
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
        )
    )

    readonly_fields = (
        'id',
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
        'images_difference',
        'sema_description_def_value_preview',
        'sema_description_def_value_short_preview',
        'sema_description_des_value_preview',
        'sema_description_des_value_short_preview',
        'sema_description_inv_value_preview',
        'sema_description_inv_value_short_preview',
        'sema_description_ext_value_preview',
        'sema_description_ext_value_short_preview',
        'sema_description_tle_value_preview',
        'sema_description_tle_value_short_preview',
        'sema_description_sho_value_preview',
        'sema_description_sho_value_short_preview',
        'sema_description_mkt_value_preview',
        'sema_description_mkt_value_short_preview',
        'sema_description_key_value_preview',
        'sema_description_key_value_short_preview',
        'sema_description_asc_value_preview',
        'sema_description_asc_value_short_preview',
        'sema_description_asm_value_preview',
        'sema_description_asm_value_short_preview',
        'sema_description_fab_value_preview',
        'sema_description_fab_value_short_preview',
        'sema_description_lab_value_preview',
        'sema_description_lab_value_short_preview',
        'sema_description_shp_value_preview',
        'sema_description_shp_value_short_preview',
        'sema_description_oth_value_preview',
        'sema_description_oth_value_short_preview',
        'sema_html_preview',
        'sema_html_value_preview',
        'sema_vehicles_value_preview',
        'sema_brand_tag_names_value_preview',
        'sema_category_tag_names_value_preview',
        'sema_filtered_images_preview',
        'sema_filtered_images_short_preview',
        'premier_description_value_preview',
        'premier_description_value_short_preview',
        'premier_weight_value_preview',
        'premier_cost_cad_value_preview',
        'premier_cost_usd_value_preview',
        'premier_premier_part_number_value_preview',
        'premier_upc_value_preview',
        'premier_primary_images_preview',
        'premier_primary_images_short_preview',
        'detail_link',
        'item_link',
        'product_link',
        'premier_product_link',
        'sema_product_link'
    )

    autocomplete_fields = (
        'product',
    )

    formfield_overrides = {
        CharField: {'widget': TextInput(attrs={'size': '40'})},
        TextField: {'widget': Textarea(attrs={'rows': 3, 'cols': 40})},
    }

    def detail_link(self, obj):
        if not obj or not obj.pk:
            return None

        return get_change_view_link(obj, 'Details')
    detail_link.short_description = ''

    def product_link(self, obj):
        if not obj or not obj.pk or not obj.product:
            return None

        return get_change_view_link(obj.product, 'See Full Product')
    product_link.short_description = ''

    def item_link(self, obj):
        if not obj or not obj.pk or not hasattr(obj.product, 'item'):
            return None

        return get_change_view_link(obj.product.item, 'See Item')
    item_link.short_description = ''

    def premier_product_link(self, obj):
        if (not obj or not obj.pk or not obj.product or
                not hasattr(obj.product, 'item')
                or not obj.product.item.premier_product):
            return None

        return get_change_view_link(
            obj.product.item.premier_product,
            'See Premier product'
        )
    premier_product_link.short_description = ''

    def sema_product_link(self, obj):
        if (not obj or not obj.pk or not obj.product
                or not hasattr(obj.product, 'item')
                or not obj.product.item.sema_product):
            return None

        return get_change_view_link(
            obj.product.item.sema_product,
            'See SEMA Product'
        )
    sema_product_link.short_description = ''
    
    def get_queryset(self, request):
        return super().get_queryset(request).with_admin_data()

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return (
                (
                    None, {
                        'fields': (
                            'product',
                            'title_choice',
                            'body_html_choice',
                            'variant_weight_choice',
                            'variant_weight_unit_choice',
                            'variant_cost_choice',
                            'variant_price_base_choice',
                            'variant_price_markup_choice',
                            'variant_sku_choice',
                            'variant_barcode_choice',
                            'metafield_value_packaging_choice',
                            'metafield_value_fitments_choice',
                            'metafields_choice',
                            'tag_names_vendor_choice',
                            'tag_names_collection_choice',
                            'tags_choice',
                            'image_urls_sema_choice',
                            'image_urls_premier_choice',
                            'images_choice'
                        )
                    }
                ),
            )

        return super().get_fieldsets(request, obj)


@admin.register(ShopifyCollectionCalculator)
class ShopifyCollectionCalculatorModelAdmin(ObjectActions, ModelAdmin,
                                            ShopifyCollectionCalculatorActions):
    list_select_related = (
        'collection',
    )

    actions = (
        'update_calculated_fields_queryset_action',
    )

    search_fields = (
        'id',
        'collection__id',
        'collection__collection_id',
        'collection__title',
        'collection__handle',
        'collection__body_html',
        'collection__parent_collection__id',
        'collection__parent_collection__collection_id',
        'collection__parent_collection__title',
        'collection__parent_collection__handle',
        'collection__parent_collection__body_html'
    )

    list_display = (
        'detail_link',
        'id',
        'collection',
        'full_match',
        'title_option'
    )

    list_display_links = (
        'detail_link',
    )

    list_editable = (
        'title_option',
    )

    change_actions = (
        'update_calculated_fields_object_action',
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    'category_paths_link',
                    'sema_category_link',
                    'id'
                )
            }
        ),
        (
            'Collection', {
                'fields': (
                    'collection_link',
                    'collection'
                ),
                'classes': (
                    'collapse',
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
        'id',
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
        'sema_category_tags_preview',
        'detail_link',
        'collection_link',
        'category_paths_link',
        'sema_category_link'
    )

    autocomplete_fields = (
        'collection',
    )

    def detail_link(self, obj):
        if not obj:
            return None
        return get_change_view_link(obj, 'Details')
    detail_link.short_description = ''

    def collection_link(self, obj):
        if not obj or not obj.pk or not obj.collection:
            return None

        return get_change_view_link(obj.collection, 'See Full Collection')
    collection_link.short_description = ''

    def category_paths_link(self, obj):
        if not obj or not obj.pk or not not obj.collection:
            return None

        if obj.collection.level == '1':
            category_path_model = obj.collection.root_category_paths.first()._meta.model
            query = f'shopify_root_collection={obj.collection.pk}'
        elif obj.collection.level == '2':
            category_path_model = obj.collection.branch_category_paths.first()._meta.model
            query = f'shopify_branch_collection={obj.collection.pk}'
        else:
            category_path_model = obj.collection.leaf_category_paths.first()._meta.model
            query = f'shopify_leaf_collection={obj.collection.pk}'

        return get_changelist_view_link(
            category_path_model,
            'See Category Paths',
            query=query
        )
    category_paths_link.short_description = ''

    def sema_category_link(self, obj):
        if not obj or not obj.pk or not obj.collection:
            return None

        if obj.collection.level == '1':
            o = obj.collection.root_category_paths.first().sema_root_category
            query = f'shopify_root_collection={obj.collection.pk}'
        elif obj.collection.level == '2':
            o = obj.collection.branch_category_paths.first().sema_branch_category
            query = f'shopify_branch_collection={obj.collection.pk}'
        else:
            o = obj.collection.leaf_category_paths.first().sema_leaf_category
            query = f'shopify_leaf_collection={obj.collection.pk}'

        return get_change_view_link(
            o,
            'See SEMA Category'
        )
    sema_category_link.short_description = ''
    
    def get_queryset(self, request):
        return super().get_queryset(request).with_admin_data()

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return (
                (
                    None, {
                        'fields': (
                            'collection',
                            'title_option',
                            'metafields_display_name_option',
                            'metafields_subcollections_option',
                            'tags_categories_option'
                        )
                    }
                ),
            )

        return super().get_fieldsets(request, obj)
