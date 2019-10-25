from django_object_actions import BaseDjangoObjectActions as ObjectActions
from imagekit.admin import AdminThumbnail
from import_export.admin import ImportMixin

from django.contrib import admin
from django.contrib.admin import ModelAdmin

from core.admin.utils import (
    get_change_view_link,
    get_custom_filter_title
)
from core.admin.filters import MayBeRelevantFilter
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
    HasPrimaryImage
)
# from .inlines import PremierProductTabularInline
from .resources import PremierProductResource


@admin.register(PremierManufacturer)
class PremierManufacturerModelAdmin(ObjectActions, ModelAdmin,
                                    PremierManufacturerActions):
    search_fields = (
        'name',
    )

    actions = (
        'mark_as_relevant_queryset_action',
        'mark_as_irrelevant_queryset_action'
    )

    list_display = (
        'details_link',
        'id',
        'name',
        'product_count',
        'primary_image_preview',
        'is_relevant',
        'relevancy_errors_flag',
        'relevancy_errors'
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
                    'name'
                )
            }
        ),
        (
            'Images', {
                'fields': (
                    ('primary_image', 'primary_image_preview'),
                )
            }
        ),
    )

    readonly_fields = (
        'id',
        'relevancy_errors_flag',
        'relevancy_errors',
        'product_count',
        'details_link',
        'primary_image_preview'
    )

    # inlines = (
    #     PremierProductTabularInline,  # TO NOTE: too long
    # )

    def details_link(self, obj):
        return get_change_view_link(obj, 'Details')
    details_link.short_description = ''

    primary_image_preview = AdminThumbnail(
        image_field='primary_image_thumbnail'
    )
    primary_image_preview.short_description = 'primary image'

    def relevancy_errors_flag(self, obj):
        return obj._relevancy_errors_flag
    relevancy_errors_flag.admin_order_field = '_relevancy_errors_flag'
    relevancy_errors_flag.short_description = ''

    def get_queryset(self, request):
        return super().get_queryset(request).with_relevancy_values()


@admin.register(PremierProduct)
class PremierProductModelAdmin(ImportMixin, ObjectActions,
                               ModelAdmin, PremierProductActions):
    resource_class = PremierProductResource

    list_select_related = (
        'manufacturer',
    )

    search_fields = (
        'premier_part_number',
        'vendor_part_number',
        'description',
        'manufacturer__name',
        'upc'
    )

    actions = (
        'update_inventory_queryset_action',
        'update_pricing_queryset_action',
        'mark_as_relevant_queryset_action',
        'mark_as_irrelevant_queryset_action',
        'update_primary_image_queryset_action'
    )

    change_actions = (
        'update_inventory_object_action',
        'update_pricing_object_action',
        'update_primary_image_object_action'
    )

    list_display = (
        'details_link',
        'premier_part_number',
        'vendor_part_number',
        'description',
        'manufacturer',
        'cost',
        'jobber',
        'msrp',
        'map',
        'primary_image_preview',
        'is_relevant',
        'relevancy_errors_flag',
        'relevancy_errors'
    )

    list_display_links = (
        'details_link',
    )

    list_editable = (
        'is_relevant',
    )

    list_filter = (
        'is_relevant',
        MayBeRelevantFilter,
        HasItem,
        ('manufacturer__name', get_custom_filter_title('manufacturer')),
        'part_status',
        HasApiInventory,
        HasApiPricing,
        HasAlbertaInventory,
        HasPrimaryImage
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    'item_link',
                    'is_relevant',
                    'premier_part_number',
                    'description',
                    'vendor_part_number',
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
        'relevancy_errors',
        'relevancy_errors_flag',
        'details_link',
        'manufacturer_link',
        'item_link',
        'primary_image_preview'
    )

    def details_link(self, obj):
        return get_change_view_link(obj, 'Details')
    details_link.short_description = ''

    def item_link(self, obj):
        if not hasattr(obj, 'item'):
            return '-----'
        return get_change_view_link(obj.item, 'See full item')
    item_link.short_description = ''

    def manufacturer_link(self, obj):
        if not obj.manufacturer:
            return '-----'
        return get_change_view_link(
            obj.manufacturer,
            'See all full manufacturer'
        )
    manufacturer_link.short_description = ''

    primary_image_preview = AdminThumbnail(
        image_field='primary_image_thumbnail'
    )
    primary_image_preview.short_description = 'primary image'

    def relevancy_errors_flag(self, obj):
        return obj._relevancy_errors_flag
    relevancy_errors_flag.admin_order_field = '_relevancy_errors_flag'
    relevancy_errors_flag.short_description = ''

    def get_queryset(self, request):
        return super().get_queryset(request).with_relevancy_values()
