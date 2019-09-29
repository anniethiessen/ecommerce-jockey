from django_object_actions import BaseDjangoObjectActions as ObjectActions
from import_export.admin import ImportMixin

from django.contrib import admin
from django.contrib.admin import ModelAdmin

from ..models import (
    PremierProduct,
    # SemaBaseVehicle,  # TO DO TEMP
    SemaBrand,
    SemaDataset,
    SemaMake,
    SemaModel,
    SemaProduct,
    SemaSubmodel,
    # SemaVehicle,  # TO DO TEMP
    SemaYear
)
from .actions import (
    PremierProductActions,
    SemaBrandActions,
    SemaDatasetActions
)
from .filters import (
    HasAlbertaInventory,
    HasMissingInventory,
    HasMissingPricing
)
from .inlines import SemaDatasetTabularInline
from .resources import PremierProductResource
from .utils import get_change_view_link


@admin.register(PremierProduct)
class PremierProductModelAdmin(ImportMixin, ObjectActions,
                               ModelAdmin, PremierProductActions):
    resource_class = PremierProductResource

    search_fields = (
        'premier_part_number',
        'vendor_part_number',
        'description',
        'manufacturer',
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
        'map'
    )

    list_display_links = (
        'details_link',
    )

    list_filter = (
        'manufacturer',
        'part_status',
        HasMissingInventory,
        HasMissingPricing,
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
        'product_link'
    )

    def details_link(self, obj):
        return get_change_view_link(obj, 'Details')
    details_link.short_description = ''

    def product_link(self, obj):
        return get_change_view_link(obj.product, 'See full product')
    product_link.short_description = ''


@admin.register(SemaYear)
class SemaYearModelAdmin(ModelAdmin):
    search_fields = (
        'year',
    )

    list_display = (
        'details_link',
        'year'
    )

    list_display_links = (
        'details_link',
    )

    list_filter = (
        'year',
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    'year',
                )
            }
        ),
    )

    readonly_fields = (
        'details_link',
    )

    def details_link(self, obj):
        return get_change_view_link(obj, 'Details')
    details_link.short_description = ''


@admin.register(SemaMake)
class SemaMakeModelAdmin(ModelAdmin):
    search_fields = (
        'make_id',
        'name',
    )

    list_display = (
        'details_link',
        'make_id',
        'name'
    )

    list_display_links = (
        'details_link',
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    'make_id',
                    'name'
                )
            }
        ),
    )

    readonly_fields = (
        'details_link',
    )

    def details_link(self, obj):
        return get_change_view_link(obj, 'Details')
    details_link.short_description = ''


@admin.register(SemaModel)
class SemaModelModelAdmin(ModelAdmin):
    search_fields = (
        'make__make_id',
        'make__name',
        # 'base_vehicle__base_vehicle_id',  # TO DO TEMP
        'model_id',
        'base_vehicle_id',  # TO DO TEMP
        'name'
    )

    list_display = (
        'details_link',
        'model_id',
        'base_vehicle_id',  # TO DO TEMP
        'name',
        'make',
        # 'base_vehicle'  # TO DO TEMP
    )

    list_display_links = (
        'details_link',
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    'model_id',
                    'base_vehicle_id',  # TO DO TEMP
                    'name',
                )
            }
        ),
        (
            'Make', {
                'fields': (
                    'make_link',
                    'make'
                )
            }
        )
        # (
        #     'Base Vehicle', {  # TO DO TEMP
        #         'fields': (
        #             'base_vehicle_link',
        #             'base_vehicle'
        #         )
        #     }
        # )
    )

    readonly_fields = (
        'details_link',
        'make_link'
        # 'base_vehicle_link'  # TO DO TEMP
    )

    def details_link(self, obj):
        return get_change_view_link(obj, 'Details')
    details_link.short_description = ''

    def make_link(self, obj):
        if not obj.make:
            return None
        return get_change_view_link(
            obj.make, 'See full make')
    make_link.short_description = ''

    # def base_vehicle_link(self, obj):  # TO DO TEMP
    #     if not obj.base_vehicle:
    #         return None
    #     return get_change_view_link(
    #         obj.base_vehicle, 'See full base vehicle')
    # base_vehicle_link.short_description = ''


@admin.register(SemaSubmodel)
class SemaSubmodelModelAdmin(ModelAdmin):
    search_fields = (
        'model__make__make_id',
        'model__make__name',
        'model__model_id',
        'model__base_vehicle_id',  # TO DO TEMP
        'model__name',
        # 'model__base_vehicle__base_vehicle_id',  # TO DO TEMP
        # 'vehicle__vehicle_id',  # TO DO TEMP
        'submodel_id',
        'vehicle_id',  # TO DO TEMP
        'name'
    )

    list_display = (
        'details_link',
        'submodel_id',
        'vehicle_id',  # TO DO TEMP
        'name',
        'model'
        # 'vehicle'  # TO DO TEMP
    )

    list_display_links = (
        'details_link',
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    'submodel_id',
                    'vehicle_id',  # TO DO TEMP
                    'name'
                )
            }
        ),
        (
            'Model', {
                'fields': (
                    'model_link',
                    'model'
                )
            }
        )
        # (
        #     'Vehicle', {  # TO DO TEMP
        #         'fields': (
        #             'vehicle_link',
        #             'vehicle'
        #         )
        #     }
        # )
    )

    readonly_fields = (
        'details_link',
        'model_link'
        # 'vehicle_link'  # TO DO TEMP
    )

    def details_link(self, obj):
        return get_change_view_link(obj, 'Details')
    details_link.short_description = ''

    def model_link(self, obj):
        if not obj.model:
            return None
        return get_change_view_link(
            obj.model, 'See full model')
    model_link.short_description = ''

    # def vehicle_link(self, obj):  # TO DO TEMP
    #     if not obj.vehicle:
    #         return None
    #     return get_change_view_link(
    #         obj.vehicle, 'See full vehicle')
    # vehicle_link.short_description = ''


@admin.register(SemaBrand)
class SemaBrandModelAdmin(ObjectActions, ModelAdmin, SemaBrandActions):
    search_fields = (
        'brand_id',
        'name'
    )

    changelist_actions = (
        'import_brands_class_action',
    )

    list_display = (
        'details_link',
        'brand_id',
        'name',
        'dataset_count'
    )

    list_display_links = (
        'details_link',
    )

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

    inlines = (
        SemaDatasetTabularInline,
    )

    readonly_fields = (
        'dataset_count',
    )

    def details_link(self, obj):
        return get_change_view_link(obj, 'Details')
    details_link.short_description = ''


@admin.register(SemaDataset)
class SemaDatasetModelAdmin(ObjectActions, ModelAdmin, SemaDatasetActions):
    search_fields = (
        'brand__brand_id',
        'brand__name',
        'dataset_id',
        'name'
    )

    changelist_actions = (
        'import_datasets_class_action',
    )

    change_actions = (
        'import_products_object_action',
    )

    list_display = (
        'details_link',
        'dataset_id',
        'name',
        'brand',
        'is_authorized'
    )

    list_display_links = (
        'details_link',
    )

    list_filter = (
        'is_authorized',
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    'dataset_id',
                    'name',
                    'is_authorized'
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
        'part_number'
    )

    list_display = (
        'details_link',
        'product_id',
        'part_number',
        'dataset'
    )

    list_display_links = (
        'details_link',
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    'product_id',
                    'part_number'
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
