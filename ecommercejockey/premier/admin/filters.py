from django.contrib.admin import SimpleListFilter
from django.db.models import Q


class HasApiInventory(SimpleListFilter):
    title = 'has API inventory'
    parameter_name = 'inventory'

    def lookups(self, request, model_admin):
        return (
            ('Yes', 'Yes'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'Yes':
            return queryset.has_all_inventory_data()
        if self.value() == 'No':
            return queryset.has_missing_inventory_data()


class HasAlbertaInventory(SimpleListFilter):
    title = 'has inventory in Alberta'
    parameter_name = 'inventory_ab'

    def lookups(self, request, model_admin):
        return (
            ('Yes', 'Yes'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'Yes':
            return queryset.filter(
                Q(inventory_ab__isnull=False)
                & Q(inventory_ab__gt=0)
            )
        if self.value() == 'No':
            return queryset.filter(
                Q(inventory_ab__isnull=True)
                | Q(inventory_ab=0)
            )


class HasApiPricing(SimpleListFilter):
    title = 'has API pricing'
    parameter_name = 'pricing'

    def lookups(self, request, model_admin):
        return (
            ('Yes', 'Yes'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'Yes':
            return queryset.has_all_pricing_data()
        if self.value() == 'No':
            return queryset.has_missing_pricing_data()


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
