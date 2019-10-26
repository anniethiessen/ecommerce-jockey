from django.db.models import (
    Model,
    BooleanField
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
    def relevancy_errors(self):
        raise Exception("Relevancy errors must be defined")
    relevancy_errors.fget.short_description = 'Errors'

    class Meta:
        abstract = True
