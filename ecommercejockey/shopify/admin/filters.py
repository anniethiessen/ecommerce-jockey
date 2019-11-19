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
