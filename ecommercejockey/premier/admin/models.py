from django_object_actions import BaseDjangoObjectActions as ObjectActions
from import_export.admin import ImportMixin

from django.contrib import admin
from django.contrib.admin import ModelAdmin

from core.admin.utils import get_change_view_link
from ..models import (
    PremierManufacturer,
    PremierProduct,
)
from .actions import PremierProductActions
from .filters import (
    HasAlbertaInventory,
    HasApiInventory,
    HasApiPricing,
    HasProduct
)
from .inlines import PremierProductTabularInline
from .resources import PremierProductResource


@admin.register(PremierManufacturer)
class PremierManufacturerModelAdmin(ModelAdmin):
    search_fields = (
        'name',
    )

    list_display = (
        'details_link',
        'id',
        'name',
        'product_count'
    )

    list_display_links = (
        'details_link',
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    'id',
                    'name'
                )
            }
        ),
    )

    readonly_fields = (
        'id',
        'product_count',
        'details_link'
    )

    inlines = (
        PremierProductTabularInline,
    )

    def details_link(self, obj):
        return get_change_view_link(obj, 'Details')
    details_link.short_description = ''


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
        'update_pricing_queryset_action'
    )

    change_actions = (
        'update_inventory_object_action',
        'update_pricing_object_action'
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
        HasProduct,
        'manufacturer__name',
        'part_status',
        HasApiInventory,
        HasApiPricing,
        HasAlbertaInventory
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
                )
            }
        ),
        (
            'Dimensions', {
                'fields': (
                    'weight',
                    'length',
                    'width',
                    'height'
                )
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
                )
            }
        )
    )

    readonly_fields = (
        'details_link',
        'manufacturer_link',
        'item_link'
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

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if not request.user.is_superuser:
            readonly_fields += (
                'premier_part_number',
                'description',
                'manufacturer',
                'vendor_part_number',
                'part_status',
                'upc',
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
                'map_usd',
                'weight',
                'length',
                'width',
                'height',
                'inventory_ab',
                'inventory_po',
                'inventory_ut',
                'inventory_ky',
                'inventory_tx',
                'inventory_ca',
                'inventory_wa',
                'inventory_co'
            )
        return readonly_fields
