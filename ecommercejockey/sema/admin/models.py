from django_object_actions import BaseDjangoObjectActions as ObjectActions

from django.contrib import admin
from django.contrib.admin import ModelAdmin, RelatedOnlyFieldListFilter
from django.utils.safestring import mark_safe

from core.admin.utils import (
    get_change_view_link,
    get_image_preview
)
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
    SemaYearByDecade,
    ByCategoryLevel,
    HasCategory,
    HasHtml,
    HasItem,
    HasVehicle,
    SemaBaseVehicleByDecade,
    SemaBaseVehicleMayBeRelevant,
    # SemaCategoryMayBeRelevant,
    SemaDatasetMayBeRelevant,
    SemaMakeYearByDecade,
    SemaMakeYearMayBeRelevant,
    # SemaProductMayBeRelevant,
    SemaVehicleByDecade,
    SemaVehicleMayBeRelevant
)
from .inlines import (
    SemaBaseVehicleTabularInline,
    SemaCategoryChildrenTabularInline,
    SemaCategoryParentsTabularInline,
    SemaCategoryProductsTabularInline,
    SemaDatasetTabularInline,
    # SemaMakeYearTabularInline,
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
        # 'update_product_vehicles_queryset_action',  # TO NOTE: too long
        'mark_as_relevant_queryset_action',
        'mark_as_irrelevant_queryset_action'
    )

    changelist_actions = (
        'import_class_action',
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
        'primary_image_preview',
        'is_authorized',
        'is_relevant',
        'relevancy_errors',
        'notes'
    )

    list_display_links = (
        'details_link',
    )

    list_editable = (
        'is_relevant',
        'is_authorized'
    )

    list_filter = (
        'is_authorized',
        'is_relevant',
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    'is_authorized',
                    'is_relevant',
                    'relevancy_errors'
                )
            }
        ),
        (
            'Brand', {
                'fields': (
                    'brand_id',
                    'name'
                )
            }
        ),
        (
            'Images', {
                'fields': (
                    ('primary_image_url', 'primary_image_preview'),
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

    inlines = (
        SemaDatasetTabularInline,
    )

    readonly_fields = (
        'primary_image_preview',
        'relevancy_errors',
        'dataset_count'
    )

    def details_link(self, obj):
        return get_change_view_link(obj, 'Details')
    details_link.short_description = ''

    def primary_image_preview(self, obj):
        if not obj.primary_image_url:
            return ''
        return get_image_preview(obj.primary_image_url, width="100")
    primary_image_preview.short_description = 'primary image'


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
        # 'update_product_vehicles_queryset_action',  # TO NOTE: too long
        'mark_as_relevant_queryset_action',
        'mark_as_irrelevant_queryset_action'
    )

    changelist_actions = (
        'import_class_action',
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
        'is_authorized',
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
        'is_authorized'
    )

    list_filter = (
        'is_authorized',
        'is_relevant',
        SemaDatasetMayBeRelevant
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    'is_authorized',
                    'may_be_relevant_flag',
                    'is_relevant',
                    'relevancy_errors'
                )
            }
        ),
        (
            'Dataset', {
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

    def may_be_relevant_flag(self, obj):
        if obj.is_relevant != obj.may_be_relevant:
            return '~'
        else:
            return ''
    may_be_relevant_flag.short_description = ''


@admin.register(SemaYear)
class SemaYearModelAdmin(ObjectActions, ModelAdmin, SemaYearActions):
    search_fields = (
        'year',
    )

    actions = (
        'mark_as_relevant_queryset_action',
        'mark_as_irrelevant_queryset_action'
    )

    changelist_actions = (
        'import_class_action',
    )

    list_display = (
        'details_link',
        'year',
        'make_year_count',
        'is_authorized',
        'is_relevant',
        'relevancy_errors',
        'notes'
    )

    list_display_links = (
        'details_link',
    )

    list_editable = (
        'is_relevant',
        'is_authorized'
    )

    list_filter = (
        'is_authorized',
        'is_relevant',
        SemaYearByDecade
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    'is_authorized',
                    'is_relevant',
                    'relevancy_errors'
                )
            }
        ),
        (
            'Year', {
                'fields': (
                    'year',
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
        'make_year_count',
        'details_link'
    )

    # inlines = (
    #     SemaMakeYearTabularInline,  # TO NOTE: too long
    # )

    def details_link(self, obj):
        return get_change_view_link(obj, 'Details')
    details_link.short_description = ''


@admin.register(SemaMake)
class SemaMakeModelAdmin(ObjectActions, ModelAdmin, SemaMakeActions):
    search_fields = (
        'make_id',
        'name',
    )

    actions = (
        'mark_as_relevant_queryset_action',
        'mark_as_irrelevant_queryset_action'
    )

    changelist_actions = (
        'import_class_action',
    )

    list_display = (
        'details_link',
        'make_id',
        'name',
        'make_year_count',
        'is_authorized',
        'is_relevant',
        'relevancy_errors',
        'notes'
    )

    list_display_links = (
        'details_link',
    )

    list_editable = (
        'is_relevant',
        'is_authorized'
    )

    list_filter = (
        'is_authorized',
        'is_relevant',
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    'is_authorized',
                    'is_relevant',
                    'relevancy_errors'
                )
            }
        ),
        (
            'Make', {
                'fields': (
                    'make_id',
                    'name'
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
        'make_year_count',
        'details_link'
    )

    # inlines = (
    #     SemaMakeYearTabularInline,  # TO NOTE: too long
    # )

    def details_link(self, obj):
        return get_change_view_link(obj, 'Details')
    details_link.short_description = ''


@admin.register(SemaModel)
class SemaModelModelAdmin(ObjectActions, ModelAdmin, SemaModelActions):
    search_fields = (
        'model_id',
        'name'
    )

    actions = (
        'mark_as_relevant_queryset_action',
        'mark_as_irrelevant_queryset_action'
    )

    changelist_actions = (
        'import_class_action',
    )

    list_display = (
        'details_link',
        'model_id',
        'name',
        'base_vehicle_count',
        'is_authorized',
        'is_relevant',
        'relevancy_errors',
        'notes'
    )

    list_display_links = (
        'details_link',
    )

    list_editable = (
        'is_relevant',
        'is_authorized'
    )

    list_filter = (
        'is_authorized',
        'is_relevant'
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    'is_authorized',
                    'is_relevant',
                    'relevancy_errors'
                )
            }
        ),
        (
            'Model', {
                'fields': (
                    'model_id',
                    'name'
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
        'base_vehicle_count',
        'details_link',
    )

    # inlines = (
    #     SemaBaseVehicleTabularInline,  # TO NOTE: too long
    # )

    def details_link(self, obj):
        return get_change_view_link(obj, 'Details')
    details_link.short_description = ''


@admin.register(SemaSubmodel)
class SemaSubmodelModelAdmin(ObjectActions, ModelAdmin, SemaSubmodelActions):
    search_fields = (
        'submodel_id',
        'name'
    )

    actions = (
        'mark_as_relevant_queryset_action',
        'mark_as_irrelevant_queryset_action'
    )

    changelist_actions = (
        'import_class_action',
    )

    list_display = (
        'details_link',
        'submodel_id',
        'name',
        'vehicle_count',
        'is_authorized',
        'is_relevant',
        'relevancy_errors',
        'notes'
    )

    list_display_links = (
        'details_link',
    )

    list_editable = (
        'is_relevant',
        'is_authorized'
    )

    list_filter = (
        'is_authorized',
        'is_relevant'
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    'is_authorized',
                    'may_be_relevant_flag',
                    'is_relevant',
                    'relevancy_errors'
                )
            }
        ),
        (
            'Submodel', {
                'fields': (
                    'submodel_id',
                    'name'
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
        'vehicle_count',
        'details_link',
    )

    # inlines = (
    #     SemaVehicleTabularInline,  # TO NOTE: too long
    # )

    def details_link(self, obj):
        return get_change_view_link(obj, 'Details')
    details_link.short_description = ''


@admin.register(SemaMakeYear)
class SemaMakeYearModelAdmin(ObjectActions, ModelAdmin, SemaMakeYearActions):
    list_select_related = (
        'year',
        'make'
    )

    actions = (
        'mark_as_relevant_queryset_action',
        'mark_as_irrelevant_queryset_action'
    )

    search_fields = (
        'year__year',
        'make__make_id',
        'make__name'
    )

    changelist_actions = (
        'import_class_action',
    )

    list_display = (
        'details_link',
        'id',
        'year',
        'make',
        'base_vehicle_count',
        'is_authorized',
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
        'is_authorized'
    )

    list_filter = (
        'is_authorized',
        'is_relevant',
        SemaMakeYearMayBeRelevant,
        SemaMakeYearByDecade,
        ('make', RelatedOnlyFieldListFilter)
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    'is_authorized',
                    'may_be_relevant_flag',
                    'is_relevant',
                    'relevancy_errors'
                )
            }
        ),
        (
            'Make Year', {
                'fields': (
                    'id',
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
            'Notes', {
                'fields': (
                    'notes',
                )
            }
        )
    )

    readonly_fields = (
        'id',
        'relevancy_errors',
        'may_be_relevant_flag',
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

    def may_be_relevant_flag(self, obj):
        if obj.is_relevant != obj.may_be_relevant:
            return '~'
        else:
            return ''
    may_be_relevant_flag.short_description = ''


@admin.register(SemaBaseVehicle)
class SemaBaseVehicleModelAdmin(ObjectActions, ModelAdmin,
                                SemaBaseVehicleActions):
    list_select_related = (
        'make_year',
        'model'
    )

    actions = (
        'mark_as_relevant_queryset_action',
        'mark_as_irrelevant_queryset_action'
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
        'import_class_action',
    )

    list_display = (
        'details_link',
        'base_vehicle_id',
        'make_year',
        'model',
        'vehicle_count',
        'is_authorized',
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
        'is_authorized'
    )

    list_filter = (
        'is_authorized',
        'is_relevant',
        SemaBaseVehicleMayBeRelevant,
        SemaBaseVehicleByDecade,
        ('make_year__make', RelatedOnlyFieldListFilter),
        ('model', RelatedOnlyFieldListFilter)
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    'is_authorized',
                    'may_be_relevant_flag',
                    'is_relevant',
                    'relevancy_errors'
                )
            }
        ),
        (
            'Base Vehicle', {
                'fields': (
                    'base_vehicle_id',
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

    def may_be_relevant_flag(self, obj):
        if obj.is_relevant != obj.may_be_relevant:
            return '~'
        else:
            return ''
    may_be_relevant_flag.short_description = ''


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

    actions = (
        'mark_as_relevant_queryset_action',
        'mark_as_irrelevant_queryset_action'
    )

    changelist_actions = (
        'import_class_action',
    )

    list_display = (
        'details_link',
        'vehicle_id',
        'base_vehicle',
        'submodel',
        'product_count',
        'is_authorized',
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
        'is_authorized'
    )

    list_filter = (
        'is_authorized',
        'is_relevant',
        SemaVehicleMayBeRelevant,
        SemaVehicleByDecade,
        ('base_vehicle__make_year__make', RelatedOnlyFieldListFilter),
        ('base_vehicle__model', RelatedOnlyFieldListFilter),
        ('submodel', RelatedOnlyFieldListFilter)
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    'is_authorized',
                    'may_be_relevant_flag',
                    'is_relevant',
                    'relevancy_errors'
                )
            }
        ),
        (
            'Vehicle', {
                'fields': (
                    'vehicle_id',
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

    def may_be_relevant_flag(self, obj):
        if obj.is_relevant != obj.may_be_relevant:
            return '~'
        else:
            return ''
    may_be_relevant_flag.short_description = ''


@admin.register(SemaCategory)
class SemaCategoryModelAdmin(ObjectActions, ModelAdmin, SemaCategoryActions):
    search_fields = (
        'category_id',
        'name'
    )

    actions = (
        'update_category_products_queryset_action',
        'mark_as_relevant_queryset_action',
        'mark_as_irrelevant_queryset_action'
    )

    changelist_actions = (
        'import_class_action',
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
        'is_authorized',
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
        'is_authorized'
    )

    list_filter = (
        'is_authorized',
        'is_relevant',
        # SemaCategoryMayBeRelevant,
        ByCategoryLevel
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    'is_authorized',
                    'may_be_relevant_flag',
                    'is_relevant',
                    'relevancy_errors'
                )
            }
        ),
        (
            'Category', {
                'fields': (
                    'category_id',
                    'name'
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

    def may_be_relevant_flag(self, obj):
        if obj.is_relevant != obj.may_be_relevant:
            return '~'
        else:
            return ''
    may_be_relevant_flag.short_description = ''


@admin.register(SemaProduct)
class SemaProductModelAdmin(ObjectActions, ModelAdmin, SemaProductActions):
    list_select_related = (
        'dataset',
    )

    ordering = (
        'product_id',
    )

    search_fields = (
        'dataset__brand__brand_id',
        'dataset__brand__name',
        'dataset__dataset_id',
        'dataset__name',
        'product_id',
        'part_number',
        'pies_c10_des',
        'pies_c10_ext'
    )

    actions = (
        'update_html_queryset_action',
        'update_product_vehicles_queryset_action',
        'mark_as_relevant_queryset_action',
        'mark_as_irrelevant_queryset_action'
    )

    changelist_actions = (
        'import_class_action',
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
        'pies_c10_des',
        'pies_c10_ext',
        'dataset',
        'primary_image_preview',
        'is_authorized',
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
        'is_authorized'
    )

    list_filter = (
        HasItem,
        'is_authorized',
        'is_relevant',
        # SemaProductMayBeRelevant,
        ('dataset__brand', RelatedOnlyFieldListFilter),
        HasCategory,
        HasVehicle,
        HasHtml
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    'is_authorized',
                    'may_be_relevant_flag',
                    'is_relevant',
                    'relevancy_errors'
                )
            }
        ),
        (
            'Product', {
                'fields': (
                    'product_id',
                    'part_number',
                    'pies_c10_des',
                    'pies_c10_ext'
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
            'Images', {
                'fields': (
                    ('primary_image_url', 'primary_image_preview'),
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
        ),
        (
            'Notes', {
                'fields': (
                    'notes',
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
        'primary_image_preview',
        'relevancy_errors',
        'may_be_relevant_flag',
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

    def primary_image_preview(self, obj):
        if not obj.primary_image_url:
            return ''
        return get_image_preview(obj.primary_image_url, width="100")
    primary_image_preview.short_description = 'primary image'

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

    def may_be_relevant_flag(self, obj):
        if obj.is_relevant != obj.may_be_relevant:
            return '~'
        else:
            return ''
    may_be_relevant_flag.short_description = ''

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related(
            'vehicles', 'categories')
