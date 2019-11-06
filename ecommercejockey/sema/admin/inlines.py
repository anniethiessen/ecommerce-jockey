from django.contrib.admin import TabularInline

from core.admin.forms import LimitedInlineFormSet
from core.admin.utils import (
    get_change_view_link,
    get_changelist_view_link,
    get_image_preview
)
from .forms import (
    LimitedManyToManyCategoryInlineFormSet,
    LimitedManyToManyChildCategoryInlineFormSet,
    LimitedManyToManyDatasetInlineFormSet,
    LimitedManyToManyParentCategoryInlineFormSet,
    LimitedManyToManyProductInlineFormSet,
    LimitedManyToManyVehicleInlineFormSet
)
from ..models import (
    SemaBaseVehicle,
    SemaCategory,
    SemaDataset,
    SemaDescriptionPiesAttribute,
    SemaDigitalAssetsPiesAttribute,
    SemaMakeYear,
    SemaProduct,
    SemaVehicle
)


class SemaDatasetBaseTabularInline(TabularInline):
    model = SemaDataset
    fk_name = None
    formset = LimitedInlineFormSet
    verbose_name_plural = 'datasets (top 10)'
    all_link_query = None
    extra = 0
    ordering = (
        'name',
    )
    classes = (
        'collapse',
    )

    fields = (
        'all_link',
        'details_link',
        'dataset_id',
        'name',
        'brand',
        'is_authorized',
        'is_relevant'
    )

    readonly_fields = (
        'details_link',
        'all_link'
    )

    def get_rel_obj(self, obj):
        return getattr(obj, self.fk_name)

    def all_link(self, obj):
        query = f'{self.all_link_query}={getattr(self.get_rel_obj(obj), "pk")}'
        return get_changelist_view_link(obj, 'See All', query)
    all_link.short_description = ''

    def details_link(self, obj):
        if not obj.pk:
            return None
        return get_change_view_link(obj, 'Details')
    details_link.short_description = ''

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'brand':
            formfield.choices = formfield.choices
        return formfield


class SemaDatasetManyToManyBaseTabularInline(TabularInline):
    model = None
    fk_name = None
    obj_name = 'semadataset'
    formset = LimitedManyToManyDatasetInlineFormSet
    verbose_name_plural = 'datasets (top 10)'
    all_link_query = None
    extra = 0
    classes = (
        'collapse',
    )

    fields = (
        'all_link',
        'details_link',
        'dataset_id_a',
        'name_a',
        'brand_a',
        'is_authorized_a',
        'is_relevant_a'
    )

    readonly_fields = (
        'all_link',
        'details_link',
        'dataset_id_a',
        'name_a',
        'brand_a',
        'is_authorized_a',
        'is_relevant_a'
    )

    def get_obj(self, obj):
        return getattr(obj, self.obj_name)

    def get_rel_obj(self, obj):
        return getattr(obj, self.fk_name)

    def all_link(self, obj):
        query = (
            f'{self.all_link_query}'
            f'={getattr(self.get_rel_obj(obj), "pk")}'
        )
        return get_changelist_view_link(
            self.get_obj(obj),
            'See All',
            query
        )
    all_link.short_description = ''

    def details_link(self, obj):
        if not obj.pk:
            return None
        return get_change_view_link(
            self.get_obj(obj),
            'Details'
        )
    details_link.short_description = ''

    def dataset_id_a(self, obj):
        if not obj.pk:
            return None
        return getattr(self.get_obj(obj), 'dataset_id')
    dataset_id_a.short_description = 'dataset ID'

    def name_a(self, obj):
        if not obj.pk:
            return None
        return getattr(self.get_obj(obj), 'name')
    name_a.short_description = 'name'

    def brand_a(self, obj):
        if not obj.pk:
            return None
        return getattr(self.get_obj(obj), 'brand')
    brand_a.short_description = 'brand'

    def is_authorized_a(self, obj):
        if not obj.pk:
            return None
        return getattr(self.get_obj(obj), 'is_authorized')
    is_authorized_a.boolean = True
    is_authorized_a.short_description = 'is authorized'

    def is_relevant_a(self, obj):
        if not obj.pk:
            return None
        return getattr(self.get_obj(obj), 'is_relevant')
    is_relevant_a.boolean = True
    is_relevant_a.short_description = 'is relevant'

    def get_ordering(self, request):
        return (
            f'{self.obj_name}__name',
        )


class SemaMakeYearBaseTabularInline(TabularInline):
    model = SemaMakeYear
    fk_name = None
    formset = LimitedInlineFormSet
    verbose_name_plural = 'make years (top 10)'
    all_link_query = None
    extra = 0
    ordering = (
        'year',
        'make'
    )
    classes = (
        'collapse',
    )

    fields = (
        'all_link',
        'details_link',
        'id',
        'year',
        'make',
        'is_authorized',
        'is_relevant'
    )

    readonly_fields = (
        'id',
        'all_link',
        'details_link'
    )

    def get_rel_obj(self, obj):
        return getattr(obj, self.fk_name)

    def all_link(self, obj):
        query = f'{self.all_link_query}={getattr(self.get_rel_obj(obj), "pk")}'
        return get_changelist_view_link(obj, 'See All', query)
    all_link.short_description = ''

    def details_link(self, obj):
        if not obj.pk:
            return None
        return get_change_view_link(obj, 'Details')
    details_link.short_description = ''

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, **kwargs)
        if db_field.name in ['year', 'make']:
            formfield.choices = formfield.choices
        return formfield


class SemaBaseVehicleBaseTabularInline(TabularInline):
    model = SemaBaseVehicle
    fk_name = None
    formset = LimitedInlineFormSet
    verbose_name_plural = 'base vehicles (top 10)'
    all_link_query = None
    extra = 0
    ordering = (
        'make_year',
        'model'
    )
    classes = (
        'collapse',
    )

    fields = (
        'all_link',
        'details_link',
        'base_vehicle_id',
        'make_year',
        'model',
        'is_authorized',
        'is_relevant'
    )

    readonly_fields = (
        'all_link',
        'details_link'
    )

    def get_rel_obj(self, obj):
        return getattr(obj, self.fk_name)

    def all_link(self, obj):
        query = f'{self.all_link_query}={getattr(self.get_rel_obj(obj), "pk")}'
        return get_changelist_view_link(obj, 'See All', query)
    all_link.short_description = ''

    def details_link(self, obj):
        if not obj.pk:
            return None
        return get_change_view_link(obj, 'Details')
    details_link.short_description = ''

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, **kwargs)
        if db_field.name in ['make_year', 'model']:
            formfield.choices = formfield.choices
        return formfield


class SemaVehicleBaseTabularInline(TabularInline):
    model = SemaVehicle
    fk_name = None
    formset = LimitedInlineFormSet
    verbose_name_plural = 'vehicles (top 10)'
    all_link_query = None
    extra = 0
    ordering = (
        'base_vehicle',
        'submodel'
    )
    classes = (
        'collapse',
    )

    fields = (
        'all_link',
        'details_link',
        'vehicle_id',
        'base_vehicle',
        'submodel',
        'is_authorized',
        'is_relevant'
    )

    readonly_fields = (
        'all_link',
        'details_link'
    )

    def get_rel_obj(self, obj):
        return getattr(obj, self.fk_name)

    def all_link(self, obj):
        query = f'{self.all_link_query}={getattr(self.get_rel_obj(obj), "pk")}'
        return get_changelist_view_link(obj, 'See All', query)
    all_link.short_description = ''

    def details_link(self, obj):
        if not obj.pk:
            return None
        return get_change_view_link(obj, 'Details')
    details_link.short_description = ''

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, **kwargs)
        if db_field.name in ['base_vehicle', 'submodel']:
            formfield.choices = formfield.choices
        return formfield


class SemaVehicleManyToManyBaseTabularInline(TabularInline):
    model = None
    fk_name = None
    obj_name = 'semavehicle'
    formset = LimitedManyToManyVehicleInlineFormSet
    verbose_name_plural = 'vehicles (top 10)'
    all_link_query = None
    extra = 0
    classes = (
        'collapse',
    )

    fields = (
        'all_link',
        'details_link',
        'vehicle_id_a',
        'base_vehicle_a',
        'submodel_a',
        'is_authorized_a',
        'is_relevant_a'
    )

    readonly_fields = (
        'all_link',
        'details_link',
        'vehicle_id_a',
        'base_vehicle_a',
        'submodel_a',
        'is_authorized_a',
        'is_relevant_a'
    )

    def get_obj(self, obj):
        return getattr(obj, self.obj_name)

    def get_rel_obj(self, obj):
        return getattr(obj, self.fk_name)

    def all_link(self, obj):
        query = (
            f'{self.all_link_query}'
            f'={getattr(self.get_rel_obj(obj), "pk")}'
        )
        return get_changelist_view_link(
            self.get_obj(obj),
            'See All',
            query
        )
    all_link.short_description = ''

    def details_link(self, obj):
        if not obj.pk:
            return None
        return get_change_view_link(
            self.get_obj(obj),
            'Details'
        )
    details_link.short_description = ''

    def vehicle_id_a(self, obj):
        if not obj.pk:
            return None
        return getattr(self.get_obj(obj), 'vehicle_id')
    vehicle_id_a.short_description = 'vehicle ID'

    def base_vehicle_a(self, obj):
        if not obj.pk:
            return None
        return getattr(self.get_obj(obj), 'base_vehicle')
    base_vehicle_a.short_description = 'base vehicle'

    def submodel_a(self, obj):
        if not obj.pk:
            return None
        return getattr(self.get_obj(obj), 'submodel')
    submodel_a.short_description = 'submodel'

    def is_authorized_a(self, obj):
        if not obj.pk:
            return None
        return getattr(self.get_obj(obj), 'is_authorized')
    is_authorized_a.boolean = True
    is_authorized_a.short_description = 'is authorized'

    def is_relevant_a(self, obj):
        if not obj.pk:
            return None
        return getattr(self.get_obj(obj), 'is_relevant')
    is_relevant_a.boolean = True
    is_relevant_a.short_description = 'is relevant'

    def get_ordering(self, request):
        return (
            f'{self.obj_name}__base_vehicle',
            f'{self.obj_name}__submodel'
        )


class SemaCategoryManyToManyBaseTabularInline(TabularInline):
    model = None
    fk_name = None
    obj_name = 'semacategory'
    formset = LimitedManyToManyCategoryInlineFormSet
    verbose_name_plural = 'categories (top 10)'
    all_link_query = None
    extra = 0
    classes = (
        'collapse',
    )

    fields = (
        'all_link',
        'details_link',
        'category_id_a',
        'name_a',
        'level_a',
        'is_authorized_a',
        'is_relevant_a'
    )

    readonly_fields = (
        'all_link',
        'details_link',
        'category_id_a',
        'name_a',
        'level_a',
        'is_authorized_a',
        'is_relevant_a'
    )

    def get_obj(self, obj):
        return getattr(obj, self.obj_name)

    def get_rel_obj(self, obj):
        return getattr(obj, self.fk_name)

    def all_link(self, obj):
        query = (
            f'{self.all_link_query}'
            f'={getattr(self.get_rel_obj(obj), "pk")}'
        )
        return get_changelist_view_link(
            self.get_obj(obj),
            'See All',
            query
        )
    all_link.short_description = ''

    def details_link(self, obj):
        if not obj.pk:
            return None
        return get_change_view_link(
            self.get_obj(obj),
            'Details'
        )
    details_link.short_description = ''

    def category_id_a(self, obj):
        if not obj.pk:
            return None
        return getattr(self.get_obj(obj), 'category_id')
    category_id_a.short_description = 'category ID'

    def name_a(self, obj):
        if not obj.pk:
            return None
        return getattr(self.get_obj(obj), 'name')
    name_a.short_description = 'name'

    def level_a(self, obj):
        if not obj.pk:
            return None
        return getattr(self.get_obj(obj), 'level')
    level_a.short_description = 'level'

    def is_authorized_a(self, obj):
        if not obj.pk:
            return None
        return getattr(self.get_obj(obj), 'is_authorized')
    is_authorized_a.boolean = True
    is_authorized_a.short_description = 'is authorized'

    def is_relevant_a(self, obj):
        if not obj.pk:
            return None
        return getattr(self.get_obj(obj), 'is_relevant')
    is_relevant_a.boolean = True
    is_relevant_a.short_description = 'is relevant'

    def get_ordering(self, request):
        return (
            f'{self.obj_name}__name',
        )


class SemaProductBaseTabularInline(TabularInline):
    model = SemaProduct
    fk_name = None
    formset = LimitedInlineFormSet
    verbose_name_plural = 'products (top 10)'
    all_link_query = None
    extra = 0
    ordering = (
        'product_id',
    )
    classes = (
        'collapse',
    )

    fields = (
        'all_link',
        'details_link',
        'product_id',
        'part_number',
        'dataset',
        'is_authorized',
        'is_relevant'
    )

    readonly_fields = (
        'all_link',
        'details_link'
    )

    def get_rel_obj(self, obj):
        return getattr(obj, self.fk_name)

    def all_link(self, obj):
        query = f'{self.all_link_query}={getattr(self.get_rel_obj(obj), "pk")}'
        return get_changelist_view_link(obj, 'See All', query)
    all_link.short_description = ''

    def details_link(self, obj):
        if not obj.pk:
            return None
        return get_change_view_link(obj, 'Details')
    details_link.short_description = ''

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'dataset':
            formfield.choices = formfield.choices
        return formfield


class SemaProductManyToManyBaseTabularInline(TabularInline):
    model = None
    fk_name = None
    obj_name = 'semaproduct'
    formset = LimitedManyToManyProductInlineFormSet
    verbose_name_plural = 'products (top 10)'
    all_link_query = None
    extra = 0
    classes = (
        'collapse',
    )

    fields = (
        'all_link',
        'details_link',
        'product_id_a',
        'part_number_a',
        'dataset_a',
        'is_authorized_a',
        'is_relevant_a'
    )

    readonly_fields = (
        'all_link',
        'details_link',
        'product_id_a',
        'part_number_a',
        'dataset_a',
        'is_authorized_a',
        'is_relevant_a'
    )

    def get_obj(self, obj):
        return getattr(obj, self.obj_name)

    def get_rel_obj(self, obj):
        return getattr(obj, self.fk_name)

    def all_link(self, obj):
        query = (
            f'{self.all_link_query}'
            f'={getattr(self.get_rel_obj(obj), "pk")}'
        )
        return get_changelist_view_link(
            self.get_obj(obj),
            'See All',
            query
        )
    all_link.short_description = ''

    def details_link(self, obj):
        if not obj.pk:
            return None
        return get_change_view_link(
            self.get_obj(obj),
            'Details'
        )
    details_link.short_description = ''

    def product_id_a(self, obj):
        if not obj.pk:
            return None
        return getattr(self.get_obj(obj), 'product_id')
    product_id_a.short_description = 'product ID'

    def part_number_a(self, obj):
        if not obj.pk:
            return None
        return getattr(self.get_obj(obj), 'part_number')
    part_number_a.short_description = 'part number'

    def dataset_a(self, obj):
        if not obj.pk:
            return None
        return getattr(self.get_obj(obj), 'dataset')
    dataset_a.short_description = 'dataset'

    def is_authorized_a(self, obj):
        if not obj.pk:
            return None
        return getattr(self.get_obj(obj), 'is_authorized')
    is_authorized_a.boolean = True
    is_authorized_a.short_description = 'is authorized'

    def is_relevant_a(self, obj):
        if not obj.pk:
            return None
        return getattr(self.get_obj(obj), 'is_relevant')
    is_relevant_a.boolean = True
    is_relevant_a.short_description = 'is relevant'

    def get_ordering(self, request):
        return (
            f'{self.obj_name}__product_id',
        )


class SemaPiesAttributeBaseTabularInline(TabularInline):
    extra = 0
    ordering = (
        'segment',
    )
    classes = (
        'collapse',
    )

    fields = (
        'details_link',
        'product',
        'segment',
        'value'
    )

    readonly_fields = (
        'details_link',
    )

    def details_link(self, obj):
        if not obj.pk:
            return None
        return get_change_view_link(obj, 'Details')
    details_link.short_description = ''


class SemaBrandDatasetsTabularInline(SemaDatasetBaseTabularInline):
    fk_name = 'brand'
    all_link_query = 'brand__brand_id__exact'


class SemaDatasetCategoriesTabularInline(SemaCategoryManyToManyBaseTabularInline):
    model = SemaDataset.categories.through
    fk_name = 'semadataset'
    all_link_query = 'datasets__dataset_id__exact'


class SemaDatasetVehiclesTabularInline(SemaVehicleManyToManyBaseTabularInline):
    model = SemaDataset.vehicles.through
    fk_name = 'semadataset'
    all_link_query = 'datasets__dataset_id__exact'


class SemaDatasetProductsTabularInline(SemaProductBaseTabularInline):
    fk_name = 'dataset'
    all_link_query = 'dataset__dataset_id__exact'


class SemaYearMakeYearsTabularInline(SemaMakeYearBaseTabularInline):
    fk_name = 'year'
    all_link_query = 'year__year__exact'


class SemaMakeMakeYearsTabularInline(SemaMakeYearBaseTabularInline):
    fk_name = 'make'
    all_link_query = 'make__make_id__exact'


class SemaModelBaseVehiclesTabularInline(SemaBaseVehicleBaseTabularInline):
    fk_name = 'model'
    all_link_query = 'model__model_id__exact'


class SemaSubmodelVehiclesTabularInline(SemaVehicleBaseTabularInline):
    fk_name = 'submodel'
    all_link_query = 'submodel__submodel_id__exact'


class SemaMakeYearBaseVehiclesTabularInline(SemaBaseVehicleBaseTabularInline):
    fk_name = 'make_year'
    all_link_query = 'make_year__id__exact'


class SemaBaseVehicleVehiclesTabularInline(SemaVehicleBaseTabularInline):
    fk_name = 'base_vehicle'
    all_link_query = 'base_vehicle__base_vehicle_id__exact'


class SemaVehicleDatasetsTabularInline(SemaDatasetManyToManyBaseTabularInline):
    model = SemaDataset.vehicles.through
    fk_name = 'semavehicle'
    all_link_query = 'vehicles__vehicle_id__exact'


class SemaVehicleProductsTabularInline(SemaProductManyToManyBaseTabularInline):
    model = SemaProduct.vehicles.through
    fk_name = 'semavehicle'
    all_link_query = 'vehicles__vehicle_id__exact'


class SemaCategoryParentCategoriesTabularInline(SemaCategoryManyToManyBaseTabularInline):
    model = SemaCategory.parent_categories.through
    obj_name = 'from_semacategory'
    fk_name = 'to_semacategory'
    formset = LimitedManyToManyParentCategoryInlineFormSet
    verbose_name_plural = 'parent categories (top 10)'
    all_link_query = 'child_categories__category_id__exact'


class SemaCategoryChildCategoriesTabularInline(SemaCategoryManyToManyBaseTabularInline):
    model = SemaCategory.parent_categories.through
    obj_name = 'to_semacategory'
    fk_name = 'from_semacategory'
    formset = LimitedManyToManyChildCategoryInlineFormSet
    verbose_name_plural = 'child categories (top 10)'
    all_link_query = 'parent_categories__category_id__exact'


class SemaCategoryDatasetsTabularInline(SemaDatasetManyToManyBaseTabularInline):
    model = SemaDataset.categories.through
    fk_name = 'semacategory'
    all_link_query = 'categories__category_id__exact'


class SemaCategoryProductsTabularInline(SemaProductManyToManyBaseTabularInline):
    model = SemaProduct.categories.through
    fk_name = 'semacategory'
    all_link_query = 'categories__category_id__exact'


class SemaProductDescriptionPiesAttributeTabularInline(SemaPiesAttributeBaseTabularInline):
    model = SemaDescriptionPiesAttribute
    verbose_name_plural = 'description PIES'


class SemaProductDigitalAssetsPiesAttributeTabularInline(SemaPiesAttributeBaseTabularInline):
    model = SemaDigitalAssetsPiesAttribute
    verbose_name_plural = 'digital assets PIES'

    def get_fields(self, request, obj=None):
        return super().get_fields(
            request, obj,
        ) + ('image_preview',)

    def get_readonly_fields(self, request, obj=None):
        return super().get_readonly_fields(
            request, obj
        ) + ('image_preview',)

    def image_preview(self, obj):
        if not obj.value:
            return ''
        try:
            return get_image_preview(obj.value, width="100")
        except Exception as err:
            return str(err)
    image_preview.short_description = ''


class SemaProductCategoriesTabularInline(SemaCategoryManyToManyBaseTabularInline):
    model = SemaProduct.categories.through
    fk_name = 'semaproduct'
    all_link_query = 'products__product_id__exact'


class SemaProductVehiclesTabularInline(SemaVehicleManyToManyBaseTabularInline):
    model = SemaProduct.vehicles.through
    fk_name = 'semaproduct'
    all_link_query = 'products__product_id__exact'
