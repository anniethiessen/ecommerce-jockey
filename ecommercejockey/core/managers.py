from django.db.models import (
    QuerySet,
    Manager
)


class RelevancyBaseQuerySet(QuerySet):
    pass


class RelevancyBaseManager(Manager):
    def get_queryset(self):
        return RelevancyBaseQuerySet(
            self.model,
            using=self._db
        )
