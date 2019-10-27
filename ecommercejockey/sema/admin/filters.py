from django.contrib.admin import SimpleListFilter
from django.db.models import Q  # Case, When, BooleanField

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
    parameter_name = 'items'

    def lookups(self, request, model_admin):
        return (
            ('Yes', 'Yes'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'Yes':
            return queryset.filter(items__isnull=False)
        if self.value() == 'No':
            return queryset.filter(items__isnull=True)


class SemaDatasetMayBeRelevant(MayBeRelevantFilter):
    def queryset(self, request, queryset):
        if self.value() == 'Yes':
            return queryset.filter(brand__is_relevant=True)
        if self.value() == 'No':
            return queryset.filter(brand__is_relevant=False)


class SemaMakeYearMayBeRelevant(MayBeRelevantFilter):
    def queryset(self, request, queryset):
        if self.value() == 'Yes':
            return queryset.filter(
                Q(year__is_relevant=True)
                & Q(make__is_relevant=True)
            )
        if self.value() == 'No':
            return queryset.filter(
                Q(year__is_relevant=False)
                | Q(make__is_relevant=False)
            )


class SemaBaseVehicleMayBeRelevant(MayBeRelevantFilter):
    def queryset(self, request, queryset):
        if self.value() == 'Yes':
            return queryset.filter(
                Q(make_year__is_relevant=True)
                & Q(model__is_relevant=True)
            )
        if self.value() == 'No':
            return queryset.filter(
                Q(make_year__is_relevant=False)
                | Q(model__is_relevant=False)
            )


class SemaVehicleMayBeRelevant(MayBeRelevantFilter):
    def queryset(self, request, queryset):
        if self.value() == 'Yes':
            return queryset.filter(
                Q(base_vehicle__is_relevant=True)
                & Q(submodel__is_relevant=True)
            )
        if self.value() == 'No':
            return queryset.filter(
                Q(base_vehicle__is_relevant=False)
                | Q(submodel__is_relevant=False)
            )


# class SemaCategoryMayBeRelevant(MayBeRelevantFilter):  # FIXME
#     def queryset(self, request, queryset):
#         from ..models import SemaProduct
#         relevant_products = SemaProduct.objects.filter(is_relevant=True)
#
#         queryset = queryset.order_by('name').annotate(
#             _has_relevant_products=Case(
#                 When(
#                     Q(products__in=relevant_products),
#                     then=True
#                 ),
#                 default=False,
#                 output_field=BooleanField()
#             )
#         ).order_by(
#             'name',
#             '-_has_relevant_products'
#         ).distinct('name')
#
#         if self.value() == 'Yes':
#             return queryset.filter(_has_relevant_products=True)
#         if self.value() == 'No':
#             return queryset.filter(_has_relevant_products=False)


# class SemaProductMayBeRelevant(MayBeRelevantFilter):  # FIXME
#     def queryset(self, request, queryset):
#         from ..models import SemaVehicle
#
#         relevant_vehicles = SemaVehicle.objects.filter(is_relevant=True)
#
#         queryset = queryset.annotate(
#             _has_relevant_vehicles=Case(
#                 When(
#                     Q(vehicles__in=relevant_vehicles),
#                     then=True
#                 ),
#                 default=False,
#                 output_field=BooleanField()
#             )
#         ).order_by(
#             'dataset_id',
#             'part_number',
#             '-_has_relevant_vehicles'
#         ).distinct('dataset_id', 'part_number')
#
#         if self.value() == 'Yes':
#             return queryset.filter(
#                 Q(dataset__is_relevant=True)
#                 & Q(_has_relevant_vehicles=True)
#             )
#         if self.value() == 'No':
#             return queryset.filter(
#                 Q(dataset__is_relevant=False)
#                 | Q(_has_relevant_vehicles=False)
#             )
