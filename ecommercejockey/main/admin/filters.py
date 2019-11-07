from django.contrib.admin import SimpleListFilter
from django.db.models import Q


class IsCompleteItem(SimpleListFilter):  # TODO add product checks
    title = 'is complete'
    parameter_name = 'is_complete'

    def lookups(self, request, model_admin):
        return (
            ('Yes', 'Yes'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'Yes':
            return queryset.filter(
                premier_product__isnull=False,
                sema_product__isnull=False,
                shopify_product__isnull=False
            )
        if self.value() == 'No':
            return queryset.filter(
                Q(premier_product__isnull=True)
                | Q(sema_product__isnull=True)
                | Q(shopify_product__isnull=True)
            )


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


class HasShopifyProduct(SimpleListFilter):
    title = 'has Shopify product'
    parameter_name = 'shopify_product'

    def lookups(self, request, model_admin):
        return (
            ('Yes', 'Yes'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'Yes':
            return queryset.filter(shopify_product__isnull=False)
        if self.value() == 'No':
            return queryset.filter(shopify_product__isnull=True)
