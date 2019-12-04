from django.contrib.admin import SimpleListFilter
from django.db.models import Q

from core.admin.filters import (
    BooleanBaseListFilter,
    MayBeRelevantBaseListFilter,
)


class HasApiInventory(BooleanBaseListFilter):
    title = 'has API inventory'
    parameter_name = 'inventory'

    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.has_all_inventory_data()

        if self.value() == 'False':
            return queryset.has_missing_inventory_data()


class HasAlbertaInventory(BooleanBaseListFilter):
    title = 'has inventory in Alberta'
    parameter_name = 'inventory_ab'

    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(
                Q(inventory_ab__isnull=False)
                & Q(inventory_ab__gt=0)
            )

        if self.value() == 'False':
            return queryset.filter(
                Q(inventory_ab__isnull=True)
                | Q(inventory_ab=0)
            )


class HasApiPricing(BooleanBaseListFilter):
    title = 'has API pricing'
    parameter_name = 'pricing'

    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.has_all_pricing_data()

        if self.value() == 'False':
            return queryset.has_missing_pricing_data()


class HasVendor(BooleanBaseListFilter):
    title = 'has vendor'
    parameter_name = 'vendor'

    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(vendor__isnull=False)

        if self.value() == 'False':
            return queryset.filter(vendor__isnull=True)


class HasSemaBrand(BooleanBaseListFilter):
    title = 'has SEMA brand'
    parameter_name = 'vendor__sema_brand'

    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(vendor__sema_brand__isnull=False)

        if self.value() == 'False':
            return queryset.filter(vendor__sema_brand__isnull=True)


class HasShopifyVendor(BooleanBaseListFilter):
    title = 'has Shopify vendor'
    parameter_name = 'vendor__shopify_vendor'

    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(vendor__shopify_vendor__isnull=False)

        if self.value() == 'False':
            return queryset.filter(vendor__shopify_vendor__isnull=True)


class HasItem(BooleanBaseListFilter):
    title = 'has item'
    parameter_name = 'item'

    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(item__isnull=False)

        if self.value() == 'False':
            return queryset.filter(item__isnull=True)


class HasSemaProduct(BooleanBaseListFilter):
    title = 'has SEMA product'
    parameter_name = 'item__sema_product'

    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(item__sema_product__isnull=False)

        if self.value() == 'False':
            return queryset.filter(item__sema_product__isnull=True)


class HasShopifyProduct(BooleanBaseListFilter):
    title = 'has Shopify product'
    parameter_name = 'item__shopify_product'

    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(item__shopify_product__isnull=False)

        if self.value() == 'False':
            return queryset.filter(item__shopify_product__isnull=True)


class HasPrimaryImage(BooleanBaseListFilter):
    title = 'has primary image'
    parameter_name = 'primary_image'

    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(
                Q(primary_image__isnull=False)
                & ~Q(primary_image__exact='')
            )

        if self.value() == 'False':
            return queryset.filter(
                Q(primary_image__isnull=True)
                | Q(primary_image__exact='')
            )


class PremierProductMayBeRelevant(MayBeRelevantBaseListFilter):
    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(
                Q(manufacturer__is_relevant=True)
                & Q(inventory_ab__gt=0)
            )

        if self.value() == 'False':
            return queryset.filter(
                Q(manufacturer__is_relevant=False)
                | Q(inventory_ab__lte=0)
            )
