from django_object_actions import BaseDjangoObjectActions as ObjectActions

from django.contrib import admin
from django.contrib.admin import ModelAdmin, RelatedOnlyFieldListFilter
from django.utils.safestring import mark_safe

from core.admin.utils import (
    get_change_view_link,
    get_changelist_view_link,
    get_image_preview
)
from ..models import (
    SemaBaseVehicle,
    SemaBrand,
    SemaCategory,
    SemaDataset,
    SemaDescriptionPiesAttribute,
    SemaDigitalAssetsPiesAttribute,
    SemaEngine,
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
    SemaEngineActions,
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
    HasCategoryPath,
    HasHtml,
    HasItem,
    HasPremierManufacturer,
    HasPremierProduct,
    HasPrimaryImage,
    HasShopifyCollection,
    HasShopifyProduct,
    HasShopifyVendor,
    HasVehicle,
    HasVendor,
    SemaBaseVehicleByDecade,
    SemaBaseVehicleMayBeRelevant,
    SemaCategoryMayBeRelevant,
    SemaBrandMayBeRelevant,
    SemaEngineByDecade,
    SemaEngineMayBeRelevant,
    SemaMakeYearByDecade,
    SemaMakeYearMayBeRelevant,
    SemaModelMayBeRelevant,
    SemaProductMayBeRelevant,
    SemaSubmodelMayBeRelevant,
    SemaYearMayBeRelevant,
    SemaVehicleByDecade,
    SemaVehicleMayBeRelevant
)
from .inlines import (
    SemaBaseVehicleVehiclesTabularInline,
    SemaBrandDatasetsTabularInline,
    SemaCategoryDatasetsTabularInline,
    SemaCategoryChildCategoriesTabularInline,
    SemaCategoryParentCategoriesTabularInline,
    SemaCategoryProductsTabularInline,
    SemaDatasetCategoriesTabularInline,
    # SemaDatasetProductsTabularInline,
    SemaDatasetVehiclesTabularInline,
    SemaMakeMakeYearsTabularInline,
    SemaMakeYearBaseVehiclesTabularInline,
    SemaModelBaseVehiclesTabularInline,
    SemaProductCategoriesTabularInline,
    SemaProductDescriptionPiesAttributeTabularInline,
    SemaProductDigitalAssetsPiesAttributeTabularInline,
    SemaProductVehiclesTabularInline,
    SemaSubmodelVehiclesTabularInline,
    SemaVehicleDatasetsTabularInline,
    # SemaVehicleEnginesTabularInline,
    # SemaVehicleProductsTabularInline,
    SemaYearMakeYearsTabularInline
)


@admin.register(SemaBrand)
class SemaBrandModelAdmin(ObjectActions, ModelAdmin, SemaBrandActions):
    actions = (
        'mark_as_relevant_queryset_action',
        'mark_as_irrelevant_queryset_action'
    )

    changelist_actions = (
        'import_new_class_action',
        # 'import_class_action',
        # 'unauthorize_class_action',
        # 'sync_class_action'
    )

    search_fields = (
        'brand_id',
        'name'
    )

    list_display = (
        'detail_link',
        'brand_id',
        'name',
        'dataset_count',
        'primary_image_preview',
        'is_authorized',
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
        'is_authorized',
        'is_relevant',
        SemaBrandMayBeRelevant,
        HasVendor,
        HasPremierManufacturer,
        HasShopifyVendor,
        HasPrimaryImage
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    'vendor_link',
                    'premier_manufacturer_link',
                    'shopify_vendor_link',
                    'is_authorized',
                    'may_be_relevant_flag',
                    'is_relevant',
                    'relevancy_warnings',
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
        )
    )

    inlines = (
        SemaBrandDatasetsTabularInline,
    )

    readonly_fields = (
        'relevancy_warnings',
        'relevancy_errors',
        'may_be_relevant_flag',
        'primary_image_preview',
        'vendor_link',
        'premier_manufacturer_link',
        'shopify_vendor_link',
        'dataset_count'
    )

    def detail_link(self, obj):
        if not obj or not obj.pk:
            return None

        return get_change_view_link(obj, 'Details')
    detail_link.short_description = ''

    def vendor_link(self, obj):
        if not obj or not obj.pk or not hasattr(obj, 'vendor'):
            return None

        return get_change_view_link(obj.vendor, 'See Vendor')
    vendor_link.short_description = ''

    def premier_manufacturer_link(self, obj):
        if (not obj or not obj.pk or not hasattr(obj, 'vendor')
                or not obj.vendor.premier_manufacturer):
            return None

        return get_change_view_link(
            obj.vendor.premier_manufacturer,
            'See Premier Manufacturer',
        )
    premier_manufacturer_link.short_description = ''

    def shopify_vendor_link(self, obj):
        if (not obj or not obj.pk or not hasattr(obj, 'vendor')
                or not obj.vendor.shopify_vendor):
            return None

        return get_change_view_link(
            obj.vendor.shopify_vendor,
            'See Shopify Vendor',
        )
    shopify_vendor_link.short_description = ''

    def dataset_count(self, obj):
        if not obj or not obj.pk:
            return None

        return f'{obj._dataset_relevant_count}/{obj._dataset_count}'
    dataset_count.admin_order_field = '_dataset_relevant_count'
    dataset_count.short_description = 'dataset count'

    def primary_image_preview(self, obj):
        if not obj or not obj.pk or not obj.primary_image_url:
            return None

        return get_image_preview(obj.primary_image_url, width="100")
    primary_image_preview.short_description = ''

    def may_be_relevant_flag(self, obj):
        if not obj or not obj.pk:
            return None

        if obj.is_relevant != obj.may_be_relevant:
            return '~'
        else:
            return ''
    may_be_relevant_flag.short_description = ''

    def get_queryset(self, request):
        return super().get_queryset(request).with_admin_data()

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)

        if obj and not request.user.is_superuser:
            readonly_fields += (
                'brand_id',
            )

        return readonly_fields

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return (
                (
                    None, {
                        'fields': (
                            'brand_id',
                            'name'
                        )
                    }
                ),
            )

        return super().get_fieldsets(request, obj)

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []

        return super().get_inline_instances(request, obj)


@admin.register(SemaDataset)
class SemaDatasetModelAdmin(ObjectActions, ModelAdmin, SemaDatasetActions):
    list_select_related = (
        'brand',
    )

    actions = (
        'mark_as_relevant_queryset_action',
        'mark_as_irrelevant_queryset_action',
        'update_dataset_categories_queryset_action',  # TO NOTE: too long
        'update_dataset_vehicles_queryset_action'  # TO NOTE: too long
    )

    changelist_actions = (
        'import_new_class_action',
        # 'import_class_action',
        # 'unauthorize_class_action',
        # 'sync_class_action'
    )

    change_actions = (
        'update_dataset_categories_object_action',
        'update_dataset_vehicles_object_action'  # TO NOTE: too long
    )

    search_fields = (
        'dataset_id',
        'name',
        'brand__brand_id',
        'brand__name'
    )

    list_display = (
        'detail_link',
        'dataset_id',
        'name',
        'brand',
        'category_count',
        'vehicle_count',
        'product_count',
        'is_authorized',
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
        'is_authorized',
        'is_relevant',
        'brand'
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    'is_authorized',
                    'is_relevant',
                    'relevancy_warnings',
                    'relevancy_errors'
                )
            }
        ),
        (
            'Brand', {
                'fields': (
                    'brand_link',
                    'brand'
                ),
                'classes': (
                    'collapse',
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
        )
    )

    autocomplete_fields = (
        'brand',
    )

    readonly_fields = (
        'relevancy_warnings',
        'relevancy_errors',
        'detail_link',
        'brand_link',
        'category_count',
        'vehicle_count',
        'product_count'
    )

    inlines = (
        SemaDatasetCategoriesTabularInline,
        SemaDatasetVehiclesTabularInline,
        # SemaDatasetProductsTabularInline  # TO NOTE: too long
    )

    def detail_link(self, obj):
        if not obj or not obj.pk:
            return None

        return get_change_view_link(obj, 'Details')
    detail_link.short_description = ''

    def brand_link(self, obj):
        if not obj or not obj.pk or not obj.brand:
            return None

        return get_change_view_link(
            obj.brand, 'See Full Brand')
    brand_link.short_description = ''

    def category_count(self, obj):
        if not obj or not obj.pk:
            return None

        return f'{obj.category_relevant_count}/{obj.category_count}'
    # category_count.admin_order_field = '_category_relevant_count'
    category_count.short_description = 'category count'

    def vehicle_count(self, obj):
        if not obj or not obj.pk:
            return None

        return f'{obj.vehicle_relevant_count}/{obj.vehicle_count}'
    # vehicle_count.admin_order_field = '_vehicle_relevant_count'
    vehicle_count.short_description = 'vehicle count'

    def product_count(self, obj):
        if not obj or not obj.pk:
            return None

        return f'{obj.product_relevant_count}/{obj.product_count}'
    # product_count.admin_order_field = '_product_relevant_count'
    product_count.short_description = 'product count'

    # def get_queryset(self, request):  # FIXME
    #     return super().get_queryset(request).with_admin_data()

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return (
                (
                    None, {
                        'fields': (
                            'dataset_id',
                            'brand',
                            'name'
                        )
                    }
                ),
            )

        return super().get_fieldsets(request, obj)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)

        if obj and not request.user.is_superuser:
            readonly_fields += (
                'dataset_id',
            )

        return readonly_fields

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []

        return super().get_inline_instances(request, obj)


@admin.register(SemaYear)
class SemaYearModelAdmin(ObjectActions, ModelAdmin, SemaYearActions):
    actions = (
        'mark_as_relevant_queryset_action',
        'mark_as_irrelevant_queryset_action'
    )

    changelist_actions = (
        'import_new_class_action',
        # 'import_class_action',
        # 'unauthorize_class_action',
        # 'sync_class_action'
    )

    search_fields = (
        'year',
    )

    list_display = (
        'detail_link',
        'year',
        'make_year_count',
        'is_authorized',
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
        'is_authorized',
        'is_relevant',
        SemaYearMayBeRelevant,
        SemaYearByDecade
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    'is_authorized',
                    'may_be_relevant_flag',
                    'is_relevant',
                    'relevancy_warnings',
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
        )
    )

    readonly_fields = (
        'relevancy_warnings',
        'relevancy_errors',
        'may_be_relevant_flag',
        'detail_link',
        'make_year_count'
    )

    inlines = (
        SemaYearMakeYearsTabularInline,
    )

    def detail_link(self, obj):
        if not obj or not obj.pk:
            return None

        return get_change_view_link(obj, 'Details')
    detail_link.short_description = ''

    def make_year_count(self, obj):
        if not obj or not obj.pk:
            return None

        return f'{obj._make_year_relevant_count}/{obj._make_year_count}'
    make_year_count.admin_order_field = '_make_year_relevant_count'
    make_year_count.short_description = 'make year count'

    def may_be_relevant_flag(self, obj):
        if not obj or not obj.pk:
            return None

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
                            'year',
                        )
                    }
                ),
            )

        return super().get_fieldsets(request, obj)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)

        if obj and not request.user.is_superuser:
            readonly_fields += (
                'year',
            )

        return readonly_fields

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []

        return super().get_inline_instances(request, obj)


@admin.register(SemaMake)
class SemaMakeModelAdmin(ObjectActions, ModelAdmin, SemaMakeActions):
    actions = (
        'mark_as_relevant_queryset_action',
        'mark_as_irrelevant_queryset_action'
    )

    changelist_actions = (
        'import_new_class_action',
        # 'import_class_action',
        # 'unauthorize_class_action',
        # 'sync_class_action'
    )

    search_fields = (
        'make_id',
        'name',
    )

    list_display = (
        'detail_link',
        'make_id',
        'name',
        'make_year_count',
        'is_authorized',
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
        'is_authorized',
        'is_relevant'
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    'is_authorized',
                    'is_relevant',
                    'relevancy_warnings',
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
        )
    )

    readonly_fields = (
        'relevancy_warnings',
        'relevancy_errors',
        'detail_link',
        'make_year_count'
    )

    inlines = (
        SemaMakeMakeYearsTabularInline,
    )

    def detail_link(self, obj):
        if not obj or not obj.pk:
            return None

        return get_change_view_link(obj, 'Details')
    detail_link.short_description = ''

    def make_year_count(self, obj):
        if not obj or not obj.pk:
            return None

        return f'{obj._make_year_relevant_count}/{obj._make_year_count}'
    make_year_count.admin_order_field = '_make_year_relevant_count'
    make_year_count.short_description = 'make year count'

    def get_queryset(self, request):
        return super().get_queryset(request).with_admin_data()

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return (
                (
                    None, {
                        'fields': (
                            'make_id',
                            'name'
                        )
                    }
                ),
            )

        return super().get_fieldsets(request, obj)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)

        if obj and not request.user.is_superuser:
            readonly_fields += (
                'make_id',
            )

        return readonly_fields

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []

        return super().get_inline_instances(request, obj)


@admin.register(SemaModel)
class SemaModelModelAdmin(ObjectActions, ModelAdmin, SemaModelActions):
    actions = (
        'mark_as_relevant_queryset_action',
        'mark_as_irrelevant_queryset_action'
    )

    changelist_actions = (
        'import_new_class_action',
        # 'import_class_action',
        # 'unauthorize_class_action',
        # 'sync_class_action',
    )

    search_fields = (
        'model_id',
        'name'
    )

    list_display = (
        'detail_link',
        'model_id',
        'name',
        'base_vehicle_count',
        'is_authorized',
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
        'is_authorized',
        'is_relevant',
        SemaModelMayBeRelevant
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    'is_authorized',
                    'may_be_relevant_flag',
                    'is_relevant',
                    'relevancy_warnings',
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
        )
    )

    readonly_fields = (
        'relevancy_warnings',
        'relevancy_errors',
        'may_be_relevant_flag',
        'detail_link',
        'base_vehicle_count'
    )

    inlines = (
        SemaModelBaseVehiclesTabularInline,
    )

    def detail_link(self, obj):
        if not obj or not obj.pk:
            return None

        return get_change_view_link(obj, 'Details')
    detail_link.short_description = ''

    def base_vehicle_count(self, obj):
        if not obj or not obj.pk:
            return None

        return f'{obj._base_vehicle_relevant_count}/{obj._base_vehicle_count}'
    base_vehicle_count.admin_order_field = '_base_vehicle_relevant_count'
    base_vehicle_count.short_description = 'base vehicle count'

    def may_be_relevant_flag(self, obj):
        if not obj or not obj.pk:
            return None

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
                            'model_id',
                            'name'
                        )
                    }
                ),
            )

        return super().get_fieldsets(request, obj)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)

        if obj and not request.user.is_superuser:
            readonly_fields += (
                'model_id',
            )

        return readonly_fields

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []

        return super().get_inline_instances(request, obj)


@admin.register(SemaSubmodel)
class SemaSubmodelModelAdmin(ObjectActions, ModelAdmin, SemaSubmodelActions):
    actions = (
        'mark_as_relevant_queryset_action',
        'mark_as_irrelevant_queryset_action'
    )

    changelist_actions = (
        'import_new_class_action',
        # 'import_class_action',
        # 'unauthorize_class_action',
        # 'sync_class_action'
    )

    search_fields = (
        'submodel_id',
        'name'
    )

    list_display = (
        'detail_link',
        'submodel_id',
        'name',
        'vehicle_count',
        'is_authorized',
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
        'is_authorized',
        'is_relevant',
        SemaSubmodelMayBeRelevant
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    'is_authorized',
                    'may_be_relevant_flag',
                    'is_relevant',
                    'relevancy_warnings',
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
        )
    )

    readonly_fields = (
        'relevancy_warnings',
        'relevancy_errors',
        'may_be_relevant_flag',
        'detail_link',
        'vehicle_count'
    )

    inlines = (
        SemaSubmodelVehiclesTabularInline,
    )

    def detail_link(self, obj):
        if not obj or not obj.pk:
            return None

        return get_change_view_link(obj, 'Details')
    detail_link.short_description = ''

    def vehicle_count(self, obj):
        if not obj or not obj.pk:
            return None

        return f'{obj._vehicle_relevant_count}/{obj._vehicle_count}'
    vehicle_count.admin_order_field = '_vehicle_relevant_count'
    vehicle_count.short_description = 'vehicle count'

    def may_be_relevant_flag(self, obj):
        if not obj or not obj.pk:
            return None

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
                            'submodel_id',
                            'name'
                        )
                    }
                ),
            )

        return super().get_fieldsets(request, obj)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)

        if obj and not request.user.is_superuser:
            readonly_fields += (
                'submodel_id',
            )

        return readonly_fields

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []

        return super().get_inline_instances(request, obj)


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

    changelist_actions = (
        'import_new_class_action',
        # 'import_class_action',
        # 'unauthorize_class_action',
        # 'sync_class_action'
    )

    search_fields = (
        'id',
        'year__year',
        'make__make_id',
        'make__name'
    )

    list_display = (
        'detail_link',
        'id',
        'year',
        'make',
        'base_vehicle_count',
        'is_authorized',
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
                    'relevancy_warnings',
                    'relevancy_errors',
                    'id'
                )
            }
        ),
        (
            'Year', {
                'fields': (
                    'year_link',
                    'year'
                ),
                'classes': (
                    'collapse',
                )
            }
        ),
        (
            'Make', {
                'fields': (
                    'make_link',
                    'make'
                ),
                'classes': (
                    'collapse',
                )
            }
        )
    )

    readonly_fields = (
        'id',
        'relevancy_warnings',
        'relevancy_errors',
        'may_be_relevant_flag',
        'detail_link',
        'year_link',
        'make_link',
        'base_vehicle_count'
    )

    autocomplete_fields = (
        'year',
        'make'
    )

    inlines = (
        SemaMakeYearBaseVehiclesTabularInline,
    )

    def detail_link(self, obj):
        if not obj or not obj.pk:
            return None

        return get_change_view_link(obj, 'Details')
    detail_link.short_description = ''

    def year_link(self, obj):
        if not obj or not obj.pk or not obj.year:
            return None

        return get_change_view_link(obj.year, 'See Full Year')
    year_link.short_description = ''

    def make_link(self, obj):
        if not obj or not obj.pk or not obj.make:
            return None

        return get_change_view_link(obj.make, 'See Full Make')
    make_link.short_description = ''

    def base_vehicle_count(self, obj):
        if not obj or not obj.pk:
            return None

        return f'{obj._base_vehicle_relevant_count}/{obj._base_vehicle_count}'
    base_vehicle_count.admin_order_field = '_base_vehicle_relevant_count'
    base_vehicle_count.short_description = 'base vehicle count'

    def may_be_relevant_flag(self, obj):
        if not obj or not obj.pk:
            return None

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
                            'year',
                            'make'
                        )
                    }
                ),
            )

        return super().get_fieldsets(request, obj)

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []

        return super().get_inline_instances(request, obj)


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

    changelist_actions = (
        'import_new_class_action',  # TO NOTE: too long
        # 'import_class_action',  # TO NOTE: too long
        # 'unauthorize_class_action',  # TO NOTE: too long
        # 'sync_class_action'  # TO NOTE: too long
    )

    search_fields = (
        'base_vehicle_id',
        'make_year__year__year',
        'make_year__make__make_id',
        'make_year__make__name',
        'model__model_id',
        'model__name'
    )

    list_display = (
        'detail_link',
        'base_vehicle_id',
        'make_year',
        'model',
        'vehicle_count',
        'is_authorized',
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
                    'relevancy_warnings',
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
                ),
                'classes': (
                    'collapse',
                )
            }
        ),
        (
            'Model', {
                'fields': (
                    'model_link',
                    'model'
                ),
                'classes': (
                    'collapse',
                )
            }
        )
    )

    readonly_fields = (
        'relevancy_warnings',
        'relevancy_errors',
        'may_be_relevant_flag',
        'detail_link',
        'make_year_link',
        'model_link',
        'vehicle_count'
    )

    autocomplete_fields = (
        'make_year',
        'model'
    )

    inlines = (
        SemaBaseVehicleVehiclesTabularInline,
    )

    def detail_link(self, obj):
        if not obj or not obj.pk:
            return None

        return get_change_view_link(obj, 'Details')
    detail_link.short_description = ''

    def make_year_link(self, obj):
        if not obj or not obj.pk or not obj.make_year:
            return None

        return get_change_view_link(obj.make_year, 'See Full Make Year')
    make_year_link.short_description = ''

    def model_link(self, obj):
        if not obj or not obj.pk or not obj.model:
            return None

        return get_change_view_link(obj.model, 'See Full Model')
    model_link.short_description = ''

    def vehicle_count(self, obj):
        if not obj or not obj.pk:
            return None

        return f'{obj._vehicle_relevant_count}/{obj._vehicle_count}'
    vehicle_count.admin_order_field = '_vehicle_relevant_count'
    vehicle_count.short_description = 'vehicle count'

    def may_be_relevant_flag(self, obj):
        if not obj or not obj.pk:
            return None

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
                            'base_vehicle_id',
                            'make_year',
                            'model'
                        )
                    }
                ),
            )

        return super().get_fieldsets(request, obj)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)

        if obj and not request.user.is_superuser:
            readonly_fields += (
                'base_vehicle_id',
            )

        return readonly_fields

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []

        return super().get_inline_instances(request, obj)


@admin.register(SemaVehicle)
class SemaVehicleModelAdmin(ObjectActions, ModelAdmin, SemaVehicleActions):
    list_select_related = (
        'base_vehicle',
        'submodel'
    )

    actions = (
        'mark_as_relevant_queryset_action',
        'mark_as_irrelevant_queryset_action'
    )

    changelist_actions = (
        'import_new_class_action',  # TO NOTE: too long
        # 'import_class_action',  # TO NOTE: too long
        # 'unauthorize_class_action',  # TO NOTE: too long
        # 'sync_class_action'  # TO NOTE: too long
    )

    search_fields = (
        'vehicle_id',
        'base_vehicle__base_vehicle_id',
        'base_vehicle__make_year__year__year',
        'base_vehicle__make_year__make__make_id',
        'base_vehicle__make_year__make__name',
        'base_vehicle__model__model_id',
        'base_vehicle__model__name',
        'submodel__submodel_id',
        'submodel__name'
    )

    list_display = (
        'detail_link',
        'vehicle_id',
        'base_vehicle',
        'submodel',
        'engine_count',
        'dataset_count',
        'product_count',
        'is_authorized',
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
                    'relevancy_warnings',
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
                ),
                'classes': (
                    'collapse',
                )
            }
        ),
        (
            'Submodel', {
                'fields': (
                    'submodel_link',
                    'submodel'
                ),
                'classes': (
                    'collapse',
                )
            }
        )
    )

    readonly_fields = (
        'relevancy_warnings',
        'relevancy_errors',
        'may_be_relevant_flag',
        'detail_link',
        'base_vehicle_link',
        'submodel_link',
        'engine_count',
        'dataset_count',
        'product_count'
    )

    autocomplete_fields = (
        'base_vehicle',
        'submodel'
    )

    inlines = (
        # SemaVehicleEnginesTabularInline, # TO NOTE: too long
        SemaVehicleDatasetsTabularInline,
        # SemaVehicleProductsTabularInline  # TO NOTE: too long
    )

    def detail_link(self, obj):
        if not obj or not obj.pk:
            return None

        return get_change_view_link(obj, 'Details')
    detail_link.short_description = ''

    def base_vehicle_link(self, obj):
        if not obj or not obj.pk or not obj.base_vehicle:
            return None

        return get_change_view_link(
            obj.base_vehicle,
            'See Full Base Vehicle'
        )
    base_vehicle_link.short_description = ''

    def submodel_link(self, obj):
        if not obj or not obj.pk or not obj.submodel:
            return None

        return get_change_view_link(obj.submodel, 'See Full Submodel')
    submodel_link.short_description = ''

    def engine_count(self, obj):
        if not obj or not obj.pk:
            return None

        return f'{obj._engine_relevant_count}/{obj._engine_count}'
    engine_count.admin_order_field = '_engine_relevant_count'
    engine_count.short_description = 'engine count'

    def dataset_count(self, obj):
        if not obj or not obj.pk:
            return None

        return f'{obj._dataset_relevant_count}/{obj._dataset_count}'
    dataset_count.admin_order_field = '_dataset_relevant_count'
    dataset_count.short_description = 'dataset count'

    def product_count(self, obj):
        if not obj or not obj.pk:
            return None

        return f'{obj._product_relevant_count}/{obj._product_count}'
    product_count.admin_order_field = '_product_relevant_count'
    product_count.short_description = 'product count'

    def may_be_relevant_flag(self, obj):
        if not obj or not obj.pk:
            return None

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
                            'vehicle_id',
                            'base_vehicle',
                            'submodel'
                        )
                    }
                ),
            )

        return super().get_fieldsets(request, obj)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)

        if obj and not request.user.is_superuser:
            readonly_fields += (
                'vehicle_id',
            )

        return readonly_fields

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []

        return super().get_inline_instances(request, obj)


@admin.register(SemaEngine)
class SemaEngineModelAdmin(ObjectActions, ModelAdmin, SemaEngineActions):
    list_select_related = (
        'vehicle',
    )

    actions = (
        'mark_as_relevant_queryset_action',
        'mark_as_irrelevant_queryset_action'
    )

    changelist_actions = (
        'import_new_class_action',  # TO NOTE: too long
        # 'import_class_action',  # TO NOTE: too long
        # 'unauthorize_class_action',  # TO NOTE: too long
        # 'sync_class_action'  # TO NOTE: too long
    )

    search_fields = (
        'id',
        'vehicle__vehicle_id',
        'vehicle__base_vehicle__base_vehicle_id',
        'vehicle__base_vehicle__make_year__year__year',
        'vehicle__base_vehicle__make_year__make__make_id',
        'vehicle__base_vehicle__make_year__make__name',
        'vehicle__base_vehicle__model__model_id',
        'vehicle__base_vehicle__model__name',
        'vehicle__submodel__submodel_id',
        'vehicle__submodel__name'
    )

    list_display = (
        'detail_link',
        'id',
        'vehicle',
        'litre',
        'block_type',
        'cylinders',
        'cylinder_head_type',
        'fuel_type',
        'is_authorized',
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
        'is_authorized',
        'is_relevant',
        SemaEngineMayBeRelevant,
        'fuel_type',
        'manufacturer',
        'litre',
        'block_type',
        'cylinders',
        'valves_per_engine',
        'cylinder_head_type',
        'ignition_system_type',
        SemaEngineByDecade,
        ('vehicle__base_vehicle__make_year__make', RelatedOnlyFieldListFilter),
        ('vehicle__base_vehicle__model', RelatedOnlyFieldListFilter),
        ('vehicle__submodel', RelatedOnlyFieldListFilter)
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    'is_authorized',
                    'may_be_relevant_flag',
                    'is_relevant',
                    'relevancy_warnings',
                    'relevancy_errors',
                    'id'
                )
            }
        ),
        (
            'Vehicle', {
                'fields': (
                    'vehicle_link',
                    'vehicle'
                ),
                'classes': (
                    'collapse',
                )
            }
        ),
        (
            'Engine', {
                'fields': (
                    'litre',
                    'cc',
                    'cid',
                    'cylinders',
                    'block_type',
                    'engine_bore_in',
                    'engine_bore_metric',
                    'engine_stroke_in',
                    'engine_stroke_metric',
                    'valves_per_engine',
                    'aspiration',
                    'cylinder_head_type',
                    'fuel_type',
                    'ignition_system_type',
                    'manufacturer',
                    'horse_power',
                    'kilowatt_power',
                    'engine_designation'
                )
            }
        )
    )

    readonly_fields = (
        'id',
        'relevancy_warnings',
        'relevancy_errors',
        'may_be_relevant_flag',
        'detail_link',
        'vehicle_link'
    )

    autocomplete_fields = (
        'vehicle',
    )

    def detail_link(self, obj):
        if not obj or not obj.pk:
            return None

        return get_change_view_link(obj, 'Details')
    detail_link.short_description = ''

    def vehicle_link(self, obj):
        if not obj or not obj.pk or not obj.vehicle:
            return None

        return get_change_view_link(
            obj.vehicle,
            'See Full Vehicle'
        )
    vehicle_link.short_description = ''

    def may_be_relevant_flag(self, obj):
        if not obj or not obj.pk:
            return None

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
                            'vehicle',
                            'litre',
                            'cc',
                            'cid',
                            'cylinders',
                            'block_type',
                            'engine_bore_in',
                            'engine_bore_metric',
                            'engine_stroke_in',
                            'engine_stroke_metric',
                            'valves_per_engine',
                            'aspiration',
                            'cylinder_head_type',
                            'fuel_type',
                            'ignition_system_type',
                            'manufacturer',
                            'horse_power',
                            'kilowatt_power',
                            'engine_designation'
                        )
                    }
                ),
            )

        return super().get_fieldsets(request, obj)

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []

        return super().get_inline_instances(request, obj)


@admin.register(SemaCategory)
class SemaCategoryModelAdmin(ObjectActions, ModelAdmin, SemaCategoryActions):
    actions = (
        'mark_as_relevant_queryset_action',
        'mark_as_irrelevant_queryset_action',
        'update_category_products_queryset_action'
    )

    changelist_actions = (
        # 'import_new_class_action',  # TO NOTE: does not add m2m
        'import_class_action',
        # 'unauthorize_class_action',
        # 'sync_class_action'
    )

    change_actions = (
        'update_category_products_object_action',
    )

    search_fields = (
        'category_id',
        'name'
    )

    list_display = (
        'detail_link',
        'category_id',
        'name',
        'level',
        'parent_category_count',
        'child_category_count',
        'dataset_count',
        'product_count',
        'is_authorized',
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
        'is_authorized',
        'is_relevant',
        SemaCategoryMayBeRelevant,
        ByCategoryLevel,
        HasCategoryPath,
        HasShopifyCollection
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    'category_paths_link',
                    'shopify_collections_link',
                    'is_authorized',
                    'may_be_relevant_flag',
                    'is_relevant',
                    'relevancy_warnings',
                    'relevancy_errors'
                )
            }
        ),
        (
            'Category', {
                'fields': (
                    'category_id',
                    'name',
                    'level'
                )
            }
        )
    )

    readonly_fields = (
        'relevancy_warnings',
        'relevancy_errors',
        'may_be_relevant_flag',
        'level',
        'detail_link',
        'category_paths_link',
        'shopify_collections_link',
        'parent_category_count',
        'child_category_count',
        'dataset_count',
        'product_count'
    )

    inlines = (
        SemaCategoryParentCategoriesTabularInline,
        SemaCategoryChildCategoriesTabularInline,
        SemaCategoryDatasetsTabularInline,
        SemaCategoryProductsTabularInline
    )

    def detail_link(self, obj):
        if not obj or not obj.pk:
            return None

        return get_change_view_link(obj, 'Details')
    detail_link.short_description = ''

    def category_paths_link(self, obj):
        if not obj or not obj.pk:
            return None

        if obj.level == '1':
            category_path_model = obj.root_category_paths.first()._meta.model
            query = f'sema_root_category={obj.pk}'
        elif obj.level == '2':
            category_path_model = obj.branch_category_paths.first()._meta.model
            query = f'sema_branch_category={obj.pk}'
        else:
            category_path_model = obj.leaf_category_paths.first()._meta.model
            query = f'sema_leaf_category={obj.pk}'

        return get_changelist_view_link(
            category_path_model,
            'See Category Paths',
            query=query
        )
    category_paths_link.short_description = ''

    def shopify_collections_link(self, obj):
        if not obj or not obj.pk:
            return None

        if obj.level == '1':
            o = obj.root_category_paths.first().shopify_root_collection
        elif obj.level == '2':
            o = obj.branch_category_paths.first().shopify_branch_collection
        else:
            o = obj.leaf_category_paths.first().shopify_leaf_collection

        return get_change_view_link(
            o,
            'See Shopify Collection'
        )
    shopify_collections_link.short_description = ''

    def parent_category_count(self, obj):
        if not obj or not obj.pk:
            return None

        return (
            f'{obj._parent_category_relevant_count}'
            f'/{obj._parent_category_count}'
        )
    parent_category_count.admin_order_field = '_parent_category_relevant_count'
    parent_category_count.short_description = 'parent count'

    def child_category_count(self, obj):
        if not obj or not obj.pk:
            return None

        return (
            f'{obj._child_category_relevant_count}'
            f'/{obj._child_category_count}'
        )
    child_category_count.admin_order_field = '_child_category_relevant_count'
    child_category_count.short_description = 'child count'

    def dataset_count(self, obj):
        if not obj or not obj.pk:
            return None

        return f'{obj._dataset_relevant_count}/{obj._dataset_count}'
    dataset_count.admin_order_field = '_dataset_relevant_count'
    dataset_count.short_description = 'dataset count'

    def product_count(self, obj):
        if not obj or not obj.pk:
            return None

        return f'{obj._product_relevant_count}/{obj._product_count}'
    product_count.admin_order_field = '_product_relevant_count'
    product_count.short_description = 'product count'

    def may_be_relevant_flag(self, obj):
        if not obj or not obj.pk:
            return None

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
                            'category_id',
                            'name',
                            'parent_categories'
                        )
                    }
                ),
            )

        return super().get_fieldsets(request, obj)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)

        if obj and not request.user.is_superuser:
            readonly_fields += (
                'category_id',
            )

        return readonly_fields

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []

        return super().get_inline_instances(request, obj)


@admin.register(SemaProduct)
class SemaProductModelAdmin(ObjectActions, ModelAdmin, SemaProductActions):
    list_select_related = (
        'dataset',
    )

    actions = (
        'mark_as_relevant_queryset_action',
        'mark_as_irrelevant_queryset_action',
        'update_html_queryset_action',
        'update_product_vehicles_queryset_action',
        'update_description_pies_queryset_action',
        'update_digital_assets_pies_queryset_action'
    )

    changelist_actions = (
        'import_new_class_action',
        # 'import_class_action',
        # 'unauthorize_class_action',
        # 'sync_class_action'
    )

    change_actions = (
        'update_html_object_action',
        'update_product_vehicles_object_action',
        'update_description_pies_object_action',
        'update_digital_assets_pies_object_action'
    )

    search_fields = (
        'product_id',
        'part_number',
        'dataset__dataset_id',
        'dataset__name',
        'dataset__brand__brand_id',
        'dataset__brand__name'
    )

    list_display = (
        'detail_link',
        'product_id',
        'part_number',
        'dataset',
        'description_pies_attribute_count',
        'digital_assets_pies_attribute_count',
        'category_count',
        'vehicle_count',
        'is_authorized',
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
        'is_authorized',
        'is_relevant',
        SemaProductMayBeRelevant,
        ('dataset__brand', RelatedOnlyFieldListFilter),
        HasItem,
        HasPremierProduct,
        HasShopifyProduct,
        HasCategory,
        HasVehicle,
        HasHtml
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    'item_link',
                    'premier_product_link',
                    'shopify_product_link',
                    'is_authorized',
                    'may_be_relevant_flag',
                    'is_relevant',
                    'relevancy_warnings',
                    'relevancy_errors'
                )
            }
        ),
        (
            'Dataset', {
                'fields': (
                    'dataset_link',
                    'dataset'
                ),
                'classes': (
                    'collapse',
                )
            }
        ),
        (
            'Product', {
                'fields': (
                    'product_id',
                    'part_number'
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
    )

    readonly_fields = (
        'relevancy_warnings',
        'relevancy_errors',
        'may_be_relevant_flag',
        'html_preview',
        'detail_link',
        'dataset_link',
        'item_link',
        'premier_product_link',
        'shopify_product_link',
        'description_pies_attribute_count',
        'digital_assets_pies_attribute_count',
        'category_count',
        'vehicle_count'
    )

    inlines = (
        SemaProductDescriptionPiesAttributeTabularInline,
        SemaProductDigitalAssetsPiesAttributeTabularInline,
        SemaProductCategoriesTabularInline,
        SemaProductVehiclesTabularInline
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

    def premier_product_link(self, obj):
        if (not obj or not obj.pk
                or not hasattr(obj, 'item') or not obj.item.premier_product):
            return None

        return get_change_view_link(
            obj.item.premier_product,
            'See Premier Product',
        )
    premier_product_link.short_description = ''

    def shopify_product_link(self, obj):
        if (not obj or not obj.pk
                or not hasattr(obj, 'item') or not obj.item.shopify_product):
            return None

        return get_change_view_link(
            obj.item.shopify_product,
            'See Shopify Product',
        )
    shopify_product_link.short_description = ''

    def dataset_link(self, obj):
        if not obj or not obj.pk or not obj.dataset:
            return None

        return get_change_view_link(obj.dataset, 'See Full Dataset')
    dataset_link.short_description = ''

    def description_pies_attribute_count(self, obj):
        if not obj or not obj.pk:
            return None

        return obj.description_pies_attribute_count
    # description_pies_attribute_count.admin_order_field = (
    #     '_description_pies_attribute_count'
    # )
    description_pies_attribute_count.short_description = 'description count'

    def digital_assets_pies_attribute_count(self, obj):
        if not obj or not obj.pk:
            return None

        return obj.digital_assets_pies_attribute_count
    # digital_assets_pies_attribute_count.admin_order_field = (
    #     '_digital_assets_pies_attribute_count'
    # )
    digital_assets_pies_attribute_count.short_description = (
        'digital assets count'
    )

    def category_count(self, obj):
        if not obj or not obj.pk:
            return None

        return f'{obj.category_relevant_count}/{obj.category_count}'
    # category_count.admin_order_field = '_category_relevant_count'
    category_count.short_description = 'category count'

    def vehicle_count(self, obj):
        if not obj or not obj.pk:
            return None

        if not obj.vehicle_count:
            return (
                f'{obj.dataset.vehicle_relevant_count}'
                f'/{obj.dataset.vehicle_count} (D)'
            )
        return f'{obj.vehicle_relevant_count}/{obj.vehicle_count}'
    # vehicle_count.admin_order_field = '_vehicle_relevant_count'
    vehicle_count.short_description = 'vehicle count'

    def html_preview(self, obj):
        if not obj or not obj.pk:
            return None

        return mark_safe(obj.clean_html)
    html_preview.short_description = ''

    def may_be_relevant_flag(self, obj):
        if not obj or not obj.pk:
            return None

        if obj.is_relevant != obj.may_be_relevant:
            return '~'
        else:
            return ''
    may_be_relevant_flag.short_description = ''

    # def get_queryset(self, request):  # FIXME
    #     return super().get_queryset(request).with_admin_data()

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return (
                (
                    None, {
                        'fields': (
                            'product_id',
                            'part_number',
                            'dataset',
                            'html',
                            'categories',
                            'vehicles'
                        )
                    }
                ),
            )

        return super().get_fieldsets(request, obj)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)

        if obj and not request.user.is_superuser:
            readonly_fields += (
                'product_id',
            )

        return readonly_fields

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []

        return super().get_inline_instances(request, obj)


class SemaPiesAttributeBaseModelAdmin(ModelAdmin):
    list_select_related = (
        'product',
    )

    search_fields = (
        'id',
        'segment',
        'value',
        'product__product_id',
        'product__part_number',
        'product__dataset__dataset_id',
        'product__dataset__name',
        'product__dataset__brand__brand_id',
        'product__dataset__brand__name'
    )

    list_display = (
        'detail_link',
        'id',
        'product',
        'segment',
        'value'
    )

    list_display_links = (
        'detail_link',
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
            'Product', {
                'fields': (
                    'product_link',
                    'product'
                ),
                'classes': (
                    'collapse',
                )
            }
        ),
        (
            'PIES Attribute', {
                'fields': (
                    'segment',
                    'value'
                )
            }
        )
    )

    autocomplete_fields = (
        'product',
    )

    readonly_fields = (
        'id',
        'detail_link',
        'product_link'
    )

    def detail_link(self, obj):
        if not obj or not obj.pk:
            return None

        return get_change_view_link(obj, 'Details')
    detail_link.short_description = ''

    def product_link(self, obj):
        if not obj or not obj.pk or not obj.product:
            return None

        return get_change_view_link(obj.product, 'See Full Product')
    product_link.short_description = ''

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return (
                (
                    None, {
                        'fields': (
                            'segment',
                            'value'
                        )
                    }
                ),
            )

        return super().get_fieldsets(request, obj)


@admin.register(SemaDescriptionPiesAttribute)
class SemaDescriptionPiesAttributeModelAdmin(SemaPiesAttributeBaseModelAdmin):
    pass


@admin.register(SemaDigitalAssetsPiesAttribute)
class SemaSemaDigitalAssetsPiesAttributeModelAdmin(SemaPiesAttributeBaseModelAdmin):
    list_display = (
        'detail_link',
        'id',
        'product',
        'segment',
        'value',
        'image_preview'
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
            'Product', {
                'fields': (
                    'product_link',
                    'product'
                ),
                'classes': (
                    'collapse',
                )
            }
        ),
        (
            'PIES Attribute', {
                'fields': (
                    'segment',
                    ('value', 'image_preview')
                )
            }
        )
    )

    readonly_fields = (
        'id',
        'image_preview',
        'detail_link',
        'product_link'
    )

    def image_preview(self, obj):
        if not obj or not obj.pk or not obj.value:
            return None

        try:
            return get_image_preview(obj.value)
        except Exception as err:
            return str(err)
    image_preview.short_description = ''
