from django.db.models import (
    Model,
    BooleanField
)

from .managers import RelevancyBaseManager
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
        return ''

    objects = RelevancyBaseManager()

    class Meta:
        abstract = True
