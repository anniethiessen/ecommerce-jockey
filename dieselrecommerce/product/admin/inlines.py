from django.contrib.admin import StackedInline

from ..models import PremierProduct
from .utils import get_change_view_link


class PremierProductStackedInline(StackedInline):
    model = PremierProduct
    extra = 0
    verbose_name = 'Premier'
    verbose_name_plural = 'Premier'

    fieldsets = (
        (
            None, {
                'fields': (
                    'details_link',
                )
            }
        ),
        (
            'Premier Part Numbers', {
                'fields': (
                    'premier_part_number',
                    'vendor_part_number',
                    'upc'
                )
            }
        ),
        (
            'Premier Details', {
                'fields': (
                    'description',
                    'manufacturer',
                    'part_status'
                )
            }
        ),
        (
            'Premier Prices', {
                'fields': (
                    'msrp',
                    'map',
                    'jobber',
                    'cost'
                )
            }
        ),
        (
            'Premier Dimensions', {
                'fields': (
                    'weight',
                    'length',
                    'width',
                    'height'
                )
            }
        ),
        (
            'Premier Inventory', {
                'fields': (
                    'inventory_ab',
                    'inventory_po',
                    'inventory_ut',
                    'inventory_ky',
                    'inventory_tx',
                    'inventory_ca',
                    'inventory_wa',
                    'inventory_co'
                )
            }
        )
    )

    classes = (
        'collapse',
    )

    readonly_fields = (
        'id',
        'details_link'
    )

    def details_link(self, obj):
        return get_change_view_link(obj, 'See Premier product')
    details_link.short_description = ''
