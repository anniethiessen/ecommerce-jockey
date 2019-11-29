from django.forms import BaseInlineFormSet

from core.admin.site import INLINE_LIMIT


class LimitedInlineFormSet(BaseInlineFormSet):
    def get_queryset(self):
        return super().get_queryset().distinct()[:INLINE_LIMIT]
