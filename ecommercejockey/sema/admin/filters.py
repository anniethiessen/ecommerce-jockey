from django.contrib.admin import SimpleListFilter
from django.db.models import Q


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


class ByDecade(SimpleListFilter):
    title = 'decade'
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
        if self.value():
            return queryset.with_year_data().filter(decade=int(self.value()))


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


class HasProduct(SimpleListFilter):
    title = 'has full product'
    parameter_name = 'product'

    def lookups(self, request, model_admin):
        return (
            ('Yes', 'Yes'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'Yes':
            return queryset.filter(product__isnull=False)
        if self.value() == 'No':
            return queryset.filter(product__isnull=True)
