from django.forms import BaseInlineFormSet

from core.admin.site import INLINE_LIMIT


class LimitedManyToManyDatasetInlineFormSet(BaseInlineFormSet):
    def get_queryset(self):
        return super().get_queryset().order_by(
            '-semadataset__is_relevant'
        ).distinct()[:INLINE_LIMIT]


class LimitedManyToManyVehicleInlineFormSet(BaseInlineFormSet):
    def get_queryset(self):
        return super().get_queryset().order_by(
            '-semavehicle__is_relevant'
        ).distinct()[:INLINE_LIMIT]


class LimitedManyToManyCategoryInlineFormSet(BaseInlineFormSet):
    def get_queryset(self):
        return super().get_queryset().order_by(
            '-semacategory__is_relevant'
        ).distinct()[:INLINE_LIMIT]


class LimitedManyToManyParentCategoryInlineFormSet(BaseInlineFormSet):
    def get_queryset(self):
        return super().get_queryset().order_by(
            '-to_semacategory__is_relevant'
        ).distinct()[:INLINE_LIMIT]


class LimitedManyToManyChildCategoryInlineFormSet(BaseInlineFormSet):
    def get_queryset(self):
        return super().get_queryset().order_by(
            '-from_semacategory__is_relevant'
        ).distinct()[:INLINE_LIMIT]


class LimitedManyToManyProductInlineFormSet(BaseInlineFormSet):
    def get_queryset(self):
        return super().get_queryset().order_by(
            '-semaproduct__is_relevant'
        ).distinct()[:INLINE_LIMIT]
