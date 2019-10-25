from django.contrib.admin.filters import SimpleListFilter


class MayBeRelevantFilter(SimpleListFilter):
    title = 'may be relevant'
    parameter_name = 'may_be_relevant'

    def lookups(self, request, model_admin):
        return (
            ('Yes', 'Yes'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        queryset = queryset.with_relevancy_values()
        if self.value() == 'Yes':
            return queryset.filter(_may_be_relevant=True)
        if self.value() == 'No':
            return queryset.filter(_may_be_relevant=False)
