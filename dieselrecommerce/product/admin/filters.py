from django.contrib.admin import SimpleListFilter
from django.db.models import Q


class HasMissingInventory(SimpleListFilter):
    title = 'has missing inventory'
    parameter_name = 'missing_inventory'

    def lookups(self, request, model_admin):
        return (
            ('Yes', 'Yes'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'Yes':
            return queryset.has_missing_inventory()
        if self.value() == 'No':
            return queryset.has_all_inventory()


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


class HasMissingPricing(SimpleListFilter):
    title = 'has missing pricing'
    parameter_name = 'missing_pricing'

    def lookups(self, request, model_admin):
        return (
            ('Yes', 'Yes'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'Yes':
            return queryset.has_missing_pricing()
        if self.value() == 'No':
            return queryset.has_all_pricing()


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


class HasPremierProduct(SimpleListFilter):
    title = 'has Premier product'
    parameter_name = 'premier_product'

    def lookups(self, request, model_admin):
        return (
            ('Yes', 'Yes'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'Yes':
            return queryset.filter(premier_product__isnull=False)
        if self.value() == 'No':
            return queryset.filter(premier_product__isnull=True)


class HasSemaProduct(SimpleListFilter):
    title = 'has SEMA product'
    parameter_name = 'sema_product'

    def lookups(self, request, model_admin):
        return (
            ('Yes', 'Yes'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'Yes':
            return queryset.filter(sema_product__isnull=False)
        if self.value() == 'No':
            return queryset.filter(sema_product__isnull=True)
