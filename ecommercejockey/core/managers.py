from django.db.models import (
    QuerySet,
    Manager,
    Case,
    When,
    Q,
    BooleanField,
    CharField,
    Value
)


class RelevancyBaseQuerySet(QuerySet):
    def _get_may_be_relevant_query(self):
        return Q()

    def _get_relevancy_errors_flag_query(self):
        return Q()

    def with_relevancy_values(self):
        relevancy_query = self._get_may_be_relevant_query()
        errors_query = self._get_relevancy_errors_flag_query()

        return self.annotate(
            _may_be_relevant=Case(
                When(
                    relevancy_query,
                    then=True
                ),
                default=False,
                output_field=BooleanField()
            ),
            _relevancy_errors_flag=Case(
                When(
                    errors_query,
                    then=Value('!')
                ),
                default=Value(''),
                output_field=CharField()
            )
        )


class RelevancyBaseManager(Manager):
    def get_queryset(self):
        return RelevancyBaseQuerySet(
            self.model,
            using=self._db
        )

    def with_relevancy_values(self):
        return self.get_queryset().with_relevancy_values()
