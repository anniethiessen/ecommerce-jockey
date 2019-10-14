from django_object_actions import BaseDjangoObjectActions as ObjectActions
from import_export.admin import ImportMixin

from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.utils.safestring import mark_safe

from ..models import (
    Manufacturer,
    PremierProduct,
    Product,
    SemaBaseVehicle,
    SemaBrand,
    SemaCategory,
    SemaDataset,
    SemaMake,
    SemaModel,
    SemaProduct,
    SemaSubmodel,
    SemaVehicle,
    SemaYear
)
from .actions import (
    ManufacturerActions,
    PremierProductActions,
    ProductActions,
    SemaBaseVehicleActions,
    SemaBrandActions,
    SemaCategoryActions,
    SemaDatasetActions,
    SemaMakeActions,
    SemaModelActions,
    SemaProductActions,
    SemaSubmodelActions,
    SemaVehicleActions,
    SemaYearActions
)
from .filters import (
    ByDecade,
    HasAlbertaInventory,
    HasMissingInventory,
    HasMissingHtml,
    HasMissingPricing,
    HasPremierProduct,
    HasProduct,
    HasSemaProduct
)
from .inlines import (
    SemaCategoryTabularInline,
    SemaDatasetTabularInline
)
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
        HasProduct,
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
                    'product_link',
                    'premier_part_number',
                    'description',
                    'manufacturer',
                    'vendor_part_number',
                    'part_status',
                    'upc'
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
        'product_link'
    )

    def details_link(self, obj):
        return get_change_view_link(obj, 'Details')
    details_link.short_description = ''

    def product_link(self, obj):
        if not hasattr(obj, 'product'):
            return '-----'
        return get_change_view_link(obj.product, 'See full product')
    product_link.short_description = ''


@admin.register(SemaYear)
class SemaYearModelAdmin(ObjectActions, ModelAdmin, SemaYearActions):
    search_fields = (
        'year',
    )

    changelist_actions = (
        'import_full_class_action',
        'import_new_class_action'
    )

    list_display = (
        'details_link',
        'year',
        'is_authorized'
    )

    list_display_links = (
        'details_link',
    )

    list_filter = (
        'is_authorized',
        ByDecade
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    'is_authorized',
                    'year'
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
class SemaMakeModelAdmin(ObjectActions, ModelAdmin, SemaMakeActions):
    search_fields = (
        'make_id',
        'name',
    )

    changelist_actions = (
        'import_full_class_action',
        'import_new_class_action'
    )

    list_display = (
        'details_link',
        'make_id',
        'name',
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
                    'is_authorized',
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
class SemaModelModelAdmin(ObjectActions, ModelAdmin, SemaModelActions):
    search_fields = (
        'model_id',
        'name'
    )

    changelist_actions = (
        'import_full_class_action',
        'import_new_class_action'
    )

    list_display = (
        'details_link',
        'model_id',
        'name',
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
                    'is_authorized',
                    'model_id',
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


@admin.register(SemaSubmodel)
class SemaSubmodelModelAdmin(ObjectActions, ModelAdmin, SemaSubmodelActions):
    search_fields = (
        'submodel_id',
        'name'
    )

    changelist_actions = (
        'import_full_class_action',
        'import_new_class_action'
    )

    list_display = (
        'details_link',
        'submodel_id',
        'name',
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
                    'is_authorized',
                    'submodel_id',
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


@admin.register(SemaBaseVehicle)
class SemaBaseVehicleModelAdmin(ObjectActions, ModelAdmin,
                                SemaBaseVehicleActions):
    search_fields = (
        'base_vehicle_id',
        'year__year',
        'make__make_id',
        'make__name',
        'model__model_id',
        'model__name'
    )

    changelist_actions = (
        'import_base_vehicles_class_action',
    )

    list_display = (
        'details_link',
        'base_vehicle_id',
        'year',
        'make',
        'model',
        'is_authorized'
    )

    list_display_links = (
        'details_link',
    )

    list_filter = (
        'is_authorized',
        'make',
        'model',
        'year'
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    'is_authorized',
                    'base_vehicle_id'
                )
            }
        ),
        (
            'Year', {
                'fields': (
                    'year_link',
                    'year'
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
        ),
        (
            'Model', {
                'fields': (
                    'model_link',
                    'model'
                )
            }
        )
    )

    readonly_fields = (
        'details_link',
        'year_link',
        'make_link',
        'model_link'
    )

    def details_link(self, obj):
        return get_change_view_link(obj, 'Details')
    details_link.short_description = ''

    def year_link(self, obj):
        if not obj.year:
            return None
        return get_change_view_link(obj.year, 'See full year')
    year_link.short_description = ''

    def make_link(self, obj):
        if not obj.make:
            return None
        return get_change_view_link(obj.make, 'See full make')
    make_link.short_description = ''

    def model_link(self, obj):
        if not obj.model:
            return None
        return get_change_view_link(obj.model, 'See full model')
    model_link.short_description = ''


@admin.register(SemaVehicle)
class SemaVehicleModelAdmin(ObjectActions, ModelAdmin, SemaVehicleActions):
    search_fields = (
        'base_vehicle__base_vehicle_id',
        'base_vehicle__year__year',
        'base_vehicle__make__make_id',
        'base_vehicle__make__name',
        'base_vehicle__model__model_id',
        'base_vehicle__model__name',
        'submodel__submodel_id',
        'submodel__name',
        'vehicle_id'
    )

    changelist_actions = (
        'import_vehicles_class_action',
    )

    list_display = (
        'details_link',
        'vehicle_id',
        'base_vehicle',
        'submodel',
        'is_authorized'
    )

    list_display_links = (
        'details_link',
    )

    list_filter = (
        'is_authorized',
        'base_vehicle',
        'submodel'
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    'is_authorized',
                    'vehicle_id'
                )
            }
        ),
        (
            'Base Vehicle', {
                'fields': (
                    'base_vehicle_link',
                    'base_vehicle'
                )
            }
        ),
        (
            'Submodel', {
                'fields': (
                    'submodel_link',
                    'submodel'
                )
            }
        )
    )

    readonly_fields = (
        'details_link',
        'base_vehicle_link',
        'submodel_link'
    )

    def details_link(self, obj):
        return get_change_view_link(obj, 'Details')
    details_link.short_description = ''

    def base_vehicle_link(self, obj):
        if not obj.base_vehicle:
            return None
        return get_change_view_link(
            obj.base_vehicle,
            'See full base vehicle'
        )
    base_vehicle_link.short_description = ''

    def submodel_link(self, obj):
        if not obj.submodel:
            return None
        return get_change_view_link(obj.submodel, 'See full submodel')
    submodel_link.short_description = ''


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
        'dataset_count',
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
                    'is_authorized',
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

    actions = (
        'import_products_queryset_action',
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
                    'is_authorized',
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


@admin.register(SemaCategory)
class SemaCategoryModelAdmin(ObjectActions, ModelAdmin, SemaCategoryActions):
    search_fields = (
        'category_id',
        'name'
    )

    changelist_actions = (
        'import_categories_class_action',
    )

    list_display = (
        'details_link',
        'category_id',
        'name',
        'parent_category',
        'is_authorized',
        'child_category_count'
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
                    'is_authorized',
                    'category_id',
                    'name'
                )
            }
        ),
        (
            'Parent Category', {
                'fields': (
                    'parent_category_link',
                    'parent_category'
                )
            }
        )
    )

    readonly_fields = (
        'details_link',
        'parent_category_link',
        'child_category_count'
    )

    inlines = (
        SemaCategoryTabularInline,
    )

    def details_link(self, obj):
        return get_change_view_link(obj, 'Details')
    details_link.short_description = ''

    def parent_category_link(self, obj):
        if not obj.parent_category:
            return None
        return get_change_view_link(
            obj.parent_category, 'See full parent category')
    parent_category_link.short_description = ''


@admin.register(SemaProduct)
class SemaProductModelAdmin(ObjectActions, ModelAdmin, SemaProductActions):
    search_fields = (
        'dataset__brand__brand_id',
        'dataset__brand__name',
        'dataset__dataset_id',
        'dataset__name',
        'product_id',
        'part_number'
    )

    actions = (
        'update_html_queryset_action',
    )

    change_actions = (
        'update_html_object_action',
    )

    list_display = (
        'details_link',
        'product_id',
        'part_number',
        'dataset',
        'is_authorized'
    )

    list_display_links = (
        'details_link',
    )

    list_filter = (
        'is_authorized',
        HasProduct,
        HasMissingHtml
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    'product_link',
                    'is_authorized',
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
        ),
        (
            'HTML', {
                'fields': (
                    'html',
                ),
                'classes': (
                    'collapse',
                )
            }
        ),
        (
            None, {
                'fields': (
                    'html_preview',
                )
            }
        )
    )

    readonly_fields = (
        'details_link',
        'product_link',
        'dataset_link',
        'brand_link',
        'brand_a',
        'html_preview'
    )

    def details_link(self, obj):
        return get_change_view_link(obj, 'Details')
    details_link.short_description = ''

    def product_link(self, obj):
        if not hasattr(obj, 'product'):
            return '-----'
        return get_change_view_link(obj.product, 'See full product')
    product_link.short_description = ''

    def dataset_link(self, obj):
        return get_change_view_link(obj.dataset, 'See full dataset')
    dataset_link.short_description = ''

    def brand_link(self, obj):
        return get_change_view_link(obj.dataset.brand, 'See full brand')
    brand_link.short_description = ''

    def brand_a(self, obj):
        return str(obj.dataset.brand)
    brand_a.short_description = 'brand'

    def html_preview(self, obj):
        if not obj.html:
            return '-----'
        try:
            html = f"<html>\n{obj.html.split('</head>', 1)[1]}"
            image_class = 'class="main-product-img"'
            image_width = 'width="300px"'
            index = html.index(image_class)
            html = f"{html[:index]}{image_width} {html[index:]}"
            return mark_safe(html)
        except Exception as err:
            return str(err)


@admin.register(Product)
class ProductModelAdmin(ObjectActions, ModelAdmin, ProductActions):
    search_fields = (
        'premier_product__premier_part_number',
        'premier_product__vendor_part_number',
        'premier_product__description',
        'premier_product__manufacturer',
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
        'link_products_class_action',
    )

    list_display = (
        'details_link',
        'id',
        'premier_product',
        'sema_product'
    )

    list_display_links = (
        'details_link',
    )

    list_filter = (
        HasPremierProduct,
        HasSemaProduct
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
        )
    )

    readonly_fields = (
        'details_link',
        'id',
        'premier_product_link',
        'sema_product_link'
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


@admin.register(Manufacturer)
class ManufacturerModelAdmin(ObjectActions, ModelAdmin, ManufacturerActions):
    search_fields = (
        'premier_manufacturer',
        'sema_brand'
    )

    changelist_actions = (
        'check_unlinked_manufacturers_class_action',
    )

    list_display = (
        'details_link',
        'id',
        'premier_manufacturer',
        'sema_brand'
    )

    list_display_links = (
        'details_link',
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    'id',
                    'premier_manufacturer',
                    'sema_brand'
                )
            }
        ),
    )

    readonly_fields = (
        'details_link',
        'id'
    )

    def details_link(self, obj):
        return get_change_view_link(obj, 'Details')
    details_link.short_description = ''
