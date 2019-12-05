from django_object_actions import BaseDjangoObjectActions as ObjectActions

from django.contrib import admin
from django.contrib.admin import ModelAdmin

from core.admin.utils import get_change_view_link
from ..models import (
    CategoryPath,
    Item,
    Vendor
)
from .actions import (
    CategoryPathActions,
    ItemActions,
    VendorActions
)
from .filters import (
    CategoryPathIsComplete,
    CategoryPathMayBeRelevant,
    HasPremierManufacturer,
    HasPremierProduct,
    HasSemaBrand,
    HasSemaBranchCategory,
    HasSemaLeafCategory,
    HasSemaProduct,
    HasSemaRootCategory,
    HasShopifyBranchCollection,
    HasShopifyLeafCollection,
    HasShopifyProduct,
    HasShopifyRootCollection,
    HasShopifyVendor,
    ItemIsComplete,
    ItemMayBeRelevant,
    VendorIsComplete,
    VendorMayBeRelevant
)


@admin.register(Vendor)
class VendorModelAdmin(ObjectActions, ModelAdmin, VendorActions):
    list_select_related = (
        'premier_manufacturer',
        'sema_brand',
        'shopify_vendor'
    )

    actions = (
        'mark_as_relevant_queryset_action',
        'mark_as_irrelevant_queryset_action',
        'create_shopify_vendors_queryset_action'
    )

    change_actions = (
        'create_shopify_vendors_object_action',
    )

    search_fields = (
        'id',
        'premier_manufacturer__id',
        'premier_manufacturer__name',
        'sema_brand__brand_id',
        'sema_brand__name',
        'shopify_vendor__id',
        'shopify_vendor__name'
    )

    list_display = (
        'detail_link',
        'id',
        'premier_manufacturer',
        'sema_brand',
        'shopify_vendor',
        'may_be_relevant_flag',
        'is_relevant',
        'relevancy_warnings',
        'relevancy_errors',
        'relevancy_exception',
        'notes'
    )

    list_display_links = (
        'detail_link',
    )

    list_editable = (
        'is_relevant',
        'relevancy_exception'
    )

    list_filter = (
        'is_relevant',
        VendorMayBeRelevant,
        VendorIsComplete,
        HasPremierManufacturer,
        HasSemaBrand,
        HasShopifyVendor
    )

    changelist_actions = (
        'check_unlinked_vendors_class_action',
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    'may_be_relevant_flag',
                    'is_relevant',
                    'relevancy_warnings',
                    'relevancy_errors',
                    'relevancy_exception',
                    'id'
                )
            }
        ),
        (
            'Premier Manufacturer', {
                'fields': (
                    'premier_manufacturer_link',
                    'premier_manufacturer'
                )
            }
        ),
        (
            'Sema Brand', {
                'fields': (
                    'sema_brand_link',
                    'sema_brand'
                )
            }
        ),
        (
            'Shopify Vendor', {
                'fields': (
                    'shopify_vendor_link',
                    'shopify_vendor'
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
        'relevancy_warnings',
        'relevancy_errors',
        'may_be_relevant_flag',
        'detail_link',
        'premier_manufacturer_link',
        'shopify_vendor_link',
        'sema_brand_link'
    )

    autocomplete_fields = (
        'premier_manufacturer',
        'sema_brand',
        'shopify_vendor'
    )

    def detail_link(self, obj):
        if not obj or not obj.pk:
            return None

        return get_change_view_link(obj, 'Details')
    detail_link.short_description = ''

    def premier_manufacturer_link(self, obj):
        if not obj or not obj.pk or not obj.premier_manufacturer:
            return None

        return get_change_view_link(
            obj.premier_manufacturer, 'See Full Premier Manufacturer')
    premier_manufacturer_link.short_description = ''

    def sema_brand_link(self, obj):
        if not obj or not obj.pk or not obj.sema_brand:
            return None

        return get_change_view_link(
            obj.sema_brand, 'See Full SEMA Brand')
    sema_brand_link.short_description = ''

    def shopify_vendor_link(self, obj):
        if not obj or not obj.pk or not obj.shopify_vendor:
            return None

        return get_change_view_link(
            obj.shopify_vendor, 'See Full Shopify Vendor')
    shopify_vendor_link.short_description = ''

    def may_be_relevant_flag(self, obj):
        if not obj or not obj.pk:
            return None

        if obj.is_relevant != obj.may_be_relevant:
            return '~'
        else:
            return ''
    may_be_relevant_flag.short_description = ''

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return (
                (
                    None, {
                        'fields': (
                            'premier_manufacturer',
                            'sema_brand',
                            'shopify_vendor',
                            'notes'
                        )
                    }
                )
            )

        return super().get_fieldsets(request, obj)


@admin.register(Item)
class ItemModelAdmin(ObjectActions, ModelAdmin, ItemActions):
    list_select_related = (
        'premier_product',
        'sema_product',
        'shopify_product'
    )

    actions = (
        'mark_as_relevant_queryset_action',
        'mark_as_irrelevant_queryset_action',
        'create_shopify_products_queryset_action'
    )

    changelist_actions = (
        'create_and_link_items_class_action',
    )

    search_fields = (
        'id',
        'premier_product__premier_part_number',
        'premier_product__vendor_part_number',
        'premier_product__description',
        'premier_product__upc',
        'premier_product__manufacturer__id',
        'premier_product__manufacturer__name',
        'sema_product__product_id',
        'sema_product__part_number',
        'sema_product__dataset__dataset_id',
        'sema_product__dataset__name',
        'sema_product__dataset__brand__brand_id',
        'sema_product__dataset__brand__name',
        'shopify_product__id',
        'shopify_product__product_id',
        'shopify_product__title',
        'shopify_product__body_html',
        'shopify_product__seo_title',
        'shopify_product__seo_description',
        'shopify_product__vendor__id',
        'shopify_product__vendor__name'
    )

    list_display = (
        'detail_link',
        'id',
        'premier_product',
        'sema_product',
        'shopify_product',
        'may_be_relevant_flag',
        'is_relevant',
        'relevancy_warnings',
        'relevancy_errors',
        'relevancy_exception',
        'notes'
    )

    list_display_links = (
        'detail_link',
    )

    list_editable = (
        'is_relevant',
        'relevancy_exception'
    )

    list_filter = (
        'is_relevant',
        ItemMayBeRelevant,
        ItemIsComplete,
        HasPremierProduct,
        HasSemaProduct,
        HasShopifyProduct
    )

    change_actions = (
        'create_shopify_products_object_action',
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    'may_be_relevant_flag',
                    'is_relevant',
                    'relevancy_warnings',
                    'relevancy_errors',
                    'relevancy_exception',
                    'id'
                )
            }
        ),
        (
            'Premier Product', {
                'fields': (
                    'premier_product_link',
                    'premier_product'
                )
            }
        ),
        (
            'SEMA Product', {
                'fields': (
                    'sema_product_link',
                    'sema_product'
                )
            }
        ),
        (
            'Shopify Product', {
                'fields': (
                    'shopify_product_link',
                    'shopify_product'
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
        'relevancy_warnings',
        'relevancy_errors',
        'detail_link',
        'premier_product_link',
        'sema_product_link',
        'shopify_product_link'
    )

    autocomplete_fields = (
        'premier_product',
        'sema_product',
        'shopify_product'
    )

    def detail_link(self, obj):
        return get_change_view_link(obj, 'Details')
    detail_link.short_description = ''

    def premier_product_link(self, obj):
        if not obj or not obj.pk or not obj.premier_product:
            return None

        return get_change_view_link(
            obj.premier_product,
            'See Full Premier Product'
        )
    detail_link.short_description = ''

    def sema_product_link(self, obj):
        if not obj or not obj.pk or not obj.sema_product:
            return None

        return get_change_view_link(
            obj.sema_product,
            'See Full SEMA Product'
        )
    sema_product_link.short_description = ''

    def shopify_product_link(self, obj):
        if not obj or not obj.pk or not obj.shopify_product:
            return None

        return get_change_view_link(
            obj.shopify_product,
            'See Full Shopify Product'
        )
    shopify_product_link.short_description = ''

    def may_be_relevant_flag(self, obj):
        if not obj or not obj.pk:
            return None

        if obj.is_relevant != obj.may_be_relevant:
            return '~'
        else:
            return ''
    may_be_relevant_flag.short_description = ''

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return (
                (
                    None, {
                        'fields': (
                            'premier_product',
                            'sema_product',
                            'shopify_product',
                            'notes'
                        )
                    }
                )
            )

        return super().get_fieldsets(request, obj)


@admin.register(CategoryPath)
class CategoryPathModelAdmin(ObjectActions, ModelAdmin, CategoryPathActions):
    list_select_related = (
        'sema_root_category',
        'shopify_root_collection',
        'sema_branch_category',
        'shopify_branch_collection',
        'sema_leaf_category',
        'shopify_leaf_collection'
    )

    actions = (
        'mark_as_relevant_queryset_action',
        'mark_as_irrelevant_queryset_action',
        'create_shopify_collections_queryset_action'
    )

    changelist_actions = (
        'create_and_link_items_class_action',
    )

    change_actions = (
        'create_shopify_collections_object_action',
    )

    search_fields = (
        'id',
        'sema_root_category__category_id',
        'sema_root_category__name',
        'sema_branch_category__category_id',
        'sema_branch_category__name',
        'sema_leaf_category__category_id',
        'sema_leaf_category__name',
        'shopify_root_collection__id',
        'shopify_root_collection__collection_id',
        'shopify_root_collection__title',
        'shopify_branch_collection__id',
        'shopify_branch_collection__collection_id',
        'shopify_branch_collection__title',
        'shopify_leaf_collection__id',
        'shopify_leaf_collection__collection_id',
        'shopify_leaf_collection__title'
    )

    ordering = (
        'sema_root_category',
        'sema_branch_category',
        'sema_leaf_category'
    )

    list_display = (
        'detail_link',
        'id',
        'sema_root_category',
        'sema_branch_category',
        'sema_leaf_category',
        'may_be_relevant_flag',
        'is_relevant',
        'relevancy_warnings',
        'relevancy_errors',
        'relevancy_exception',
        'notes'
    )

    list_display_links = (
        'detail_link',
    )

    list_editable = (
        'is_relevant',
        'relevancy_exception'
    )

    list_filter = (
        'is_relevant',
        CategoryPathMayBeRelevant,
        CategoryPathIsComplete,
        HasSemaRootCategory,
        HasSemaBranchCategory,
        HasSemaLeafCategory,
        HasShopifyRootCollection,
        HasShopifyBranchCollection,
        HasShopifyLeafCollection
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    'may_be_relevant_flag',
                    'is_relevant',
                    'relevancy_warnings',
                    'relevancy_errors',
                    'relevancy_exception',
                    'id'
                )
            }
        ),
        (
            'Root', {
                'fields': (
                    'sema_root_category_link',
                    'sema_root_category',
                    'shopify_root_collection_link',
                    'shopify_root_collection'
                )
            }
        ),
        (
            'Branch', {
                'fields': (
                    'sema_branch_category_link',
                    'sema_branch_category',
                    'shopify_branch_collection_link',
                    'shopify_branch_collection'
                )
            }
        ),
        (
            'Leaf', {
                'fields': (
                    'sema_leaf_category_link',
                    'sema_leaf_category',
                    'shopify_leaf_collection_link',
                    'shopify_leaf_collection'
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
        'relevancy_warnings',
        'relevancy_errors',
        'detail_link',
        'sema_root_category_link',
        'sema_branch_category_link',
        'sema_leaf_category_link',
        'shopify_root_collection_link',
        'shopify_branch_collection_link',
        'shopify_leaf_collection_link'
    )

    autocomplete_fields = (
        'sema_root_category',
        'shopify_root_collection',
        'sema_branch_category',
        'shopify_branch_collection',
        'sema_leaf_category',
        'shopify_leaf_collection'
    )

    def detail_link(self, obj):
        return get_change_view_link(obj, 'Details')
    detail_link.short_description = ''

    def sema_root_category_link(self, obj):
        if not obj or not obj.pk or not obj.sema_root_category:
            return None

        return get_change_view_link(
            obj.sema_root_category,
            'See Full SEMA Root Category'
        )
    sema_root_category_link.short_description = ''

    def sema_branch_category_link(self, obj):
        if not obj or not obj.pk or not obj.sema_branch_category:
            return None

        return get_change_view_link(
            obj.sema_branch_category,
            'See Full SEMA Branch Category'
        )
    sema_branch_category_link.short_description = ''

    def sema_leaf_category_link(self, obj):
        if not obj or not obj.pk or not obj.sema_leaf_category:
            return None

        return get_change_view_link(
            obj.sema_leaf_category,
            'See Full SEMA Leaf Category'
        )
    sema_leaf_category_link.short_description = ''

    def shopify_root_collection_link(self, obj):
        if not obj or not obj.pk or not obj.shopify_root_collection:
            return None

        return get_change_view_link(
            obj.shopify_root_collection,
            'See Full Shopify Root Collection'
        )
    shopify_root_collection_link.short_description = ''

    def shopify_branch_collection_link(self, obj):
        if not obj or not obj.pk or not obj.shopify_branch_collection:
            return None

        return get_change_view_link(
            obj.shopify_branch_collection,
            'See Full Shopify Branch Collection'
        )
    shopify_branch_collection_link.short_description = ''

    def shopify_leaf_collection_link(self, obj):
        if not obj or not obj.pk or not obj.shopify_leaf_collection:
            return None

        return get_change_view_link(
            obj.shopify_leaf_collection,
            'See Full Shopify Leaf Collection'
        )
    shopify_leaf_collection_link.short_description = ''

    def may_be_relevant_flag(self, obj):
        if not obj or not obj.pk:
            return None

        if obj.is_relevant != obj.may_be_relevant:
            return '~'
        else:
            return ''
    may_be_relevant_flag.short_description = ''

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return (
                (
                    None, {
                        'fields': (
                            'sema_root_category',
                            'shopify_root_collection',
                            'sema_branch_category',
                            'shopify_branch_collection',
                            'sema_leaf_category',
                            'shopify_leaf_collection',
                            'notes'
                        )
                    }
                )
            )

        return super().get_fieldsets(request, obj)
