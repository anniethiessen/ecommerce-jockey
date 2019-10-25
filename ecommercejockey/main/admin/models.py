from django_object_actions import BaseDjangoObjectActions as ObjectActions

from django.contrib import admin
from django.contrib.admin import ModelAdmin

from core.admin.utils import get_change_view_link
from ..models import (
    Item,
    Vendor
)
from .actions import (
    ItemActions,
    VendorActions
)
from .filters import (
    HasPremierProduct,
    HasSemaProduct,
    IsCompleteItem
)


@admin.register(Vendor)
class VendorModelAdmin(ObjectActions, ModelAdmin, VendorActions):
    list_select_related = (
        'premier_manufacturer',
        'sema_brand'
    )

    actions = (
        'mark_as_relevant_queryset_action',
        'mark_as_irrelevant_queryset_action'
    )

    search_fields = (
        'premier_manufacturer__name',
        'sema_brand__brand_id',
        'sema_brand__name',
        'slug'
    )

    changelist_actions = (
        'check_unlinked_vendors_class_action',
    )

    list_display = (
        'details_link',
        'id',
        'premier_manufacturer',
        'sema_brand',
        'slug',
        'is_relevant'
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
                    'is_relevant',
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
            None, {
                'fields': (
                    'sema_brand_link',
                    'sema_brand'
                )
            }
        ),
    )

    readonly_fields = (
        'id',
        'details_link',
        'premier_manufacturer_link',
        'sema_brand_link'
    )

    autocomplete_fields = (
        'premier_manufacturer',
        'sema_brand'
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


@admin.register(Item)
class ItemModelAdmin(ObjectActions, ModelAdmin, ItemActions):
    list_select_related = (
        'premier_product',
        'sema_product'
    )

    actions = (
        'mark_as_relevant_queryset_action',
        'mark_as_irrelevant_queryset_action'
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
        'id'
    )

    changelist_actions = (
        'create_items_class_action',
        'link_products_class_action'
    )

    list_display = (
        'details_link',
        'id',
        'premier_product',
        'sema_product',
        'notes',
        'is_relevant'
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
        HasPremierProduct,
        HasSemaProduct
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    'is_relevant',
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
            'Notes', {
                'fields': (
                    'notes',
                )
            }
        ),
    )

    readonly_fields = (
        'details_link',
        'id',
        'premier_product_link',
        'sema_product_link'
    )

    autocomplete_fields = (
        'premier_product',
        'sema_product'
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
    details_link.short_description = ''
