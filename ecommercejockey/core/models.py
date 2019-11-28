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

    @property
    def may_be_relevant(self):
        raise Exception("May be relevant must be defined")

    @property
    def relevancy_warnings(self):
        return ''
    relevancy_warnings.fget.short_description = 'Warnings'

    @property
    def relevancy_errors(self):
        return ''
    relevancy_errors.fget.short_description = 'Errors'

    class Meta:
        abstract = True


class NotesBaseModel(Model, MessagesMixin):
    notes = TextField(
        blank=True
    )

    class Meta:
        abstract = True
