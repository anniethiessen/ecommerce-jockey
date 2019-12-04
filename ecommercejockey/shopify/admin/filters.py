from django.db.models import Q

from core.admin.filters import (
    BooleanBaseListFilter,
    LevelBaseListFilter
)


class ByCollectionLevel(LevelBaseListFilter):
    def queryset(self, request, queryset):
        if self.value() == '1':
            return queryset.filter(
                parent_collection__isnull=True,
                child_collections__isnull=False
            ).distinct()

        if self.value() == '2':
            return queryset.filter(
                parent_collection__isnull=False,
                child_collections__isnull=False
            ).distinct()

        if self.value() == '3':
            return queryset.filter(
                parent_collection__isnull=False,
                child_collections__isnull=True
            ).distinct()


class ByTagLevel(LevelBaseListFilter):
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(name__endswith=self.value())


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


class HasSemaBrand(BooleanBaseListFilter):
    title = 'has SEMA brand'
    parameter_name = 'vendor__sema_brand'

    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(vendor__sema_brand__isnull=False)

        if self.value() == 'False':
            return queryset.filter(vendor__sema_brand__isnull=True)


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


class HasSemaCategory(BooleanBaseListFilter):
    title = 'has SEMA category'
    parameter_name = 'category_paths__sema_category'

    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(
                (
                    Q(root_category_paths__isnull=False)
                    & Q(root_category_paths__sema_root_category__isnull=False)
                )
                | (
                    Q(branch_category_paths__isnull=False)
                    & Q(branch_category_paths__sema_branch_category__isnull=False)
                )
                | (
                    Q(leaf_category_paths__isnull=False)
                    & Q(leaf_category_paths__sema_leaf_category__isnull=False)
                )
            ).distinct()

        if self.value() == 'False':
            return queryset.filter(
                (
                    Q(root_category_paths__isnull=True)
                    | Q(root_category_paths__sema_root_category__isnull=True)
                )
                & (
                    Q(branch_category_paths__isnull=True)
                    | Q(branch_category_paths__sema_branch_category__isnull=True)
                )
                & (
                    Q(leaf_category_paths__isnull=True)
                    | Q(leaf_category_paths__sema_leaf_category__isnull=True)
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
    title = 'has Premier manufacturer'
    parameter_name = 'item__premier_product'

    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(item__premier_product__isnull=False)

        if self.value() == 'False':
            return queryset.filter(item__premier_product__isnull=True)


class HasSemaProduct(BooleanBaseListFilter):
    title = 'has SEMA brand'
    parameter_name = 'item__sema_product'

    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(item__sema_product__isnull=False)

        if self.value() == 'False':
            return queryset.filter(item__sema_product__isnull=True)
