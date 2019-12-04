from django.contrib.admin.filters import SimpleListFilter


class BooleanBaseListFilter(SimpleListFilter):
    def lookups(self, request, model_admin):
        return (
            ('True', 'Yes'),
            ('False', 'No')
        )

    def queryset(self, request, queryset):
        raise Exception("Filter must be defined")


class LevelBaseListFilter(SimpleListFilter):
    title = 'level'
    parameter_name = 'level'

    def lookups(self, request, model_admin):
        return (
            ('1', 'Root'),
            ('2', 'Branch'),
            ('3', 'Leaf')
        )

    def queryset(self, request, queryset):
        raise Exception("Filter must be defined")


class MayBeRelevantBaseListFilter(BooleanBaseListFilter):
    title = 'may be relevant'
    parameter_name = 'may_be_relevant'
