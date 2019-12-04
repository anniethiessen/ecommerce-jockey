from django_object_actions import BaseDjangoObjectActions as ObjectActions
from imagekit.admin import AdminThumbnail
from import_export.admin import ImportMixin

from django.contrib import admin
from django.contrib.admin import ModelAdmin

from core.admin.utils import (
    get_change_view_link,
    get_custom_filter_title
)
from ..models import (
    PremierManufacturer,
    PremierProduct,
)
from .actions import (
    PremierManufacturerActions,
    PremierProductActions
)
from .filters import (
    HasAlbertaInventory,
    HasApiInventory,
    HasApiPricing,
    HasItem,
    HasPrimaryImage,
    HasSemaBrand,
    HasSemaProduct,
    HasShopifyProduct,
    HasShopifyVendor,
    HasVendor,
    PremierProductMayBeRelevant
)
from .inlines import PremierManufacturerProductsTabularInline
from .resources import PremierProductResource


@admin.register(PremierManufacturer)
class PremierManufacturerModelAdmin(ObjectActions, ModelAdmin,
                                    PremierManufacturerActions):
    actions = (
        'mark_as_relevant_queryset_action',
        'mark_as_irrelevant_queryset_action'
    )

    search_fields = (
        'id',
        'name'
    )

    list_display = (
        'detail_link',
        'id',
        'name',
        'product_count',
        'primary_image_preview',
        'is_relevant',
        'relevancy_warnings',
        'relevancy_errors'
    )

    list_display_links = (
        'detail_link',
    )

    list_editable = (
        'is_relevant',
    )

    list_filter = (
        'is_relevant',
        HasVendor,
        HasSemaBrand,
        HasShopifyVendor
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    'vendor_link',
                    'sema_brand_link',
                    'shopify_vendor_link',
                    'is_relevant',
                    'relevancy_warnings',
                    'relevancy_errors',
                    'id'
                )
            }
        ),
        (
            'Manufacturer', {
                'fields': (
                    'name',
                )
            }
        ),
        (
            'Images', {
                'fields': (
                    ('primary_image', 'primary_image_preview'),
                )
            }
        )
    )

    readonly_fields = (
        'id',
        'relevancy_warnings',
        'relevancy_errors',
        'primary_image_preview',
        'detail_link',
        'vendor_link',
        'sema_brand_link',
        'shopify_vendor_link',
        'product_count'
    )

    inlines = (
        PremierManufacturerProductsTabularInline,  # TO NOTE: too long
    )

    def detail_link(self, obj):
        return get_change_view_link(obj, 'Details')
    detail_link.short_description = ''

    def vendor_link(self, obj):
        if not obj or not obj.pk or not hasattr(obj, 'vendor'):
            return None

        return get_change_view_link(obj.vendor, 'See Vendor')
    vendor_link.short_description = ''

    def sema_brand_link(self, obj):
        if (not obj or not obj.pk or not hasattr(obj, 'vendor')
                or not obj.vendor.sema_brand):
            return None

        return get_change_view_link(
            obj.vendor.sema_brand,
            'See SEMA brand'
        )
    sema_brand_link.short_description = ''

    def shopify_vendor_link(self, obj):
        if (not obj or not obj.pk or not hasattr(obj, 'vendor')
                or not obj.vendor.shopify_vendor):
            return None

        return get_change_view_link(
            obj.vendor.shopify_vendor,
            'See Shopify vendor'
        )
    shopify_vendor_link.short_description = ''

    def product_count(self, obj):
        return f'{obj._product_relevant_count}/{obj._product_count}'
    product_count.admin_order_field = '_product_relevant_count'
    product_count.short_description = 'product count'

    primary_image_preview = AdminThumbnail(
        image_field='primary_image_thumbnail'
    )
    primary_image_preview.short_description = 'primary image'

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


@admin.register(PremierProduct)
class PremierProductModelAdmin(ImportMixin, ObjectActions,
                               ModelAdmin, PremierProductActions):
    resource_class = PremierProductResource

    list_select_related = (
        'manufacturer',
    )

    actions = (
        'mark_as_relevant_queryset_action',
        'mark_as_irrelevant_queryset_action',
        'update_inventory_queryset_action',
        'update_pricing_queryset_action',
        'update_primary_image_queryset_action'
    )

    search_fields = (
        'premier_part_number',
        'vendor_part_number',
        'description',
        'upc',
        'manufacturer__id',
        'manufacturer__name',
    )

    list_display = (
        'detail_link',
        'premier_part_number',
        'vendor_part_number',
        'description',
        'manufacturer',
        'inventory_ab',
        'cost_cad',
        'primary_image_preview',
        'may_be_relevant_flag',
        'is_relevant',
        'relevancy_warnings',
        'relevancy_errors'
    )

    list_display_links = (
        'detail_link',
    )

    list_editable = (
        'is_relevant',
    )

    list_filter = (
        'is_relevant',
        PremierProductMayBeRelevant,
        ('manufacturer__name', get_custom_filter_title('manufacturer')),
        'part_status',
        HasItem,
        HasSemaProduct,
        HasShopifyProduct,
        HasApiInventory,
        HasApiPricing,
        HasAlbertaInventory,
        HasPrimaryImage
    )

    change_actions = (
        'update_inventory_object_action',
        'update_pricing_object_action',
        'update_primary_image_object_action'
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    'item_link',
                    'sema_product_link',
                    'shopify_product_link',
                    'may_be_relevant_flag',
                    'is_relevant',
                    'relevancy_warnings',
                    'relevancy_errors'
                )
            }
        ),
        (
            'Product', {
                'fields': (
                    'premier_part_number',
                    'vendor_part_number',
                    'description',
                    'part_status',
                    'upc'
                )
            }
        ),
        (
            'Manufacturer', {
                'fields': (
                    'manufacturer_link',
                    'manufacturer'
                ),
                'classes': (
                    'collapse',
                )
            }
        ),
        (
            'Pricing', {
                'fields': (
                    'cost',
                    'cost_cad',
                    'cost_usd',
                    'jobber',
                    'jobber_cad',
                    'jobber_usd',
                    'msrp',
                    'msrp_cad',
                    'msrp_usd',
                    'map',
                    'map_cad',
                    'map_usd'
                ),
                'classes': (
                    'collapse',
                ),
            }
        ),
        (
            'Dimensions', {
                'fields': (
                    'weight',
                    'length',
                    'width',
                    'height'
                ),
                'classes': (
                    'collapse',
                ),
            }
        ),
        (
            'Inventory', {
                'fields': (
                    'inventory_ab',
                    'inventory_po',
                    'inventory_ut',
                    'inventory_ky',
                    'inventory_tx',
                    'inventory_ca',
                    'inventory_wa',
                    'inventory_co'
                ),
                'classes': (
                    'collapse',
                )
            }
        ),
        (
            'Images', {
                'fields': (
                    ('primary_image', 'primary_image_preview'),
                )
            }
        )
    )

    readonly_fields = (
        'relevancy_warnings',
        'relevancy_errors',
        'may_be_relevant_flag',
        'primary_image_preview',
        'detail_link',
        'manufacturer_link',
        'item_link',
        'sema_product_link',
        'shopify_product_link'
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

    def sema_product_link(self, obj):
        if (not obj or not obj.pk or not hasattr(obj, 'item')
                or not obj.item.sema_product):
            return None

        return get_change_view_link(
            obj.item.sema_product,
            'See SEMA product'
        )
    sema_product_link.short_description = ''

    def shopify_product_link(self, obj):
        if (not obj or not obj.pk or not hasattr(obj, 'item')
                or not obj.item.shopify_product):
            return None

        return get_change_view_link(
            obj.item.shopify_product,
            'See Shopify product'
        )
    shopify_product_link.short_description = ''

    def manufacturer_link(self, obj):
        if not obj or not obj.pk or not obj.manufacturer:
            return None

        return get_change_view_link(
            obj.manufacturer,
            'See Full Manufacturer'
        )
    manufacturer_link.short_description = ''

    primary_image_preview = AdminThumbnail(
        image_field='primary_image_thumbnail'
    )
    primary_image_preview.short_description = 'primary image'

    def may_be_relevant_flag(self, obj):
        if obj.is_relevant != obj.may_be_relevant:
            return '~'
        else:
            return ''
    may_be_relevant_flag.short_description = ''

    def get_queryset(self, request):
        return super().get_queryset(request).with_admin_data()

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return (
                (
                    None, {
                        'fields': (
                            'premier_part_number',
                            'vendor_part_number',
                            'manufacturer',
                            'description',
                            'part_status',
                            'upc',
                            'cost',
                            'jobber',
                            'msrp',
                            'map',
                            'weight',
                            'length',
                            'width',
                            'height'
                        )
                    }
                ),
            )

        return super().get_fieldsets(request, obj)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)

        if not request.user.is_superuser:
            readonly_fields += (
                'premier_part_number',
            )

        return readonly_fields
