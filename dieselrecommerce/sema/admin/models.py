from django_object_actions import BaseDjangoObjectActions as ObjectActions

from django.contrib import admin
from django.contrib.admin import ModelAdmin, RelatedOnlyFieldListFilter
from django.utils.safestring import mark_safe

from core.admin.utils import get_change_view_link
from ..models import (
    SemaBaseVehicle,
    SemaBrand,
    SemaCategory,
    SemaDataset,
    SemaMake,
    SemaMakeYear,
    SemaModel,
    SemaProduct,
    SemaSubmodel,
    SemaVehicle,
    SemaYear
)
from .actions import (
    SemaBaseVehicleActions,
    SemaBrandActions,
    SemaCategoryActions,
    SemaDatasetActions,
    SemaMakeActions,
    SemaMakeYearActions,
    SemaModelActions,
    SemaProductActions,
    SemaSubmodelActions,
    SemaVehicleActions,
    SemaYearActions
)
from .filters import (
    ByDecade,
    ByCategoryLevel,
    HasCategory,
    HasHtml,
    HasProduct,
    HasVehicle
)
from .inlines import (
    SemaBaseVehicleTabularInline,
    SemaCategoryChildrenTabularInline,
    SemaCategoryParentsTabularInline,
    SemaCategoryProductsTabularInline,
    SemaDatasetTabularInline,
    SemaMakeYearTabularInline,
    SemaProductTabularInline,
    SemaVehicleProductsTabularInline,
    SemaVehicleTabularInline
)


@admin.register(SemaBrand)
class SemaBrandModelAdmin(ObjectActions, ModelAdmin, SemaBrandActions):
    search_fields = (
        'brand_id',
        'name'
    )

    actions = (
        'import_datasets_queryset_action',
        # 'update_product_vehicles_queryset_action'  # TO NOTE: too long
    )

    changelist_actions = (
        'import_and_unauthorize_class_action',
        # 'update_product_vehicles_class_action'  # TO NOTE: too long
    )

    change_actions = (
        'import_datasets_object_action',
        # 'update_product_vehicles_object_action'  # TO NOTE: too long
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
    list_select_related = (
        'brand',
    )

    search_fields = (
        'brand__brand_id',
        'brand__name',
        'dataset_id',
        'name'
    )

    actions = (
        'import_products_queryset_action',
        # 'update_product_vehicles_queryset_action'  # TO NOTE: too long
    )

    changelist_actions = (
        'import_and_unauthorize_class_action',
        # 'update_product_vehicles_class_action'  # TO NOTE: too long
    )

    # change_actions = (
    #     'update_product_vehicles_object_action',  # TO NOTE: too long
    # )

    list_display = (
        'details_link',
        'dataset_id',
        'name',
        'brand',
        'product_count',
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
        'product_count',
        'details_link',
        'brand_link'
    )

    autocomplete_fields = (
        'brand',
    )

    inlines = (
        SemaProductTabularInline,
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


@admin.register(SemaYear)
class SemaYearModelAdmin(ObjectActions, ModelAdmin, SemaYearActions):
    search_fields = (
        'year',
    )

    changelist_actions = (
        'import_and_unauthorize_class_action',
    )

    list_display = (
        'details_link',
        'year',
        'make_year_count',
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
        'make_year_count',
        'details_link'
    )

    inlines = (
        SemaMakeYearTabularInline,
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
        'import_and_unauthorize_class_action',
    )

    list_display = (
        'details_link',
        'make_id',
        'name',
        'make_year_count',
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
        'make_year_count',
        'details_link'
    )

    inlines = (
        SemaMakeYearTabularInline,
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
        'import_and_unauthorize_class_action',
    )

    list_display = (
        'details_link',
        'model_id',
        'name',
        'base_vehicle_count',
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
        'base_vehicle_count',
        'details_link',
    )

    inlines = (
        SemaBaseVehicleTabularInline,
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
        'import_and_unauthorize_class_action',
    )

    list_display = (
        'details_link',
        'submodel_id',
        'name',
        'vehicle_count',
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
        'vehicle_count',
        'details_link',
    )

    inlines = (
        SemaVehicleTabularInline,
    )

    def details_link(self, obj):
        return get_change_view_link(obj, 'Details')
    details_link.short_description = ''


@admin.register(SemaMakeYear)
class SemaMakeYearModelAdmin(ObjectActions, ModelAdmin, SemaMakeYearActions):
    list_select_related = (
        'year',
        'make'
    )

    search_fields = (
        'year__year',
        'make__make_id',
        'make__name'
    )

    changelist_actions = (
        'import_and_unauthorize_class_action',
    )

    list_display = (
        'details_link',
        'id',
        'year',
        'make',
        'base_vehicle_count',
        'is_authorized'
    )

    list_display_links = (
        'details_link',
    )

    list_filter = (
        'is_authorized',
        ('make', RelatedOnlyFieldListFilter),
        ('year', RelatedOnlyFieldListFilter)
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    'is_authorized',
                    'id'
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
        )
    )

    readonly_fields = (
        'id',
        'base_vehicle_count',
        'details_link',
        'year_link',
        'make_link'
    )

    autocomplete_fields = (
        'year',
        'make'
    )

    inlines = (
        SemaBaseVehicleTabularInline,
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


@admin.register(SemaBaseVehicle)
class SemaBaseVehicleModelAdmin(ObjectActions, ModelAdmin,
                                SemaBaseVehicleActions):
    list_select_related = (
        'make_year',
        'model'
    )

    search_fields = (
        'base_vehicle_id',
        'make_year__year__year',
        'make_year__make__make_id',
        'make_year__make__name',
        'model__model_id',
        'model__name'
    )

    changelist_actions = (
        'import_and_unauthorize_class_action',
    )

    list_display = (
        'details_link',
        'base_vehicle_id',
        'make_year',
        'model',
        'vehicle_count',
        'is_authorized'
    )

    list_display_links = (
        'details_link',
    )

    list_filter = (
        'is_authorized',
        ('make_year__make', RelatedOnlyFieldListFilter),
        ('model', RelatedOnlyFieldListFilter),
        ('make_year__year', RelatedOnlyFieldListFilter)
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
            'Make Year', {
                'fields': (
                    'make_year_link',
                    'make_year'
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
        'vehicle_count',
        'details_link',
        'make_year_link',
        'model_link'
    )

    autocomplete_fields = (
        'make_year',
        'model'
    )

    inlines = (
        SemaVehicleTabularInline,
    )

    def details_link(self, obj):
        return get_change_view_link(obj, 'Details')
    details_link.short_description = ''

    def make_year_link(self, obj):
        if not obj.make_year:
            return None
        return get_change_view_link(obj.make_year, 'See full make year')
    make_year_link.short_description = ''

    def model_link(self, obj):
        if not obj.model:
            return None
        return get_change_view_link(obj.model, 'See full model')
    model_link.short_description = ''


@admin.register(SemaVehicle)
class SemaVehicleModelAdmin(ObjectActions, ModelAdmin, SemaVehicleActions):
    list_select_related = (
        'base_vehicle',
        'submodel'
    )

    search_fields = (
        'base_vehicle__base_vehicle_id',
        'base_vehicle__make_year__year__year',
        'base_vehicle__make_year__make__make_id',
        'base_vehicle__make_year__make__name',
        'base_vehicle__model__model_id',
        'base_vehicle__model__name',
        'submodel__submodel_id',
        'submodel__name',
        'vehicle_id'
    )

    changelist_actions = (
        'import_and_unauthorize_class_action',
    )

    list_display = (
        'details_link',
        'vehicle_id',
        'base_vehicle',
        'submodel',
        'product_count',
        'is_authorized',
        'is_relevant'
    )

    list_display_links = (
        'details_link',
    )

    list_editable = (
        'is_relevant',
    )

    list_filter = (
        'is_authorized',
        ('base_vehicle__make_year__year', RelatedOnlyFieldListFilter),
        ('base_vehicle__make_year__make', RelatedOnlyFieldListFilter),
        ('base_vehicle__model', RelatedOnlyFieldListFilter),
        ('submodel', RelatedOnlyFieldListFilter)
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    'is_relevant',
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
        'product_count',
        'base_vehicle_link',
        'submodel_link'
    )

    autocomplete_fields = (
        'base_vehicle',
        'submodel'
    )

    inlines = (
        SemaVehicleProductsTabularInline,
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

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if not request.user.is_superuser:
            readonly_fields += (
                'is_authorized',
                'vehicle_id',
                'base_vehicle',
                'submodel'
            )
        return readonly_fields


@admin.register(SemaCategory)
class SemaCategoryModelAdmin(ObjectActions, ModelAdmin, SemaCategoryActions):
    search_fields = (
        'category_id',
        'name'
    )

    actions = (
        'update_category_products_queryset_action',
    )

    changelist_actions = (
        'import_and_unauthorize_class_action',
        'update_category_products_class_action'
    )

    change_actions = (
        'update_category_products_object_action',
    )

    list_display = (
        'details_link',
        'category_id',
        'name',
        'parent_category_count',
        'child_category_count',
        'product_count',
        'is_authorized'
    )

    list_display_links = (
        'details_link',
    )

    list_filter = (
        'is_authorized',
        ByCategoryLevel
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
    )

    readonly_fields = (
        'parent_category_count',
        'child_category_count',
        'product_count',
        'details_link'
    )

    inlines = (
        SemaCategoryParentsTabularInline,
        SemaCategoryChildrenTabularInline,
        SemaCategoryProductsTabularInline
    )

    def details_link(self, obj):
        return get_change_view_link(obj, 'Details')
    details_link.short_description = ''


@admin.register(SemaProduct)
class SemaProductModelAdmin(ObjectActions, ModelAdmin, SemaProductActions):
    list_select_related = (
        'dataset',
    )

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
        'update_product_vehicles_queryset_action'
    )

    changelist_actions = (
        'import_and_unauthorize_class_action',
        # 'update_product_categories_class_action',  # TO NOTE: too long
        # 'update_product_vehicles_class_action'  # TO NOTE: too long
    )

    change_actions = (
        'update_html_object_action',
        'update_product_vehicles_object_action'
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
        HasProduct,
        'is_authorized',
        ('dataset', RelatedOnlyFieldListFilter),
        HasCategory,
        HasVehicle,
        HasHtml
    )

    fieldsets = (
        (
            None, {
                'fields': (
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
            'Categories', {
                'fields': (
                    'categories',
                )
            }
        ),
        (
            'Vehicles', {
                'fields': (
                    'vehicles',
                ),
                'classes': (
                    'collapse',
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

    autocomplete_fields = (
        'dataset',
        'categories',
        'vehicles'
    )

    readonly_fields = (
        'details_link',
        'dataset_link',
        'brand_link',
        'brand_a',
        'html_preview'
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

    def html_preview(self, obj):
        if not obj.html:
            return '-----'
        try:
            html = f"<html>\n{obj.html.split('</head>', 1)[1]}"
            image_classes = [
                'main-product-img',
                'brand-logo'
            ]
            image_width = '300px'
            for image_class in image_classes:
                index = html.index(f'class="{image_class}"')
                html = f'{html[:index]}width="{image_width}" {html[index:]}'
            return mark_safe(html)
        except Exception as err:
            return str(err)
