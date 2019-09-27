from import_export.admin import ImportMixin

from django.contrib import admin
from django.contrib.admin import ModelAdmin

from ..models import (
    PremierProduct,
    SemaBrand,
    SemaDataset,
    SemaProduct
)
from .actions import PremierAPIActions
from .filters import (
    HasAlbertaInventory,
    HasMissingInventory
)
from .resources import PremierProductResource
from .utils import get_change_view_link


@admin.register(SemaBrand)
class SemaBrandModelAdmin(ModelAdmin):
    search_fields = (
        'brand_id',
        'name'
    )

    # actions = ()

    list_display = (
        'details_link',
        'brand_id',
        'name'
    )

    list_display_links = (
        'details_link',
    )

    # list_filter = ()

    fieldsets = (
        (
            None, {
                'fields': (
                    'brand_id',
                    'name'
                )
            }
        ),
    )

    # readonly_fields = ()

    def details_link(self, obj):
        return get_change_view_link(obj, 'Details')
    details_link.short_description = ''


@admin.register(SemaDataset)
class SemaDatasetModelAdmin(ModelAdmin):
    search_fields = (
        'brand__brand_id',
        'brand__name',
        'dataset_id',
        'name'
    )

    # actions = ()

    list_display = (
        'details_link',
        'dataset_id',
        'name',
        'brand'
    )

    list_display_links = (
        'details_link',
    )

    # list_filter = ()

    fieldsets = (
        (
            None, {
                'fields': (
                    'dataset_id',
                    'name'
                )
            }
        ),
        (
            'Brand', {
                'fields': (
                    'brand_link',
                    'brand'
                )
            }
        )
    )

    readonly_fields = (
        'details_link',
        'brand_link'
    )

    def details_link(self, obj):
        return get_change_view_link(obj, 'Details')
    details_link.short_description = ''

    def brand_link(self, obj):
        if not obj.brand:
            return None
        return get_change_view_link(
            obj.brand, 'See full brand')
    brand_link.short_description = ''


@admin.register(SemaProduct)
class SemaProductModelAdmin(ModelAdmin):
    search_fields = (
        'dataset__brand__brand_id',
        'dataset__brand__name',
        'dataset__dataset_id',
        'dataset__name',
        'product_id',
    )

    # actions = ()

    list_display = (
        'details_link',
        'product_id',
        'dataset'
    )

    list_display_links = (
        'details_link',
    )

    # list_filter = ()

    fieldsets = (
        (
            None, {
                'fields': (
                    'product_id',
                )
            }
        ),
        (
            'Dataset', {
                'fields': (
                    'dataset_link',
                    'dataset'
                )
            }
        ),
        (
            'Brand', {
                'fields': (
                    'brand_link',
                    'brand_a'
                )
            }
        )
    )

    readonly_fields = (
        'details_link',
        'dataset_link',
        'brand_link',
        'brand_a'
    )

    def details_link(self, obj):
        return get_change_view_link(obj, 'Details')
    details_link.short_description = ''

    def dataset_link(self, obj):
        return get_change_view_link(obj.dataset, 'See full dataset')
    dataset_link.short_description = ''

    def brand_link(self, obj):
        return get_change_view_link(obj.dataset.brand, 'See full brand')
    brand_link.short_description = ''

    def brand_a(self, obj):
        return str(obj.dataset.brand)
    brand_a.short_description = 'brand'


@admin.register(PremierProduct)
class PremierProductModelAdmin(ImportMixin, ModelAdmin, PremierAPIActions):
    resource_class = PremierProductResource
    list_per_page = 10
    search_fields = (
        'premier_part_number',
        'vendor_part_number',
        'description',
        'manufacturer',
        'upc'
    )

    actions = (
        'update_inventory_action',
    )

    list_display = (
        'details_link',
        'premier_part_number',
        'vendor_part_number',
        'description',
        'manufacturer',
        'msrp',
        'map',
        'jobber',
        'cost',
        'part_status',
        'weight',
        'length',
        'width',
        'height',
        'upc',
        'inventory_ab',
        'inventory_po',
        'inventory_ut',
        'inventory_ky',
        'inventory_tx',
        'inventory_ca',
        'inventory_wa',
        'inventory_co'
    )

    list_display_links = (
        'details_link',
    )

    list_filter = (
        'manufacturer',
        'part_status',
        HasMissingInventory,
        HasAlbertaInventory
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    'premier_part_number',
                )
            }
        ),
        (
            'Details', {
                'fields': (
                    'description',
                    'manufacturer',
                    'vendor_part_number',
                    'part_status',
                    'upc'
                )
            }
        ),
        (
            'Prices', {
                'fields': (
                    'msrp',
                    'map',
                    'jobber',
                    'cost'
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
        'product_link'
    )

    def details_link(self, obj):
        return get_change_view_link(obj, 'Details')
    details_link.short_description = ''

    def product_link(self, obj):
        return get_change_view_link(obj.product, 'See full product')
    product_link.short_description = ''
