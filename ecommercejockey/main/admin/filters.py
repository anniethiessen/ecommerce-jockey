from django.contrib.admin import SimpleListFilter
from django.db.models import Q

from core.admin.filters import MayBeRelevantBaseListFilter


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


class CategoryPathMayBeRelevant(MayBeRelevantBaseListFilter):
    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(
                sema_root_category__is_relevant=True,
                sema_branch_category__is_relevant=True,
                sema_leaf_category__is_relevant=True,
            )
        if self.value() == 'False':
            return queryset.filter(
                Q(sema_root_category__is_relevant=False)
                | Q(sema_branch_category__is_relevant=False)
                | Q(sema_leaf_category__is_relevant=False)
            )
