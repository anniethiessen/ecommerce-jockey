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


class SemaCategoryParentsTabularInline(TabularInline):
    model = SemaCategory.parent_categories.through
    fk_name = 'from_semacategory'
    extra = 0
    verbose_name_plural = 'Parent Categories'

    fields = (
        'details_link',
        'category_id_a',
        'category_name_a',
        'parent_category_count_a',
        'child_category_count_a'
    )

    readonly_fields = (
        'details_link',
        'category_id_a',
        'category_name_a',
        'parent_category_count_a',
        'child_category_count_a'
    )

    def details_link(self, obj):
        if not obj.pk:
            return None
        return get_change_view_link(obj.to_semacategory, 'Details')
    details_link.short_description = ''

    def category_id_a(self, obj):
        if not obj.pk:
            return None
        return obj.to_semacategory.category_id
    category_id_a.short_description = 'Category ID'

    def category_name_a(self, obj):
        if not obj.pk:
            return None
        return obj.to_semacategory.name
    category_name_a.short_description = 'Name'

    def parent_category_count_a(self, obj):
        return obj.to_semacategory.parent_categories.all().count()
    parent_category_count_a.short_description = 'Parent count'

    def child_category_count_a(self, obj):
        return obj.to_semacategory.child_categories.all().count()
    child_category_count_a.short_description = 'Child count'


class SemaCategoryChildrenTabularInline(TabularInline):
    model = SemaCategory.parent_categories.through
    fk_name = 'to_semacategory'
    extra = 0
    verbose_name_plural = 'Child Categories'

    fields = (
        'details_link',
        'category_id_a',
        'category_name_a',
        'parent_category_count_a',
        'child_category_count_a'
    )

    readonly_fields = (
        'details_link',
        'category_id_a',
        'category_name_a',
        'parent_category_count_a',
        'child_category_count_a'
    )

    def details_link(self, obj):
        if not obj.pk:
            return None
        return get_change_view_link(obj.from_semacategory, 'Details')
    details_link.short_description = ''

    def category_id_a(self, obj):
        if not obj.pk:
            return None
        return obj.from_semacategory.category_id
    category_id_a.short_description = 'Category ID'

    def category_name_a(self, obj):
        if not obj.pk:
            return None
        return obj.from_semacategory.name
    category_name_a.short_description = 'Name'

    def parent_category_count_a(self, obj):
        return obj.from_semacategory.parent_categories.all().count()
    parent_category_count_a.short_description = 'Parent count'

    def child_category_count_a(self, obj):
        return obj.from_semacategory.child_categories.all().count()
    child_category_count_a.short_description = 'Child count'
