from django.contrib.admin import SimpleListFilter
from django.db.models import Q


class HasMissingInventory(SimpleListFilter):
    title = 'needs inventory update'
    parameter_name = 'missing_inventory'

    def lookups(self, request, model_admin):
        return (
            ('Yes', 'Yes'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'Yes':
            return queryset.filter(
                Q(inventory_ab__isnull=True)
                | Q(inventory_po__isnull=True)
                | Q(inventory_ut__isnull=True)
                | Q(inventory_ky__isnull=True)
                | Q(inventory_tx__isnull=True)
                | Q(inventory_ca__isnull=True)
                | Q(inventory_wa__isnull=True)
                | Q(inventory_co__isnull=True)
            )
        if self.value() == 'No':
            return queryset.filter(
                inventory_ab__isnull=False,
                inventory_po__isnull=False,
                inventory_ut__isnull=False,
                inventory_ky__isnull=False,
                inventory_tx__isnull=False,
                inventory_ca__isnull=False,
                inventory_wa__isnull=False,
                inventory_co__isnull=False
            )


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
