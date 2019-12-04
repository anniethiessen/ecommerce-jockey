from imagekit.admin import AdminThumbnail

from django.contrib.admin import TabularInline

from core.admin.forms import LimitedInlineFormSet
from core.admin.utils import (
    get_change_view_link,
    get_changelist_view_link
)
from ..models import PremierProduct


class PremierManufacturerProductsTabularInline(TabularInline):
    model = PremierProduct
    fk_name = 'manufacturer'
    formset = LimitedInlineFormSet
    extra = 0
    verbose_name_plural = 'products (top 10)'
    all_link_query = 'manufacturer__id__exact'
    ordering = (
        'premier_part_number',
    )
    classes = (
        'collapse',
    )

    fields = (
        'all_link',
        'detail_link',
        'premier_part_number',
        'vendor_part_number',
        'description',
        'manufacturer',
        'inventory_ab',
        'cost_cad',
        'primary_image_preview',
        'may_be_relevant_flag',
        'is_relevant',
        'relevancy_warnings',
        'relevancy_errors'
    )

    readonly_fields = (
        'relevancy_warnings',
        'relevancy_errors',
        'may_be_relevant_flag',
        'primary_image_preview',
        'all_link',
        'detail_link'
    )

    def get_rel_obj(self, obj):
        return getattr(obj, self.fk_name)

    def detail_link(self, obj):
        if not obj.pk:
            return None

        return get_change_view_link(obj, 'Details')
    detail_link.short_description = ''

    def all_link(self, obj):
        if not obj:
            return None
        query = f'{self.all_link_query}={getattr(self.get_rel_obj(obj), "pk")}'
        return get_changelist_view_link(obj._meta.model, 'See All', query)
    all_link.short_description = ''

    primary_image_preview = AdminThumbnail(
        image_field='primary_image_thumbnail'
    )
    primary_image_preview.short_description = 'primary image'

    def may_be_relevant_flag(self, obj):
        if obj.is_relevant != obj.may_be_relevant:
            return '~'
        else:
            return ''
    may_be_relevant_flag.short_description = ''

    def get_queryset(self, request):
        return super().get_queryset(request).filter(
            is_relevant=True
        ).with_admin_data()

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)

        if not request.user.is_superuser:
            readonly_fields += (
                'premier_part_number',
            )

        return readonly_fields
