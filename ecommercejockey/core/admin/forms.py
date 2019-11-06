from django.forms import BaseInlineFormSet

from .site import INLINE_LIMIT


class LimitedInlineFormSet(BaseInlineFormSet):
    def get_queryset(self):
        return super().get_queryset().order_by(
            '-is_relevant'
        ).distinct()[:INLINE_LIMIT]
