from django.contrib.admin import TabularInline

from ..models import SemaDataset
from .utils import get_change_view_link


class SemaDatasetTabularInline(TabularInline):
    model = SemaDataset
    extra = 0

    fields = (
        'details_link',
        'dataset_id',
        'name',
        'is_authorized'
    )

    readonly_fields = (
        'details_link',
    )

    def details_link(self, obj):
        if not obj.pk:
            return None
        return get_change_view_link(obj, 'Details')
    details_link.short_description = ''
