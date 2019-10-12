from django.contrib.admin import TabularInline

from ..models import (
    SemaCategory,
    SemaDataset
)
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


class SemaCategoryTabularInline(TabularInline):
    model = SemaCategory
    extra = 0

    fields = (
        'details_link',
        'category_id',
        'name',
        'child_category_count'
    )

    readonly_fields = (
        'details_link',
        'child_category_count'
    )

    def details_link(self, obj):
        if not obj.pk:
            return None
        return get_change_view_link(obj, 'Details')
    details_link.short_description = ''
