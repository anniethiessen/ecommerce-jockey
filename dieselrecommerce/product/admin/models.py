from django_object_actions import BaseDjangoObjectActions as ObjectActions
from import_export.admin import ImportMixin

from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.utils.safestring import mark_safe

from ..models import (
    Manufacturer,
    PremierProduct,
    Product,
    SemaBrand,
    SemaDataset,
    SemaMake,
    SemaModel,
    SemaProduct,
    SemaSubmodel,
    SemaYear
)
from .actions import (
    ManufacturerActions,
    PremierProductActions,
    ProductActions,
    SemaBrandActions,
    SemaDatasetActions,
    SemaProductActions
)
from .filters import (
    HasAlbertaInventory,
    HasMissingInventory,
    HasMissingPricing,
    HasPremierProduct,
    HasProduct,
    HasSemaProduct
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
        'model_id',
        'base_vehicle_id',
        'name'
    )

    list_display = (
        'details_link',
        'model_id',
        'base_vehicle_id',
        'name',
        'make'
    )

    list_display_links = (
        'details_link',
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    'model_id',
                    'base_vehicle_id',
                    'name'
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
    )

    readonly_fields = (
        'details_link',
        'make_link'
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


@admin.register(SemaSubmodel)
class SemaSubmodelModelAdmin(ModelAdmin):
    search_fields = (
        'model__make__make_id',
        'model__make__name',
        'model__model_id',
        'model__base_vehicle_id',
        'model__name',
        'submodel_id',
        'vehicle_id',
        'name'
    )

    list_display = (
        'details_link',
        'submodel_id',
        'vehicle_id',
        'name',
        'model'
    )

    list_display_links = (
        'details_link',
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    'submodel_id',
                    'vehicle_id',
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
    )

    readonly_fields = (
        'details_link',
        'model_link'
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
class SemaProductModelAdmin(ObjectActions, ModelAdmin, SemaProductActions):
    search_fields = (
        'dataset__brand__brand_id',
        'dataset__brand__name',
        'dataset__dataset_id',
        'dataset__name',
        'product_id',
        'part_number'
    )

    change_actions = (
        'update_html_object_action',
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

    list_filter = (
        HasProduct,
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    'product_link',
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
