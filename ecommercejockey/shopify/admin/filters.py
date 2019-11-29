from django.contrib.admin.filters import SimpleListFilter


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
