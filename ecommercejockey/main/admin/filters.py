from django.contrib.admin import SimpleListFilter


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
