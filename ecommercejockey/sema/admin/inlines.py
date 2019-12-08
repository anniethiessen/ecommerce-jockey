from django.contrib.admin import TabularInline

from core.admin.forms import LimitedInlineFormSet
from core.admin.utils import (
    get_change_view_link,
    get_changelist_view_link,
    get_image_preview
)
from ..models import (
    SemaBaseVehicle,
    SemaCategory,
    SemaDataset,
    SemaDescriptionPiesAttribute,
    SemaDigitalAssetsPiesAttribute,
    SemaEngine,
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

    readonly_fields = (
        'relevancy_warnings',
        'relevancy_errors',
        'detail_link',
        'all_link',
        'category_count',
        'vehicle_count',
        'product_count'
    )

    def get_rel_obj(self, obj):
        return getattr(obj, self.fk_name)

    def all_link(self, obj):
        query = f'{self.all_link_query}={getattr(self.get_rel_obj(obj), "pk")}'
        return get_changelist_view_link(obj._meta.model, 'See All', query)
    all_link.short_description = ''

    def detail_link(self, obj):
        if not obj.pk:
            return None
        return get_change_view_link(obj, 'Details')
    detail_link.short_description = ''

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

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'brand':
            formfield.choices = formfield.choices
        return formfield

    def get_queryset(self, request):
        # return super().get_queryset(request).filter(is_relevant=True).with_admin_data()
        return super().get_queryset(request).filter(is_relevant=True)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)

        if obj and not request.user.is_superuser:
            readonly_fields += (
                'dataset_id',
            )

        return readonly_fields


class SemaDatasetManyToManyBaseTabularInline(TabularInline):
    model = None
    fk_name = None
    obj_name = 'semadataset'
    formset = LimitedInlineFormSet
    verbose_name_plural = 'datasets (top 10)'
    all_link_query = None
    extra = 0
    classes = (
        'collapse',
    )

    fields = (
        'all_link',
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

    readonly_fields = (
        'dataset_id',
        'name',
        'brand',
        'is_authorized',
        'is_relevant',
        'relevancy_warnings',
        'relevancy_errors',
        'all_link',
        'detail_link',
        'category_count',
        'vehicle_count',
        'product_count'
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
            self.get_obj(obj)._meta.model,
            'See All',
            query
        )
    all_link.short_description = ''

    def detail_link(self, obj):
        if not obj.pk:
            return None
        return get_change_view_link(
            self.get_obj(obj),
            'Details'
        )
    detail_link.short_description = ''

    def category_count(self, obj):
        if not obj.pk:
            return None

        o = self.get_obj(obj)
        return (
            f"{getattr(o, 'category_relevant_count')}"
            f"/{getattr(o, 'category_count')}"
        )
    category_count.short_description = 'category count'

    def vehicle_count(self, obj):
        if not obj.pk:
            return None

        o = self.get_obj(obj)
        return (
            f"{getattr(o, 'vehicle_relevant_count')}"
            f"/{getattr(o, 'vehicle_count')}"
        )
    vehicle_count.short_description = 'vehicle count'

    def product_count(self, obj):
        if not obj.pk:
            return None

        o = self.get_obj(obj)
        return (
            f"{getattr(o, 'product_relevant_count')}"
            f"/{getattr(o, 'product_count')}"
        )
    product_count.short_description = 'product count'

    def relevancy_warnings(self, obj):
        if not obj.pk:
            return None

        return getattr(self.get_obj(obj), 'relevancy_warnings')
    relevancy_warnings.short_description = 'warnings'

    def relevancy_errors(self, obj):
        if not obj.pk:
            return None

        return getattr(self.get_obj(obj), 'relevancy_errors')
    relevancy_errors.short_description = 'errors'

    def dataset_id(self, obj):
        if not obj.pk:
            return None
        return getattr(self.get_obj(obj), 'dataset_id')
    dataset_id.short_description = 'dataset ID'

    def name(self, obj):
        if not obj.pk:
            return None
        return getattr(self.get_obj(obj), 'name')
    name.short_description = 'name'

    def brand(self, obj):
        if not obj.pk:
            return None
        return getattr(self.get_obj(obj), 'brand')
    brand.short_description = 'brand'

    def is_authorized(self, obj):
        if not obj.pk:
            return None
        return getattr(self.get_obj(obj), 'is_authorized')
    is_authorized.boolean = True
    is_authorized.short_description = 'is authorized'

    def is_relevant(self, obj):
        if not obj.pk:
            return None
        return getattr(self.get_obj(obj), 'is_relevant')
    is_relevant.boolean = True
    is_relevant.short_description = 'is relevant'

    def get_ordering(self, request):
        return (
            f'{self.obj_name}__name',
        )

    def get_queryset(self, request):
        filter_dict = {f'{self.obj_name}__is_relevant': True}
        return super().get_queryset(request).filter(
            **filter_dict
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
        'detail_link',
        'id',
        'year',
        'make',
        'base_vehicle_count',
        'is_authorized',
        'may_be_relevant_flag',
        'is_relevant',
        'relevancy_warnings',
        'relevancy_errors',
        'relevancy_exception'
    )

    readonly_fields = (
        'id',
        'relevancy_warnings',
        'relevancy_errors',
        'may_be_relevant_flag',
        'all_link',
        'detail_link',
        'base_vehicle_count'
    )

    def get_rel_obj(self, obj):
        return getattr(obj, self.fk_name)

    def all_link(self, obj):
        query = f'{self.all_link_query}={getattr(self.get_rel_obj(obj), "pk")}'
        return get_changelist_view_link(obj._meta.model, 'See All', query)
    all_link.short_description = ''

    def detail_link(self, obj):
        if not obj.pk:
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

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, **kwargs)
        if db_field.name in ['year', 'make']:
            formfield.choices = formfield.choices
        return formfield

    def get_queryset(self, request):
        return super().get_queryset(request).filter(
            is_relevant=True
        ).with_admin_data()


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
        'detail_link',
        'base_vehicle_id',
        'make_year',
        'model',
        'vehicle_count',
        'is_authorized',
        'may_be_relevant_flag',
        'is_relevant',
        'relevancy_warnings',
        'relevancy_errors',
        'relevancy_exception'
    )

    readonly_fields = (
        'relevancy_warnings',
        'relevancy_errors',
        'may_be_relevant_flag',
        'all_link',
        'detail_link',
        'vehicle_count'
    )

    def get_rel_obj(self, obj):
        return getattr(obj, self.fk_name)

    def all_link(self, obj):
        query = f'{self.all_link_query}={getattr(self.get_rel_obj(obj), "pk")}'
        return get_changelist_view_link(obj._meta.model, 'See All', query)
    all_link.short_description = ''

    def detail_link(self, obj):
        if not obj.pk:
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

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, **kwargs)
        if db_field.name in ['make_year', 'model']:
            formfield.choices = formfield.choices
        return formfield

    def get_queryset(self, request):
        return super().get_queryset(request).filter(
            is_relevant=True
        ).with_admin_data()

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)

        if obj and not request.user.is_superuser:
            readonly_fields += (
                'base_vehicle_id',
            )

        return readonly_fields


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
        'relevancy_errors',
        'relevancy_exception'
    )

    readonly_fields = (
        'relevancy_warnings',
        'relevancy_errors',
        'may_be_relevant_flag',
        'all_link',
        'detail_link',
        'engine_count',
        'dataset_count',
        'product_count'
    )

    def get_rel_obj(self, obj):
        return getattr(obj, self.fk_name)

    def all_link(self, obj):
        query = f'{self.all_link_query}={getattr(self.get_rel_obj(obj), "pk")}'
        return get_changelist_view_link(obj._meta.model, 'See All', query)
    all_link.short_description = ''

    def detail_link(self, obj):
        if not obj.pk:
            return None
        return get_change_view_link(obj, 'Details')
    detail_link.short_description = ''

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

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, **kwargs)
        if db_field.name in ['base_vehicle', 'submodel']:
            formfield.choices = formfield.choices
        return formfield

    def get_queryset(self, request):
        return super().get_queryset(request).filter(
            is_relevant=True
        ).with_admin_data()

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)

        if obj and not request.user.is_superuser:
            readonly_fields += (
                'vehicle_id',
            )

        return readonly_fields


class SemaEngineBaseTabularInline(TabularInline):
    model = SemaEngine
    fk_name = None
    formset = LimitedInlineFormSet
    verbose_name_plural = 'engines (top 10)'
    all_link_query = None
    extra = 0
    classes = (
        'collapse',
    )

    fields = (
        'all_link',
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
        'relevancy_errors',
        'relevancy_exception'
    )

    readonly_fields = (
        'id',
        'relevancy_warnings',
        'relevancy_errors',
        'may_be_relevant_flag',
        'all_link',
        'detail_link'
    )

    def get_rel_obj(self, obj):
        return getattr(obj, self.fk_name)

    def all_link(self, obj):
        query = f'{self.all_link_query}={getattr(self.get_rel_obj(obj), "pk")}'
        return get_changelist_view_link(obj._meta.model, 'See All', query)
    all_link.short_description = ''

    def detail_link(self, obj):
        if not obj.pk:
            return None
        return get_change_view_link(obj, 'Details')
    detail_link.short_description = ''

    def may_be_relevant_flag(self, obj):
        if not obj or not obj.pk:
            return None

        if obj.is_relevant != obj.may_be_relevant:
            return '~'
        else:
            return ''
    may_be_relevant_flag.short_description = ''

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'vehicle':
            formfield.choices = formfield.choices
        return formfield

    def get_queryset(self, request):
        return super().get_queryset(request).filter(
            is_relevant=True
        ).with_admin_data()


class SemaVehicleManyToManyBaseTabularInline(TabularInline):
    model = None
    fk_name = None
    obj_name = 'semavehicle'
    formset = LimitedInlineFormSet
    verbose_name_plural = 'vehicles (top 10)'
    all_link_query = None
    extra = 0
    classes = (
        'collapse',
    )

    fields = (
        'all_link',
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
        'relevancy_errors',
        'relevancy_exception'
    )

    readonly_fields = (
        'vehicle_id',
        'base_vehicle',
        'submodel',
        'is_authorized',
        'is_relevant',
        'may_be_relevant_flag',
        'relevancy_warnings',
        'relevancy_errors',
        'relevancy_exception',
        'all_link',
        'detail_link',
        'engine_count',
        'dataset_count',
        'product_count'
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
            self.get_obj(obj)._meta.model,
            'See All',
            query
        )
    all_link.short_description = ''

    def detail_link(self, obj):
        if not obj.pk:
            return None
        return get_change_view_link(
            self.get_obj(obj),
            'Details'
        )
    detail_link.short_description = ''

    def engine_count(self, obj):
        if not obj.pk:
            return None

        o = self.get_obj(obj)
        return (
            f"{getattr(o, 'engine_relevant_count')}"
            f"/{getattr(o, 'engine_count')}"
        )
    engine_count.short_description = 'engine count'

    def dataset_count(self, obj):
        if not obj.pk:
            return None

        o = self.get_obj(obj)
        return (
            f"{getattr(o, 'dataset_relevant_count')}"
            f"/{getattr(o, 'dataset_count')}"
        )
    dataset_count.short_description = 'dataset count'

    def product_count(self, obj):
        if not obj.pk:
            return None

        o = self.get_obj(obj)
        return (
            f"{getattr(o, 'product_relevant_count')}"
            f"/{getattr(o, 'product_count')}"
        )
    product_count.short_description = 'product count'

    def relevancy_warnings(self, obj):
        if not obj.pk:
            return None

        return getattr(self.get_obj(obj), 'relevancy_warnings')
    relevancy_warnings.short_description = 'warnings'

    def relevancy_errors(self, obj):
        if not obj.pk:
            return None

        return getattr(self.get_obj(obj), 'relevancy_errors')
    relevancy_errors.short_description = 'errors'

    def relevancy_exception(self, obj):
        if not obj.pk:
            return None

        return getattr(self.get_obj(obj), 'relevancy_exception')
    relevancy_exception.short_description = 'exception'

    def may_be_relevant_flag(self, obj):
        if not obj:
            return None

        if getattr(self.get_obj(obj), 'is_relevant') != getattr(self.get_obj(obj), 'may_be_relevant'):
            return '~'
        else:
            return ''
    may_be_relevant_flag.short_description = ''

    def vehicle_id(self, obj):
        if not obj.pk:
            return None
        return getattr(self.get_obj(obj), 'vehicle_id')
    vehicle_id.short_description = 'vehicle ID'

    def base_vehicle(self, obj):
        if not obj.pk:
            return None
        return getattr(self.get_obj(obj), 'base_vehicle')
    base_vehicle.short_description = 'base vehicle'

    def submodel(self, obj):
        if not obj.pk:
            return None
        return getattr(self.get_obj(obj), 'submodel')
    submodel.short_description = 'submodel'

    def is_authorized(self, obj):
        if not obj.pk:
            return None
        return getattr(self.get_obj(obj), 'is_authorized')
    is_authorized.boolean = True
    is_authorized.short_description = 'is authorized'

    def is_relevant(self, obj):
        if not obj.pk:
            return None
        return getattr(self.get_obj(obj), 'is_relevant')
    is_relevant.boolean = True
    is_relevant.short_description = 'is relevant'

    def get_ordering(self, request):
        return (
            f'{self.obj_name}__base_vehicle',
            f'{self.obj_name}__submodel'
        )

    def get_queryset(self, request):
        filter_dict = {f'{self.obj_name}__is_relevant': True}
        return super().get_queryset(request).filter(
            **filter_dict
        )


class SemaCategoryManyToManyBaseTabularInline(TabularInline):
    model = None
    fk_name = None
    obj_name = 'semacategory'
    formset = LimitedInlineFormSet
    verbose_name_plural = 'categories (top 10)'
    all_link_query = None
    extra = 0
    classes = (
        'collapse',
    )

    fields = (
        'all_link',
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
        'relevancy_errors',
        'relevancy_exception'
    )

    readonly_fields = (
        'category_id',
        'name',
        'level',
        'is_authorized',
        'is_relevant',
        'may_be_relevant_flag',
        'relevancy_warnings',
        'relevancy_errors',
        'relevancy_exception',
        'all_link',
        'detail_link',
        'parent_category_count',
        'child_category_count',
        'dataset_count',
        'product_count'
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
            self.get_obj(obj)._meta.model,
            'See All',
            query
        )
    all_link.short_description = ''

    def detail_link(self, obj):
        if not obj.pk:
            return None
        return get_change_view_link(
            self.get_obj(obj),
            'Details'
        )
    detail_link.short_description = ''

    def parent_category_count(self, obj):
        if not obj.pk:
            return None

        o = self.get_obj(obj)
        return (
            f"{getattr(o, 'parent_category_relevant_count')}"
            f"/{getattr(o, 'parent_category_count')}"
        )
    parent_category_count.short_description = 'parent count'

    def child_category_count(self, obj):
        if not obj.pk:
            return None

        o = self.get_obj(obj)
        return (
            f"{getattr(o, 'child_category_relevant_count')}"
            f"/{getattr(o, 'child_category_count')}"
        )
    child_category_count.short_description = 'child count'

    def dataset_count(self, obj):
        if not obj.pk:
            return None

        o = self.get_obj(obj)
        return (
            f"{getattr(o, 'dataset_relevant_count')}"
            f"/{getattr(o, 'dataset_count')}"
        )
    dataset_count.short_description = 'dataset count'

    def product_count(self, obj):
        if not obj.pk:
            return None

        o = self.get_obj(obj)
        return (
            f"{getattr(o, 'product_relevant_count')}"
            f"/{getattr(o, 'product_count')}"
        )
    product_count.short_description = 'product count'

    def relevancy_warnings(self, obj):
        if not obj.pk:
            return None

        return getattr(self.get_obj(obj), 'relevancy_warnings')
    relevancy_warnings.short_description = 'warnings'

    def relevancy_errors(self, obj):
        if not obj.pk:
            return None

        return getattr(self.get_obj(obj), 'relevancy_errors')
    relevancy_errors.short_description = 'errors'

    def relevancy_exception(self, obj):
        if not obj.pk:
            return None

        return getattr(self.get_obj(obj), 'relevancy_exception')
    relevancy_exception.short_description = 'exception'

    def may_be_relevant_flag(self, obj):
        if not obj:
            return None

        if getattr(self.get_obj(obj), 'is_relevant') != getattr(
                self.get_obj(obj), 'may_be_relevant'):
            return '~'
        else:
            return ''
    may_be_relevant_flag.short_description = ''

    def category_id(self, obj):
        if not obj.pk:
            return None
        return getattr(self.get_obj(obj), 'category_id')
    category_id.short_description = 'category ID'

    def name(self, obj):
        if not obj.pk:
            return None
        return getattr(self.get_obj(obj), 'name')
    name.short_description = 'name'

    def level(self, obj):
        if not obj.pk:
            return None
        return getattr(self.get_obj(obj), 'level')
    level.short_description = 'level'

    def is_authorized(self, obj):
        if not obj.pk:
            return None
        return getattr(self.get_obj(obj), 'is_authorized')
    is_authorized.boolean = True
    is_authorized.short_description = 'is authorized'

    def is_relevant(self, obj):
        if not obj.pk:
            return None
        return getattr(self.get_obj(obj), 'is_relevant')
    is_relevant.boolean = True
    is_relevant.short_description = 'is relevant'

    def get_ordering(self, request):
        return (
            f'{self.obj_name}__name',
        )

    def get_queryset(self, request):
        filter_dict = {f'{self.obj_name}__is_relevant': True}
        return super().get_queryset(request).filter(
            **filter_dict
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
        'relevancy_errors',
        'relevancy_exception'
    )

    readonly_fields = (
        'relevancy_warnings',
        'relevancy_errors',
        'may_be_relevant_flag',
        'all_link',
        'detail_link',
        'description_pies_attribute_count',
        'digital_assets_pies_attribute_count',
        'category_count',
        'vehicle_count'
    )

    def get_rel_obj(self, obj):
        return getattr(obj, self.fk_name)

    def all_link(self, obj):
        query = f'{self.all_link_query}={getattr(self.get_rel_obj(obj), "pk")}'
        return get_changelist_view_link(obj._meta.model, 'See All', query)
    all_link.short_description = ''

    def detail_link(self, obj):
        if not obj.pk:
            return None
        return get_change_view_link(obj, 'Details')
    detail_link.short_description = ''

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

        return f'{obj.vehicle_relevant_count}/{obj.vehicle_count}'
    # vehicle_count.admin_order_field = '_vehicle_relevant_count'
    vehicle_count.short_description = 'vehicle count'

    def may_be_relevant_flag(self, obj):
        if not obj or not obj.pk:
            return None

        if obj.is_relevant != obj.may_be_relevant:
            return '~'
        else:
            return ''
    may_be_relevant_flag.short_description = ''

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'dataset':
            formfield.choices = formfield.choices
        return formfield

    def get_queryset(self, request):
        # return super().get_queryset(request).filter(
        #     is_relevant=True
        # ).with_admin_data()
        return super().get_queryset(request).filter(is_relevant=True)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)

        if obj and not request.user.is_superuser:
            readonly_fields += (
                'product_id',
            )

        return readonly_fields


class SemaProductManyToManyBaseTabularInline(TabularInline):
    model = None
    fk_name = None
    obj_name = 'semaproduct'
    formset = LimitedInlineFormSet
    verbose_name_plural = 'products (top 10)'
    all_link_query = None
    extra = 0
    classes = (
        'collapse',
    )

    fields = (
        'all_link',
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
        'relevancy_errors',
        'relevancy_exception'
    )

    readonly_fields = (
        'product_id',
        'part_number',
        'dataset',
        'is_authorized',
        'is_relevant',
        'may_be_relevant_flag',
        'relevancy_warnings',
        'relevancy_errors',
        'relevancy_exception',
        'all_link',
        'detail_link',
        'description_pies_attribute_count',
        'digital_assets_pies_attribute_count',
        'category_count',
        'vehicle_count'
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
            self.get_obj(obj)._meta.model,
            'See All',
            query
        )
    all_link.short_description = ''

    def detail_link(self, obj):
        if not obj.pk:
            return None
        return get_change_view_link(
            self.get_obj(obj),
            'Details'
        )
    detail_link.short_description = ''

    def description_pies_attribute_count(self, obj):
        if not obj.pk:
            return None

        return getattr(self.get_obj(obj), 'description_pies_attribute_count')
    description_pies_attribute_count.short_description = 'description count'

    def digital_assets_pies_attribute_count(self, obj):
        if not obj.pk:
            return None

        return getattr(
            self.get_obj(obj),
            'digital_assets_pies_attribute_count'
        )
    digital_assets_pies_attribute_count.short_description = (
        'digital assets count'
    )

    def category_count(self, obj):
        if not obj.pk:
            return None

        o = self.get_obj(obj)
        return (
            f"{getattr(o, 'category_relevant_count')}"
            f"/{getattr(o, 'category_count')}"
        )
    category_count.short_description = 'category count'

    def vehicle_count(self, obj):
        if not obj.pk:
            return None

        o = self.get_obj(obj)
        return (
            f"{getattr(o, 'vehicle_relevant_count')}"
            f"/{getattr(o, 'vehicle_count')}"
        )
    vehicle_count.short_description = 'vehicle count'

    def relevancy_warnings(self, obj):
        if not obj.pk:
            return None

        return getattr(self.get_obj(obj), 'relevancy_warnings')
    relevancy_warnings.short_description = 'warnings'

    def relevancy_errors(self, obj):
        if not obj.pk:
            return None

        return getattr(self.get_obj(obj), 'relevancy_errors')
    relevancy_errors.short_description = 'errors'

    def relevancy_exception(self, obj):
        if not obj.pk:
            return None

        return getattr(self.get_obj(obj), 'relevancy_exception')
    relevancy_exception.short_description = 'exception'

    def may_be_relevant_flag(self, obj):
        if not obj:
            return None

        if getattr(self.get_obj(obj), 'is_relevant') != getattr(
                self.get_obj(obj), 'may_be_relevant'):
            return '~'
        else:
            return ''
    may_be_relevant_flag.short_description = ''

    def product_id(self, obj):
        if not obj.pk:
            return None
        return getattr(self.get_obj(obj), 'product_id')
    product_id.short_description = 'product ID'

    def part_number(self, obj):
        if not obj.pk:
            return None
        return getattr(self.get_obj(obj), 'part_number')
    part_number.short_description = 'part number'

    def dataset(self, obj):
        if not obj.pk:
            return None
        return getattr(self.get_obj(obj), 'dataset')
    dataset.short_description = 'dataset'

    def is_authorized(self, obj):
        if not obj.pk:
            return None
        return getattr(self.get_obj(obj), 'is_authorized')
    is_authorized.boolean = True
    is_authorized.short_description = 'is authorized'

    def is_relevant(self, obj):
        if not obj.pk:
            return None
        return getattr(self.get_obj(obj), 'is_relevant')
    is_relevant.boolean = True
    is_relevant.short_description = 'is relevant'

    def get_ordering(self, request):
        return (
            f'{self.obj_name}__product_id',
        )

    def get_queryset(self, request):
        filter_dict = {f'{self.obj_name}__is_relevant': True}
        return super().get_queryset(request).filter(
            **filter_dict
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
        'detail_link',
        'id',
        'product',
        'segment',
        'value'
    )

    readonly_fields = (
        'id',
        'detail_link'
    )

    def detail_link(self, obj):
        if not obj.pk:
            return None
        return get_change_view_link(obj, 'Details')
    detail_link.short_description = ''


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


class SemaVehicleEnginesTabularInline(SemaEngineBaseTabularInline):
    fk_name = 'vehicle'
    all_link_query = 'vehicle__vehicle_id__exact'


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
    obj_name = 'to_semacategory'
    fk_name = 'from_semacategory'
    formset = LimitedInlineFormSet
    verbose_name_plural = 'parent categories (top 10)'
    all_link_query = 'child_categories__category_id__exact'


class SemaCategoryChildCategoriesTabularInline(SemaCategoryManyToManyBaseTabularInline):
    model = SemaCategory.parent_categories.through
    obj_name = 'from_semacategory'
    fk_name = 'to_semacategory'
    formset = LimitedInlineFormSet
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

    def image_preview(self, obj):
        if not obj.value:
            return ''
        try:
            return get_image_preview(obj.value)
        except Exception as err:
            return str(err)
    image_preview.short_description = ''

    def get_fields(self, request, obj=None):
        return super().get_fields(
            request, obj,
        ) + ('image_preview',)

    def get_readonly_fields(self, request, obj=None):
        return super().get_readonly_fields(
            request, obj
        ) + ('image_preview',)


class SemaProductCategoriesTabularInline(SemaCategoryManyToManyBaseTabularInline):
    model = SemaProduct.categories.through
    fk_name = 'semaproduct'
    all_link_query = 'products__product_id__exact'


class SemaProductVehiclesTabularInline(SemaVehicleManyToManyBaseTabularInline):
    model = SemaProduct.vehicles.through
    fk_name = 'semaproduct'
    all_link_query = 'products__product_id__exact'
