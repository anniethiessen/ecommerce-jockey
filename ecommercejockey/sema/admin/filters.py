from django.contrib.admin import SimpleListFilter
from django.db.models import Q, Count, Case, When, F, IntegerField

from core.admin.filters import (
    BooleanBaseListFilter,
    LevelBaseListFilter,
    MayBeRelevantBaseListFilter
)


class HasCategory(BooleanBaseListFilter):
    title = 'has category'
    parameter_name = 'categories'

    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(~Q(categories=None))

        if self.value() == 'False':
            return queryset.filter(categories=None)


class HasVehicle(BooleanBaseListFilter):
    title = 'has vehicle'
    parameter_name = 'vehicles'

    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(~Q(vehicles=None))

        if self.value() == 'False':
            return queryset.filter(vehicles=None)


class HasPrimaryImage(BooleanBaseListFilter):
    title = 'has primary image'
    parameter_name = 'primary_image_url'

    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(
                Q(primary_image_url__isnull=False)
                & ~Q(primary_image_url='')
            )

        if self.value() == 'False':
            return queryset.filter(
                Q(primary_image_url__isnull=True)
                | Q(primary_image_url='')
            )


class ByDecadeBaseListFilter(SimpleListFilter):
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


class SemaYearByDecade(ByDecadeBaseListFilter):
    def queryset(self, request, queryset):
        if self.value():
            return queryset.with_year_data().filter(decade=int(self.value()))


class SemaMakeYearByDecade(ByDecadeBaseListFilter):
    def queryset(self, request, queryset):
        from sema.models import SemaYear

        if self.value():
            years = SemaYear.objects.with_year_data().filter(
                decade=int(self.value())
            )

            return queryset.filter(year__in=years)


class SemaBaseVehicleByDecade(ByDecadeBaseListFilter):
    def queryset(self, request, queryset):
        from sema.models import SemaYear

        if self.value():
            years = SemaYear.objects.with_year_data().filter(
                decade=int(self.value())
            )

            return queryset.filter(make_year__year__in=years)


class SemaVehicleByDecade(ByDecadeBaseListFilter):
    def queryset(self, request, queryset):
        from sema.models import SemaYear

        if self.value():
            years = SemaYear.objects.with_year_data().filter(
                decade=int(self.value())
            )

            return queryset.filter(
                base_vehicle__make_year__year__in=years
            )


class SemaEngineByDecade(ByDecadeBaseListFilter):
    def queryset(self, request, queryset):
        from sema.models import SemaYear

        if self.value():
            years = SemaYear.objects.with_year_data().filter(
                decade=int(self.value())
            )

            return queryset.filter(
                vehicle__base_vehicle__make_year__year__in=years
            )


class ByCategoryLevel(LevelBaseListFilter):
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


class HasHtml(BooleanBaseListFilter):
    title = 'has HTML'
    parameter_name = 'html'

    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(
                Q(html__isnull=False)
                & ~Q(html='')
            )

        if self.value() == 'False':
            return queryset.filter(
                Q(html__isnull=True)
                | Q(html='')
            )


class HasVendor(BooleanBaseListFilter):
    title = 'has vendor'
    parameter_name = 'vendor'

    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(vendor__isnull=False)

        if self.value() == 'False':
            return queryset.filter(vendor__isnull=True)


class HasPremierManufacturer(BooleanBaseListFilter):
    title = 'has Premier manufacturer'
    parameter_name = 'vendor__premier_manufacturer'

    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(vendor__premier_manufacturer__isnull=False)

        if self.value() == 'False':
            return queryset.filter(vendor__premier_manufacturer__isnull=True)


class HasShopifyVendor(BooleanBaseListFilter):
    title = 'has Shopify vendor'
    parameter_name = 'vendor__shopify_vendor'

    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(vendor__shopify_vendor__isnull=False)

        if self.value() == 'False':
            return queryset.filter(vendor__shopify_vendor__isnull=True)


class HasCategoryPath(BooleanBaseListFilter):
    title = 'has category path'
    parameter_name = 'category_paths'

    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(
                Q(root_category_paths__isnull=False)
                | Q(branch_category_paths__isnull=False)
                | Q(leaf_category_paths__isnull=False)
            ).distinct()

        if self.value() == 'False':
            return queryset.filter(
                Q(root_category_paths__isnull=True)
                & Q(branch_category_paths__isnull=True)
                & Q(leaf_category_paths__isnull=True)
            ).distinct()


class HasShopifyCollection(BooleanBaseListFilter):
    title = 'has Shopify collection'
    parameter_name = 'category_paths__shopify_collection'

    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(
                (
                    Q(root_category_paths__isnull=False)
                    & Q(root_category_paths__shopify_root_collection__isnull=False)
                )
                | (
                    Q(branch_category_paths__isnull=False)
                    & Q(branch_category_paths__shopify_branch_collection__isnull=False)
                )
                | (
                    Q(leaf_category_paths__isnull=False)
                    & Q(leaf_category_paths__shopify_leaf_collection__isnull=False)
                )
            ).distinct()

        if self.value() == 'False':
            return queryset.filter(
                (
                    Q(root_category_paths__isnull=True)
                    | Q(root_category_paths__shopify_root_collection__isnull=True)
                )
                & (
                    Q(branch_category_paths__isnull=True)
                    | Q(branch_category_paths__shopify_branch_collection__isnull=True)
                )
                & (
                    Q(leaf_category_paths__isnull=True)
                    | Q(leaf_category_paths__shopify_leaf_collection__isnull=True)
                )
            ).distinct()


class HasItem(BooleanBaseListFilter):
    title = 'has item'
    parameter_name = 'item'

    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(item__isnull=False)

        if self.value() == 'False':
            return queryset.filter(item__isnull=True)


class HasPremierProduct(BooleanBaseListFilter):
    title = 'has Premier product'
    parameter_name = 'item__premier_product'

    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(item__premier_product__isnull=False)

        if self.value() == 'False':
            return queryset.filter(item__premier_product__isnull=True)


class HasShopifyProduct(BooleanBaseListFilter):
    title = 'has Shopify product'
    parameter_name = 'item__shopify_product'

    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(item__shopify_product__isnull=False)

        if self.value() == 'False':
            return queryset.filter(item__shopify_product__isnull=True)


class SemaBrandMayBeRelevant(MayBeRelevantBaseListFilter):
    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(_dataset_relevant_count__gt=0)

        if self.value() == 'False':
            return queryset.filter(_dataset_relevant_count=0)


class SemaYearMayBeRelevant(MayBeRelevantBaseListFilter):
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

        if self.value() == 'True':
            return queryset.filter(_vehicle_relevant_count__gt=0)

        if self.value() == 'False':
            return queryset.filter(_vehicle_relevant_count=0)


class SemaModelMayBeRelevant(MayBeRelevantBaseListFilter):
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

        if self.value() == 'True':
            return queryset.filter(_vehicle_relevant_count__gt=0)

        if self.value() == 'False':
            return queryset.filter(_vehicle_relevant_count=0)


class SemaSubmodelMayBeRelevant(MayBeRelevantBaseListFilter):
    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(_vehicle_relevant_count__gt=0)

        if self.value() == 'False':
            return queryset.filter(_vehicle_relevant_count=0)


class SemaMakeYearMayBeRelevant(MayBeRelevantBaseListFilter):
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

        if self.value() == 'True':
            return queryset.filter(_vehicle_relevant_count__gt=0)

        if self.value() == 'False':
            return queryset.filter(_vehicle_relevant_count=0)


class SemaBaseVehicleMayBeRelevant(MayBeRelevantBaseListFilter):
    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(_vehicle_relevant_count__gt=0)

        if self.value() == 'False':
            return queryset.filter(_vehicle_relevant_count=0)


class SemaVehicleMayBeRelevant(MayBeRelevantBaseListFilter):
    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(_engine_relevant_count__gt=0)

        if self.value() == 'False':
            return queryset.filter(_engine_relevant_count=0)


class SemaEngineMayBeRelevant(MayBeRelevantBaseListFilter):
    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(
                Q(vehicle__base_vehicle__make_year__make__is_relevant=True)
                & Q(fuel_type__exact='DIESEL')
            )

        if self.value() == 'False':
            return queryset.filter(
                Q(vehicle__base_vehicle__make_year__make__is_relevant=False)
                | ~Q(fuel_type__exact='DIESEL')
            )


class SemaCategoryMayBeRelevant(MayBeRelevantBaseListFilter):
    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset

        if self.value() == 'False':
            return queryset.none()


class SemaProductMayBeRelevant(MayBeRelevantBaseListFilter):
    def queryset(self, request, queryset):
        queryset = queryset.annotate(
            _vehicle_count=Count(
                'vehicles',
                distinct=True
            ),
            _vehicle_relevant_count=Count(
                'vehicles',
                filter=Q(vehicles__is_relevant=True),
                distinct=True
            )
        )

        if self.value() == 'True':
            return queryset.filter(
                Q(dataset__is_relevant=True)
                & (
                    Q(_vehicle_count=0)
                    | Q(_vehicle_relevant_count__gt=0)
                )
            )

        if self.value() == 'False':
            return queryset.filter(
                Q(dataset__is_relevant=False)
                | (
                    Q(_vehicle_count__gt=0)
                    & Q(_vehicle_relevant_count=0)
                )
            )
