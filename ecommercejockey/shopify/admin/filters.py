from django.contrib.admin.filters import SimpleListFilter
from django.db.models import Q


class ByCollectionLevel(SimpleListFilter):
    title = 'collection level'
    parameter_name = 'collection_level'

    def lookups(self, request, model_admin):
        return (
            ('1', 'Root'),
            ('2', 'Branch'),
            ('3', 'Leaf')
        )

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


class ByTagLevel(SimpleListFilter):
    title = 'tag level'
    parameter_name = 'tag_level'

    def lookups(self, request, model_admin):
        return (
            ('1', 'Root'),
            ('2', 'Branch'),
            ('3', 'Leaf')
        )

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        return queryset.filter(name__endswith=self.value())


class HasVendor(SimpleListFilter):
    title = 'has main vendor'
    parameter_name = 'vendor'

    def lookups(self, request, model_admin):
        return (
            ('Yes', 'Yes'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'Yes':
            return queryset.filter(vendor__isnull=False)
        if self.value() == 'No':
            return queryset.filter(vendor__isnull=True)


class HasPremierManufacturer(SimpleListFilter):
    title = 'has Premier manufacturer'
    parameter_name = 'vendor__premier_manufacturer'

    def lookups(self, request, model_admin):
        return (
            ('Yes', 'Yes'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'Yes':
            return queryset.filter(vendor__premier_manufacturer__isnull=False)
        if self.value() == 'No':
            return queryset.filter(vendor__premier_manufacturer__isnull=True)


class HasSemaBrand(SimpleListFilter):
    title = 'has SEMA brand'
    parameter_name = 'vendor__sema_brand'

    def lookups(self, request, model_admin):
        return (
            ('Yes', 'Yes'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'Yes':
            return queryset.filter(vendor__sema_brand__isnull=False)
        if self.value() == 'No':
            return queryset.filter(vendor__sema_brand__isnull=True)


class HasCategoryPath(SimpleListFilter):
    title = 'has main category path(s)'
    parameter_name = 'category_paths'

    def lookups(self, request, model_admin):
        return (
            ('Yes', 'Yes'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'Yes':
            return queryset.filter(
                Q(root_category_paths__isnull=False)
                | Q(branch_category_paths__isnull=False)
                | Q(leaf_category_paths__isnull=False)
            ).distinct()
        if self.value() == 'No':
            return queryset.filter(
                Q(root_category_paths__isnull=True)
                & Q(branch_category_paths__isnull=True)
                & Q(leaf_category_paths__isnull=True)
            ).distinct()


class HasSemaCategory(SimpleListFilter):
    title = 'has SEMA category'
    parameter_name = 'sema_category'

    def lookups(self, request, model_admin):
        return (
            ('Yes', 'Yes'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'Yes':
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

        if self.value() == 'No':
            return queryset.filter(
                (
                    Q(root_category_paths__isnull=True)
                    & Q(root_category_paths__sema_root_category__isnull=True)
                )
                & (
                    Q(branch_category_paths__isnull=True)
                    & Q(branch_category_paths__sema_branch_category__isnull=True)
                )
                & (
                    Q(leaf_category_paths__isnull=True)
                    & Q(leaf_category_paths__sema_leaf_category__isnull=True)
                )
            ).distinct()


class HasItem(SimpleListFilter):
    title = 'has main item'
    parameter_name = 'item'

    def lookups(self, request, model_admin):
        return (
            ('Yes', 'Yes'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'Yes':
            return queryset.filter(item__isnull=False)
        if self.value() == 'No':
            return queryset.filter(item__isnull=True)


class HasPremierProduct(SimpleListFilter):
    title = 'has Premier manufacturer'
    parameter_name = 'item__premier_product'

    def lookups(self, request, model_admin):
        return (
            ('Yes', 'Yes'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'Yes':
            return queryset.filter(item__premier_product__isnull=False)
        if self.value() == 'No':
            return queryset.filter(item__premier_product__isnull=True)


class HasSemaProduct(SimpleListFilter):
    title = 'has SEMA brand'
    parameter_name = 'vendor__sema_product'

    def lookups(self, request, model_admin):
        return (
            ('Yes', 'Yes'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'Yes':
            return queryset.filter(item__sema_product__isnull=False)
        if self.value() == 'No':
            return queryset.filter(item__sema_product__isnull=True)
