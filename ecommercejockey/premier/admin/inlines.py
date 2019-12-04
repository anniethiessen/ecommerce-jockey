from imagekit.admin import AdminThumbnail

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
        'detail_link',
        'premier_part_number',
        'vendor_part_number',
        'description',
        'manufacturer',
        'cost',
        'jobber',
        'msrp',
        'map',
        'is_relevant',
        'primary_image_preview'
    )

    readonly_fields = (
        'primary_image_preview',
        'detail_link'
    )

    def detail_link(self, obj):
        if not obj.pk:
            return None
        return get_change_view_link(obj, 'Details')
    detail_link.short_description = ''

    primary_image_preview = AdminThumbnail(
        image_field='primary_image_thumbnail'
    )
    primary_image_preview.short_description = 'primary image'
