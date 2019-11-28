from django.contrib.admin import SimpleListFilter
from django.db.models import Q, Count, Case, When, F, IntegerField

from core.admin.filters import MayBeRelevantFilter


class HasCategory(SimpleListFilter):
    title = 'has category'
    parameter_name = 'categories'

    def lookups(self, request, model_admin):
        return (
            ('Yes', 'Yes'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'Yes':
            return queryset.filter(~Q(categories=None))
        if self.value() == 'No':
            return queryset.filter(categories=None)


class HasVehicle(SimpleListFilter):
    title = 'has vehicle'
    parameter_name = 'vehicles'

    def lookups(self, request, model_admin):
        return (
            ('Yes', 'Yes'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'Yes':
            return queryset.filter(~Q(vehicles=None))
        if self.value() == 'No':
            return queryset.filter(vehicles=None)


class HasPrimaryImage(SimpleListFilter):
    title = 'has primary image'
    parameter_name = 'primary_image_url'

    def lookups(self, request, model_admin):
        return (
            ('Yes', 'Yes'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'Yes':
            return queryset.filter(
                Q(primary_image_url__isnull=False)
                & ~Q(primary_image_url='')
            )
        if self.value() == 'No':
            return queryset.filter(
                Q(primary_image_url__isnull=True)
                | Q(primary_image_url='')
            )


class ByDecadeFilter(SimpleListFilter):
    title = 'year'
    parameter_name = 'year'

    def lookups(self, request, model_admin):
        return (
            ('1900', '1900s'),
            ('1910', '1910s'),
            ('1920', '1920s'),
            ('1930', '1930s'),
            ('1940', '1940s'),
            ('1950', '1950s'),
            ('1960', '1960s'),
            ('1970', '1970s'),
            ('1980', '1980s'),
            ('1990', '1990s'),
            ('2000', '2000s'),
            ('2010', '2010s'),
            ('2020', '2020s')
        )

    def queryset(self, request, queryset):
        raise Exception("Filter must be defined")


class SemaYearByDecade(ByDecadeFilter):
    def queryset(self, request, queryset):
        if self.value():
            return queryset.with_year_data().filter(decade=int(self.value()))


class SemaMakeYearByDecade(ByDecadeFilter):
    def queryset(self, request, queryset):
        from sema.models import SemaYear

        if self.value():
            years = SemaYear.objects.with_year_data().filter(
                decade=int(self.value())
            )
            return queryset.filter(year__in=years)


class SemaBaseVehicleByDecade(ByDecadeFilter):
    def queryset(self, request, queryset):
        from sema.models import SemaYear

        if self.value():
            years = SemaYear.objects.with_year_data().filter(
                decade=int(self.value())
            )
            return queryset.filter(make_year__year__in=years)


class SemaVehicleByDecade(ByDecadeFilter):
    def queryset(self, request, queryset):
        from sema.models import SemaYear

        if self.value():
            years = SemaYear.objects.with_year_data().filter(
                decade=int(self.value())
            )
            return queryset.filter(
                base_vehicle__make_year__year__in=years
            )


class SemaEngineByDecade(ByDecadeFilter):
    def queryset(self, request, queryset):
        from sema.models import SemaYear

        if self.value():
            years = SemaYear.objects.with_year_data().filter(
                decade=int(self.value())
            )
            return queryset.filter(
                vehicle__base_vehicle__make_year__year__in=years
            )


class ByCategoryLevel(SimpleListFilter):
    title = 'category level'
    parameter_name = 'category_level'

    def lookups(self, request, model_admin):
        return (
            ('1', 'Root'),
            ('2', 'Branch'),
            ('3', 'Leaf')
        )

    def queryset(self, request, queryset):
        if self.value() == '1':
            return queryset.filter(
                Q(parent_categories=None)
                & ~Q(child_categories=None)
            )

        if self.value() == '2':
            return queryset.filter(
                ~Q(parent_categories=None)
                & ~Q(child_categories=None)
            )

        if self.value() == '3':
            return queryset.filter(
                ~Q(parent_categories=None)
                & Q(child_categories=None)
            )


class HasHtml(SimpleListFilter):
    title = 'has HTML'
    parameter_name = 'html'

    def lookups(self, request, model_admin):
        return (
            ('Yes', 'Yes'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'Yes':
            return queryset.filter(
                Q(html__isnull=False)
                & ~Q(html='')
            )
        if self.value() == 'No':
            return queryset.filter(
                Q(html__isnull=True)
                | Q(html='')
            )


class HasItem(SimpleListFilter):
    title = 'part of main item'
    parameter_name = 'item'

    def lookups(self, request, model_admin):
        return (
            ('Yes', 'Yes'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'Yes':
            return queryset.filter(item__isnull=False)
        if self.value() == 'No':
            return queryset.filter(item__isnull=True)


class SemaBrandMayBeRelevant(MayBeRelevantFilter):
    def queryset(self, request, queryset):
        queryset = queryset.annotate(
            _dataset_relevant_count=Count(
                'datasets',
                filter=Q(datasets__is_relevant=True),
                distinct=True
            )
        )
        if self.value() == 'Yes':
            return queryset.filter(_dataset_relevant_count__gt=0)
        if self.value() == 'No':
            return queryset.filter(_dataset_relevant_count=0)


class SemaYearMayBeRelevant(MayBeRelevantFilter):
    def queryset(self, request, queryset):
        queryset = queryset.annotate(
            _vehicle_relevant_count=Count(
                'make_years__base_vehicles__vehicles',
                filter=(
                    Q(make_years__base_vehicles__vehicles__is_relevant=True)
                ),
                distinct=True
            )
        )
        if self.value() == 'Yes':
            return queryset.filter(_vehicle_relevant_count__gt=0)
        if self.value() == 'No':
            return queryset.filter(_vehicle_relevant_count=0)


class SemaModelMayBeRelevant(MayBeRelevantFilter):
    def queryset(self, request, queryset):
        queryset = queryset.annotate(
            _vehicle_relevant_count=Count(
                'base_vehicles__vehicles',
                filter=(
                    Q(base_vehicles__vehicles__is_relevant=True)
                ),
                distinct=True
            )
        )
        if self.value() == 'Yes':
            return queryset.filter(_vehicle_relevant_count__gt=0)
        if self.value() == 'No':
            return queryset.filter(_vehicle_relevant_count=0)


class SemaSubmodelMayBeRelevant(MayBeRelevantFilter):
    def queryset(self, request, queryset):
        queryset = queryset.annotate(
            _vehicle_relevant_count=Count(
                'vehicles',
                filter=(
                    Q(vehicles__is_relevant=True)
                ),
                distinct=True
            )
        )
        if self.value() == 'Yes':
            return queryset.filter(_vehicle_relevant_count__gt=0)
        if self.value() == 'No':
            return queryset.filter(_vehicle_relevant_count=0)


class SemaMakeYearMayBeRelevant(MayBeRelevantFilter):
    def queryset(self, request, queryset):
        queryset = queryset.annotate(
            _vehicle_relevant_count=Count(
                'base_vehicles__vehicles',
                filter=(
                    Q(base_vehicles__vehicles__is_relevant=True)
                ),
                distinct=True
            )
        )
        if self.value() == 'Yes':
            return queryset.filter(_vehicle_relevant_count__gt=0)
        if self.value() == 'No':
            return queryset.filter(_vehicle_relevant_count=0)


class SemaBaseVehicleMayBeRelevant(MayBeRelevantFilter):
    def queryset(self, request, queryset):
        queryset = queryset.annotate(
            _vehicle_relevant_count=Count(
                'vehicles',
                filter=(
                    Q(vehicles__is_relevant=True)
                ),
                distinct=True
            )
        )
        if self.value() == 'Yes':
            return queryset.filter(_vehicle_relevant_count__gt=0)
        if self.value() == 'No':
            return queryset.filter(_vehicle_relevant_count=0)


class SemaVehicleMayBeRelevant(MayBeRelevantFilter):
    def queryset(self, request, queryset):
        queryset = queryset.annotate(
            _engine_relevant_count=Count(
                'engines',
                filter=Q(engines__is_relevant=True),
                distinct=True
            )
        )
        if self.value() == 'Yes':
            return queryset.filter(_engine_relevant_count__gt=0)
        if self.value() == 'No':
            return queryset.filter(_engine_relevant_count=0)


class SemaEngineMayBeRelevant(MayBeRelevantFilter):
    def queryset(self, request, queryset):
        if self.value() == 'Yes':
            return queryset.filter(
                Q(vehicle__base_vehicle__make_year__make__is_relevant=True)
                & Q(fuel_type__exact='DIESEL')
            )
        if self.value() == 'No':
            return queryset.filter(
                Q(vehicle__base_vehicle__make_year__make__is_relevant=False)
                | ~Q(fuel_type__exact='DIESEL')
            )


class SemaCategoryMayBeRelevant(MayBeRelevantFilter):
    def queryset(self, request, queryset):
        if self.value() == 'Yes':
            return queryset
        if self.value() == 'No':
            return queryset.none()


class SemaProductMayBeRelevant(MayBeRelevantFilter):
    def queryset(self, request, queryset):
        queryset = queryset.annotate(
            _vehicle_count=Count(
                'vehicles',
                distinct=True
            ),
            _dataset_vehicle_relevant_count=Count(
                'dataset__vehicles',
                filter=Q(dataset__vehicles__is_relevant=True),
                distinct=True
            ),
            _product_vehicle_relevant_count=Count(
                'vehicles',
                filter=Q(vehicles__is_relevant=True),
                distinct=True
            ),
            _vehicle_relevant_count=Case(
                When(
                    _vehicle_count=0,
                    then=F('_dataset_vehicle_relevant_count')
                ),
                default=F('_product_vehicle_relevant_count'),
                output_field=IntegerField()
            )
        )

        if self.value() == 'Yes':
            return queryset.filter(
                Q(dataset__is_relevant=True)
                & Q(_vehicle_relevant_count__gt=0)
            )
        if self.value() == 'No':
            return queryset.filter(
                Q(dataset__is_relevant=False)
                | Q(_vehicle_relevant_count=0)
            )
