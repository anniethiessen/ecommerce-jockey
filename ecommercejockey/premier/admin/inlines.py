from django.contrib.admin import TabularInline

from core.admin.utils import get_change_view_link
from ..models import PremierProduct


class PremierProductTabularInline(TabularInline):
    model = PremierProduct
    extra = 0
    verbose_name = 'product'
    verbose_name_plural = 'products'
    ordering = (
        'premier_part_number',
    )

    fields = (
        'details_link',
        'premier_part_number',
        'vendor_part_number',
        'description',
        'manufacturer',
        'cost',
        'jobber',
        'msrp',
        'map',
        'is_relevant'
    )

    readonly_fields = (
        'details_link',
    )

    def details_link(self, obj):
        if not obj.pk:
            return None
        return get_change_view_link(obj, 'Details')
    details_link.short_description = ''
