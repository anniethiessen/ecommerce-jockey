from django.db.models import Manager, QuerySet, Q

from .apis import premier_api
from core.utils import chunkify_list


class PremierProductQuerySet(QuerySet):
    def has_missing_inventory_data(self):
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

    def has_all_inventory_data(self):
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

    def has_missing_pricing_data(self):
        return self.filter(
            Q(cost_cad__isnull=True)
            | Q(cost_usd__isnull=True)
            | Q(jobber_cad__isnull=True)
            | Q(jobber_usd__isnull=True)
            | Q(msrp_cad__isnull=True)
            | Q(msrp_usd__isnull=True)
            | Q(map_cad__isnull=True)
            | Q(map_usd__isnull=True)
        )

    def has_all_pricing_data(self):
        return self.filter(
            cost_cad__isnull=False,
            cost_usd__isnull=False,
            jobber_cad__isnull=False,
            jobber_usd__isnull=False,
            msrp_cad__isnull=False,
            msrp_usd__isnull=False,
            map_cad__isnull=False,
            map_usd__isnull=False
        )

    def update_inventory_from_api(self):
        msgs = []

        invalid = self.filter(premier_part_number__isnull=True)
        for obj in invalid:
            msgs.append(
                obj.get_instance_error_msg("Premier Part Number required")
            )

        queryset = self.filter(premier_part_number__isnull=False)
        part_numbers = [obj.premier_part_number for obj in queryset]

        chunks = chunkify_list(part_numbers, chunk_size=50)
        for chunk in chunks:
            try:
                response = self.model.objects.get_api_inventory_data(chunk)
                for items in response:
                    obj = queryset.get(premier_part_number=items['itemNumber'])
                    data = items['inventory']
                    update_fields = obj.parse_api_inventory_data(data)
                    msgs.append(
                        obj.update_inventory_from_api_data(**update_fields)
                    )
            except Exception as err:
                msgs.append(f'Chunk Error: {chunk}, {err}')
                continue
        return msgs

    def update_pricing_from_api(self):
        msgs = []

        invalid = self.filter(premier_part_number__isnull=True)
        for obj in invalid:
            msgs.append(
                obj.get_instance_error_msg("Premier Part Number required")
            )

        queryset = self.filter(premier_part_number__isnull=False)
        part_numbers = [obj.premier_part_number for obj in queryset]

        chunks = chunkify_list(part_numbers, chunk_size=50)
        for chunk in chunks:
            try:
                response = self.model.objects.get_api_inventory_data(chunk)
                for items in response:
                    obj = queryset.get(premier_part_number=items['itemNumber'])
                    data = items['pricing']
                    update_fields = obj.parse_api_pricing_data(data)
                    msgs.append(
                        obj.update_pricing_from_api_data(**update_fields)
                    )
            except Exception as err:
                msgs.append(f'Chunk Error: {chunk}, {err}')
                continue
        return msgs


class PremierProductManager(Manager):
    @staticmethod
    def get_api_inventory_data(part_numbers):
        try:
            return premier_api.retrieve_product_inventory(part_numbers)
        except Exception:
            raise

    @staticmethod
    def get_api_pricing_data(part_numbers):
        try:
            return premier_api.retrieve_product_pricing(part_numbers)
        except Exception:
            raise

    @staticmethod
    def parse_api_inventory_data(data):
        try:
            update_fields = {}
            for item in data:
                field = f'inventory_{item["warehouseCode"][:2].lower()}'
                update_fields[field] = int(item['quantityAvailable'])
            return update_fields
        except Exception:
            raise

    @staticmethod
    def parse_api_pricing_data(data):
        try:
            update_fields = {}
            for item in data:
                currency = item.pop('currency')
                item['msrp'] = item.pop('retail')
                for key, value in item.items():
                    field = f'{key.lower()}_{currency.lower()}'
                    update_fields[field] = value
            return update_fields
        except Exception:
            raise

    def get_queryset(self):
        return PremierProductQuerySet(
            self.model,
            using=self._db
        )

    def has_all_inventory_data(self):
        return self.get_queryset().has_all_inventory_data()

    def has_missing_inventory_data(self):
        return self.get_queryset().has_missing_inventory_data()

    def has_all_pricing_data(self):
        return self.get_queryset().has_all_pricing_data()

    def has_missing_pricing_data(self):
        return self.get_queryset().has_missing_pricing_data()

    def update_inventory_from_api(self):
        return self.get_queryset().update_inventory_from_api()

    def update_pricing_from_api(self):
        return self.get_queryset().update_pricing_from_api()
