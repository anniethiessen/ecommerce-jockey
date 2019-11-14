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
    CategoryPathMayBeRelevant,
    HasSemaProduct,
    HasShopifyProduct,
    IsCompleteItem
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
        'mark_as_irrelevant_queryset_action'
    )

    search_fields = (
        'premier_manufacturer__name',
        'sema_brand__brand_id',
        'sema_brand__name',
        'shopify_vendor__name'
        'slug'
    )

    changelist_actions = (
        'check_unlinked_vendors_class_action',
    )

    list_display = (
        'details_link',
        'id',
        'slug',
        'premier_manufacturer',
        'sema_brand',
        'shopify_vendor',
        'may_be_relevant_flag',
        'is_relevant',
        'relevancy_errors',
        'notes'
    )

    list_display_links = (
        'details_link',
    )

    list_editable = (
        'is_relevant',
    )

    list_filter = (
        'is_relevant',
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    'may_be_relevant_flag',
                    'is_relevant',
                    'relevancy_errors'
                )
            }
        ),
        (
            'Vendor', {
                'fields': (
                    'id',
                    'slug'
                )
            }
        ),
        (
            'Premier Manufacturer', {
                'fields': (
                    'premier_manufacturer_link',
                    'premier_manufacturer',
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
        'relevancy_errors',
        'may_be_relevant_flag',
        'id',
        'details_link',
        'premier_manufacturer_link',
        'shopify_vendor_link',
        'sema_brand_link'
    )

    autocomplete_fields = (
        'premier_manufacturer',
        'sema_brand',
        'shopify_vendor'
    )

    def details_link(self, obj):
        return get_change_view_link(obj, 'Details')
    details_link.short_description = ''

    def premier_manufacturer_link(self, obj):
        return get_change_view_link(
            obj.premier_manufacturer, 'See full Premier manufacturer')
    premier_manufacturer_link.short_description = ''

    def sema_brand_link(self, obj):
        return get_change_view_link(
            obj.sema_brand, 'See full SEMA brand')
    sema_brand_link.short_description = ''

    def shopify_vendor_link(self, obj):
        return get_change_view_link(
            obj.shopify_vendor, 'See full Shopify vendor')
    shopify_vendor_link.short_description = ''

    def may_be_relevant_flag(self, obj):
        if obj.is_relevant != obj.may_be_relevant:
            return '~'
        else:
            return ''
    may_be_relevant_flag.short_description = ''


@admin.register(Item)
class ItemModelAdmin(ObjectActions, ModelAdmin, ItemActions):
    actions = (
        'create_shopify_products_queryset_action',
        'mark_as_relevant_queryset_action',
        'mark_as_irrelevant_queryset_action'
    )

    changelist_actions = (
        'create_and_link_items_class_action',
    )

    change_actions = (
        'create_shopify_products_object_action',
    )

    list_select_related = (
        'premier_product',
        'sema_product',
        'shopify_product'
    )

    search_fields = (
        'premier_product__premier_part_number',
        'premier_product__vendor_part_number',
        'premier_product__description',
        'premier_product__manufacturer__name',
        'premier_product__upc',
        'sema_product__dataset__brand__brand_id',
        'sema_product__dataset__brand__name',
        'sema_product__dataset__dataset_id',
        'sema_product__dataset__name',
        'sema_product__product_id',
        'sema_product__part_number',
        'shopify_product__product_id',
        'shopify_product__title',
        'shopify_product__body_html',
        'shopify_product__vendor__name',
        'shopify_product__seo_title',
        'shopify_product__seo_description',
        'id'
    )

    list_display = (
        'details_link',
        'id',
        'premier_product',
        'sema_product',
        'shopify_product',
        'may_be_relevant_flag',
        'is_relevant',
        'relevancy_errors',
        'notes'
    )

    list_display_links = (
        'details_link',
    )

    list_editable = (
        'is_relevant',
    )

    list_filter = (
        'is_relevant',
        IsCompleteItem,
        HasSemaProduct,
        HasShopifyProduct
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    'may_be_relevant_flag',
                    'is_relevant',
                    'relevancy_errors'
                )
            }
        ),
        (
            'Item', {
                'fields': (
                    'id',
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
        'may_be_relevant_flag',
        'relevancy_errors',
        'details_link',
        'id',
        'premier_product_link',
        'sema_product_link',
        'shopify_product_link'
    )

    autocomplete_fields = (
        'premier_product',
        'sema_product',
        'shopify_product'
    )

    def details_link(self, obj):
        return get_change_view_link(obj, 'Details')
    details_link.short_description = ''

    def premier_product_link(self, obj):
        if not obj.premier_product:
            return '-----'
        return get_change_view_link(
            obj.premier_product, 'See full Premier product')
    details_link.short_description = ''

    def sema_product_link(self, obj):
        if not obj.sema_product:
            return '-----'
        return get_change_view_link(
            obj.sema_product, 'See full SEMA product')
    sema_product_link.short_description = ''

    def shopify_product_link(self, obj):
        if not obj.shopify_product:
            return '-----'
        return get_change_view_link(
            obj.shopify_product, 'See full Shopify product')
    shopify_product_link.short_description = ''

    def may_be_relevant_flag(self, obj):
        if obj.is_relevant != obj.may_be_relevant:
            return '~'
        else:
            return ''
    may_be_relevant_flag.short_description = ''


@admin.register(CategoryPath)
class CategoryPathModelAdmin(ObjectActions, ModelAdmin, CategoryPathActions):
    actions = (
        'create_shopify_collections_queryset_action',
        'mark_as_relevant_queryset_action',
        'mark_as_irrelevant_queryset_action'
    )

    changelist_actions = (
        'create_and_link_items_class_action',
    )

    change_actions = (
        'create_shopify_collections_object_action',
    )

    list_select_related = (
        'sema_root_category',
        'sema_branch_category',
        'sema_leaf_category'
    )

    ordering = (
        'sema_root_category',
        'sema_branch_category',
        'sema_leaf_category'
    )

    search_fields = (
        'id',
    )

    list_display = (
        'details_link',
        'id',
        'sema_root_category',
        'sema_branch_category',
        'sema_leaf_category',
        'shopify_collection_count',
        'may_be_relevant_flag',
        'is_relevant',
        'relevancy_errors',
        'notes'
    )

    list_display_links = (
        'details_link',
    )

    list_editable = (
        'is_relevant',
    )

    list_filter = (
        'is_relevant',
        CategoryPathMayBeRelevant,
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    'may_be_relevant_flag',
                    'is_relevant',
                    'relevancy_errors'
                )
            }
        ),
        (
            'Path', {
                'fields': (
                    'id',
                )
            }
        ),
        (
            'SEMA Root Category', {
                'fields': (
                    'sema_root_category_link',
                    'sema_root_category'
                )
            }
        ),
        (
            'SEMA Branch Category', {
                'fields': (
                    'sema_branch_category_link',
                    'sema_branch_category'
                )
            }
        ),
        (
            'SEMA Leaf Category', {
                'fields': (
                    'sema_leaf_category_link',
                    'sema_leaf_category'
                )
            }
        ),
        (
            'Shopify Collections', {
                'fields': (
                    'shopify_collections',
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
        'details_link',
        'may_be_relevant_flag',
        'relevancy_errors',
        'id',
        'sema_root_category_link',
        'sema_branch_category_link',
        'sema_leaf_category_link',
        'shopify_collection_count'
    )

    autocomplete_fields = (
        'sema_root_category',
        'sema_branch_category',
        'sema_leaf_category',
        'shopify_collections'
    )

    def details_link(self, obj):
        return get_change_view_link(obj, 'Details')
    details_link.short_description = ''

    def sema_root_category_link(self, obj):
        if not obj.sema_root_category:
            return '-----'
        return get_change_view_link(
            obj.sema_root_category, 'See full SEMA root category')
    sema_root_category_link.short_description = ''

    def sema_branch_category_link(self, obj):
        if not obj.sema_branch_category:
            return '-----'
        return get_change_view_link(
            obj.sema_branch_category, 'See full SEMA branch category')
    sema_branch_category_link.short_description = ''

    def sema_leaf_category_link(self, obj):
        if not obj.sema_leaf_category:
            return '-----'
        return get_change_view_link(
            obj.sema_leaf_category, 'See full SEMA leaf category')
    sema_leaf_category_link.short_description = ''

    def may_be_relevant_flag(self, obj):
        if obj.is_relevant != obj.may_be_relevant:
            return '~'
        else:
            return ''
    may_be_relevant_flag.short_description = ''
