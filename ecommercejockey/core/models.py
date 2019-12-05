from django.db.models import (
    Model,
    BooleanField,
    CharField,
    TextField
)

from .mixins import MessagesMixin


class RelevancyBaseModel(Model, MessagesMixin):
    is_relevant = BooleanField(
        default=False
    )
    relevancy_exception = CharField(
        blank=True,
        max_length=255,
        verbose_name='exception'
    )

    @property
    def may_be_relevant(self):
        return True

    @property
    def relevancy_warnings(self):
        return ''
    relevancy_warnings.fget.short_description = 'warnings'

    @property
    def relevancy_errors(self):
        return ''
    relevancy_errors.fget.short_description = 'errors'

    class Meta:
        abstract = True


class NotesBaseModel(Model, MessagesMixin):
    notes = TextField(
        blank=True
    )

    class Meta:
        abstract = True
