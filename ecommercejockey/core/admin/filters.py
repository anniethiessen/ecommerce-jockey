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
        raise Exception('May be relevant filter must be defined')
