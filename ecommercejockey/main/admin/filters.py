from django.db.models import Q

from core.admin.filters import (
    BooleanBaseListFilter,
    MayBeRelevantBaseListFilter
)


class IsCompleteBaseListFilter(BooleanBaseListFilter):
    title = 'is complete'
    parameter_name = 'is_complete'


class ItemIsComplete(IsCompleteBaseListFilter):
    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(
                premier_product__isnull=False,
                sema_product__isnull=False,
                shopify_product__isnull=False
            )

        if self.value() == 'False':
            return queryset.filter(
                Q(premier_product__isnull=True)
                | Q(sema_product__isnull=True)
                | Q(shopify_product__isnull=True)
            )


class VendorIsComplete(IsCompleteBaseListFilter):
    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(
                premier_manufacturer__isnull=False,
                sema_brand__isnull=False,
                shopify_vendor__isnull=False
            )

        if self.value() == 'False':
            return queryset.filter(
                Q(premier_manufacturer__isnull=True)
                | Q(sema_brand__isnull=True)
                | Q(shopify_vendor__isnull=True)
            )


class CategoryPathIsComplete(IsCompleteBaseListFilter):
    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(
                sema_root_category__isnull=False,
                sema_branch_category__isnull=False,
                sema_leaf_category__isnull=False,
                shopify_root_collection__isnull=False,
                shopify_branch_collection__isnull=False,
                shopify_leaf_collection__isnull=False
            )

        if self.value() == 'False':
            return queryset.filter(
                Q(sema_root_category__isnull=True)
                | Q(sema_branch_category__isnull=True)
                | Q(sema_leaf_category__isnull=True)
                | Q(shopify_root_collection__isnull=True)
                | Q(shopify_branch_collection__isnull=True)
                | Q(shopify_leaf_collection__isnull=True)
            )


class HasPremierProduct(BooleanBaseListFilter):
    title = 'has Premier product'
    parameter_name = 'premier_product'

    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(premier_product__isnull=False)

        if self.value() == 'False':
            return queryset.filter(premier_product__isnull=True)


class HasSemaProduct(BooleanBaseListFilter):
    title = 'has SEMA product'
    parameter_name = 'sema_product'

    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(sema_product__isnull=False)

        if self.value() == 'False':
            return queryset.filter(sema_product__isnull=True)


class HasShopifyProduct(BooleanBaseListFilter):
    title = 'has Shopify product'
    parameter_name = 'shopify_product'

    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(shopify_product__isnull=False)

        if self.value() == 'False':
            return queryset.filter(shopify_product__isnull=True)


class HasPremierManufacturer(BooleanBaseListFilter):
    title = 'has Premier manufacturer'
    parameter_name = 'premier_manufacturer'

    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(premier_manufacturer__isnull=False)

        if self.value() == 'False':
            return queryset.filter(premier_manufacturer__isnull=True)


class HasSemaBrand(BooleanBaseListFilter):
    title = 'has SEMA brand'
    parameter_name = 'sema_brand'

    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(sema_brand__isnull=False)

        if self.value() == 'False':
            return queryset.filter(sema_brand__isnull=True)


class HasShopifyVendor(BooleanBaseListFilter):
    title = 'has Shopify vendor'
    parameter_name = 'shopify_vendor'

    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(shopify_vendor__isnull=False)

        if self.value() == 'False':
            return queryset.filter(shopify_vendor__isnull=True)


class HasSemaRootCategory(BooleanBaseListFilter):
    title = 'has Sema root category'
    parameter_name = 'sema_root_category'

    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(sema_root_category__isnull=False)

        if self.value() == 'False':
            return queryset.filter(sema_root_category__isnull=True)


class HasSemaBranchCategory(BooleanBaseListFilter):
    title = 'has Sema branch category'
    parameter_name = 'sema_branch_category'

    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(sema_branch_category__isnull=False)

        if self.value() == 'False':
            return queryset.filter(sema_branch_category__isnull=True)


class HasSemaLeafCategory(BooleanBaseListFilter):
    title = 'has Sema leaf category'
    parameter_name = 'sema_leaf_category'

    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(sema_leaf_category__isnull=False)

        if self.value() == 'False':
            return queryset.filter(sema_leaf_category__isnull=True)


class HasShopifyRootCollection(BooleanBaseListFilter):
    title = 'has Shopify root collection'
    parameter_name = 'shopify_root_collection'

    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(shopify_root_collection__isnull=False)

        if self.value() == 'False':
            return queryset.filter(shopify_root_collection__isnull=True)


class HasShopifyBranchCollection(BooleanBaseListFilter):
    title = 'has Shopify branch collection'
    parameter_name = 'shopify_branch_collection'

    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(shopify_branch_collection__isnull=False)

        if self.value() == 'False':
            return queryset.filter(shopify_branch_collection__isnull=True)


class HasShopifyLeafCollection(BooleanBaseListFilter):
    title = 'has Shopify leaf collection'
    parameter_name = 'shopify_leaf_collection'

    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(shopify_leaf_collection__isnull=False)

        if self.value() == 'False':
            return queryset.filter(shopify_leaf_collection__isnull=True)


class ItemMayBeRelevant(MayBeRelevantBaseListFilter):
    def lookups(self, request, model_admin):
        return (
            ('True', 'Yes'),
            ('Partial', 'Partial'),
            ('False', 'No')
        )

    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(
                premier_product__isnull=False,
                premier_product__is_relevant=True,
                sema_product__isnull=False,
                sema_product__is_relevant=True
            )

        if self.value() == 'Partial':
            return queryset.filter(
                (
                    Q(premier_product__isnull=False)
                    & Q(premier_product__is_relevant=True)
                    & (
                        Q(sema_product__isnull=True)
                        | (
                            Q(sema_product__isnull=False)
                            & Q(sema_product__is_relevant=False)
                        )
                    )
                )
                | (
                    Q(sema_product__isnull=False)
                    & Q(sema_product__is_relevant=True)
                    & (
                        Q(premier_product__isnull=True)
                        | (
                            Q(premier_product__isnull=False)
                            & Q(premier_product__is_relevant=False)
                        )
                    )
                )
            )

        if self.value() == 'False':
            return queryset.filter(
                (
                    Q(premier_product__isnull=True)
                    | (
                        Q(premier_product__isnull=False)
                        & Q(premier_product__is_relevant=False)
                    )
                )
                & (
                    Q(sema_product__isnull=True)
                    | (
                        Q(sema_product__isnull=False)
                        & Q(sema_product__is_relevant=False)
                    )
                )
            )


class VendorMayBeRelevant(MayBeRelevantBaseListFilter):
    def lookups(self, request, model_admin):
        return (
            ('True', 'Yes'),
            ('Partial', 'Partial'),
            ('False', 'No')
        )

    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(
                premier_manufacturer__isnull=False,
                premier_manufacturer__is_relevant=True,
                sema_brand__isnull=False,
                sema_brand__is_relevant=True
            )

        if self.value() == 'Partial':
            return queryset.filter(
                (
                    Q(premier_manufacturer__isnull=False)
                    & Q(premier_manufacturer__is_relevant=True)
                    & (
                        Q(sema_brand__isnull=True)
                        | (
                            Q(sema_brand__isnull=False)
                            & Q(sema_brand__is_relevant=False)
                        )
                    )
                )
                | (
                    Q(sema_brand__isnull=False)
                    & Q(sema_brand__is_relevant=True)
                    & (
                        Q(premier_manufacturer__isnull=True)
                        | (
                            Q(premier_manufacturer__isnull=False)
                            & Q(premier_manufacturer__is_relevant=False)
                        )
                    )
                )
            )

        if self.value() == 'False':
            return queryset.filter(
                (
                    Q(premier_manufacturer__isnull=True)
                    | (
                        Q(premier_manufacturer__isnull=False)
                        & Q(premier_manufacturer__is_relevant=False)
                    )
                )
                & (
                    Q(sema_brand__isnull=True)
                    | (
                        Q(sema_brand__isnull=False)
                        & Q(sema_brand__is_relevant=False)
                    )
                )
            )


class CategoryPathMayBeRelevant(MayBeRelevantBaseListFilter):
    def lookups(self, request, model_admin):
        return (
            ('True', 'Yes'),
            ('Partial', 'Partial'),
            ('False', 'No')
        )

    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(
                sema_root_category__isnull=False,
                sema_root_category__is_relevant=True,
                sema_branch_category__isnull=False,
                sema_branch_category__is_relevant=True,
                sema_leaf_category__isnull=False,
                sema_leaf_category__is_relevant=True
            )

        if self.value() == 'Partial':
            return queryset.filter(
                (
                    Q(sema_root_category__isnull=False)
                    & Q(sema_root_category__is_relevant=True)
                    & (
                        (
                            Q(sema_branch_category__isnull=True)
                            | (
                                Q(sema_branch_category__isnull=False)
                                & Q(sema_branch_category__is_relevant=False)
                            )
                        )
                        | (
                            Q(sema_leaf_category__isnull=True)
                            | (
                                Q(sema_leaf_category__isnull=False)
                                & Q(sema_leaf_category__is_relevant=False)
                            )
                        )
                    )
                )
                | (
                    Q(sema_branch_category__isnull=False)
                    & Q(sema_branch_category__is_relevant=True)
                    & (
                        (
                            Q(sema_root_category__isnull=True)
                            | (
                                Q(sema_root_category__isnull=False)
                                & Q(sema_root_category__is_relevant=False)
                            )
                        )
                        | (
                            Q(sema_leaf_category__isnull=True)
                            | (
                                Q(sema_leaf_category__isnull=False)
                                & Q(sema_leaf_category__is_relevant=False)
                            )
                        )
                    )
                )
                | (
                    Q(sema_leaf_category__isnull=False)
                    & Q(sema_leaf_category__is_relevant=True)
                    & (
                        (
                            Q(sema_root_category__isnull=True)
                            | (
                                Q(sema_root_category__isnull=False)
                                & Q(sema_root_category__is_relevant=False)
                            )
                        )
                        | (
                            Q(sema_branch_category__isnull=True)
                            | (
                                Q(sema_branch_category__isnull=False)
                                & Q(sema_branch_category__is_relevant=False)
                            )
                        )
                    )
                )
            )

        if self.value() == 'False':
            return queryset.filter(
                (
                    Q(sema_root_category__isnull=True)
                    | (
                        Q(sema_root_category__isnull=False)
                        & Q(sema_root_category__is_relevant=False)
                    )
                )
                & (
                    Q(sema_branch_category__isnull=True)
                    | (
                        Q(sema_branch_category__isnull=False)
                        & Q(sema_branch_category__is_relevant=False)
                    )
                )
                & (
                    Q(sema_leaf_category__isnull=True)
                    | (
                        Q(sema_leaf_category__isnull=False)
                        & Q(sema_leaf_category__is_relevant=False)
                    )
                )
            )
