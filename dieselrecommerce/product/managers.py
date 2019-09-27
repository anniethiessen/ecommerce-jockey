from django.db.models import Manager, QuerySet, Q

from .utils import chunkify_list


class PremierProductQuerySet(QuerySet):
    def has_missing_inventory(self):
        return self.filter(
            Q(inventory_ab__isnull=True)
            | Q(inventory_po__isnull=True)
            | Q(inventory_ut__isnull=True)
            | Q(inventory_ky__isnull=True)
            | Q(inventory_tx__isnull=True)
            | Q(inventory_ca__isnull=True)
            | Q(inventory_wa__isnull=True)
            | Q(inventory_co__isnull=True)
        )

    def has_all_inventory(self):
        return self.filter(
            inventory_ab__isnull=False,
            inventory_po__isnull=False,
            inventory_ut__isnull=False,
            inventory_ky__isnull=False,
            inventory_tx__isnull=False,
            inventory_ca__isnull=False,
            inventory_wa__isnull=False,
            inventory_co__isnull=False
        )

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

        chunks = chunkify_list(part_numbers, chunk_size=50)
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

    def has_all_inventory(self):
        return self.get_queryset().has_all_inventory()

    def has_missing_inventory(self):
        return self.get_queryset().has_missing_inventory()

    def update_inventory_from_premier_api(self, token=None):
        return self.get_queryset().update_inventory_from_premier_api(token)
