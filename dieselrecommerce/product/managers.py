from math import floor

from django.db.models import Manager, QuerySet

from .utils import chunkify_list


class PremierProductQuerySet(QuerySet):
    def update_inventory_from_premier_api(self, token=None):
        msgs = []
        invalid = self.filter(premier_part_number__isnull=True)
        for obj in invalid:
            msgs.append(
                obj.get_inventory_update_error_msg(
                    "Premier Part Number required"
                )
            )

        queryset = self.filter(premier_part_number__isnull=False)
        part_numbers = [obj.premier_part_number for obj in queryset]

        chunks = chunkify_list(part_numbers)
        for chunk in chunks:
            try:
                if not token:
                    token = self.model.retrieve_premier_api_token()
                response = self.model.retrieve_premier_api_inventory(
                    chunk, token)
                for items in response:
                    instance = queryset.get(
                        premier_part_number=items['itemNumber'])
                    data = items['inventory']
                    msgs.append(instance.update_inventory_from_data(data))
            except Exception as err:
                msgs.append(f'Chunk Error: {chunk}, {err}')
                continue
        return msgs


class PremierProductManager(Manager):
    def get_queryset(self):
        return PremierProductQuerySet(
            self.model,
            using=self._db
        )

    def update_inventory_from_premier_api(self, token=None):
        return self.get_queryset().update_inventory_from_premier_api(token)
