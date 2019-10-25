from django.db.models import Q

from core.managers import (
    RelevancyBaseManager,
    RelevancyBaseQuerySet
)
from core.utils import chunkify_list
from .apis import premier_api


class PremierManufacturerQuerySet(RelevancyBaseQuerySet):
    def _get_relevancy_errors_flag_query(self):
        return (
            Q(is_relevant=True)
            & (
                Q(primary_image__isnull=True)
                | Q(primary_image__exact='')
            )
        )


class PremierProductQuerySet(RelevancyBaseQuerySet):
    def _get_may_be_relevant_query(self):
        return (
            Q(manufacturer__is_relevant=True)
            & Q(inventory_ab__isnull=False)
            & Q(inventory_ab__gt=0)
        )

    def _get_relevancy_errors_flag_query(self):
        return (
            Q(is_relevant=True)
            & (
                Q(manufacturer__is_relevant=False)
                | Q(inventory_ab__isnull=True)
                | Q(inventory_ab__lte=0)
                | Q(cost_cad__isnull=True)
                | Q(cost_cad__lte=0)
                | Q(primary_image__isnull=True)
                | Q(primary_image__exact='')
            )
        )

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

        queryset = self.all()
        part_numbers = [obj.premier_part_number for obj in queryset]

        chunks = chunkify_list(part_numbers, chunk_size=50)
        for chunk in chunks:
            try:
                response = self.model.objects.get_api_inventory_data(chunk)
                for items in response:
                    obj = queryset.get(premier_part_number=items['itemNumber'])
                    data = items['inventory']
                    update_fields = self.model.objects.parse_api_inventory_data(
                        data
                    )
                    msgs.append(
                        obj.update_inventory_from_api_data(**update_fields)
                    )
            except Exception as err:
                msgs.append(f'Chunk Error: {chunk}, {err}')
                continue
        return msgs

    def update_pricing_from_api(self):
        msgs = []

        queryset = self.all()
        part_numbers = [obj.premier_part_number for obj in queryset]

        chunks = chunkify_list(part_numbers, chunk_size=50)
        for chunk in chunks:
            try:
                response = self.model.objects.get_api_pricing_data(chunk)
                for items in response:
                    obj = queryset.get(premier_part_number=items['itemNumber'])
                    data = items['pricing']
                    update_fields = self.model.objects.parse_api_pricing_data(
                        data
                    )
                    msgs.append(
                        obj.update_pricing_from_api_data(**update_fields)
                    )
            except Exception as err:
                msgs.append(f'Chunk Error: {chunk}, {err}')
                continue
        return msgs

    def update_primary_image_from_media_root(self):
        msgs = []
        for obj in self:
            try:
                msgs.append(obj.update_primary_image_from_media_root())
            except Exception as err:
                msgs.append(self.model.get_class_error_msg(str(err)))
                continue
        if not msgs:
            msgs.append(self.model.get_class_up_to_date_msg())
        return msgs


class PremierManufacturerManager(RelevancyBaseManager):
    def get_queryset(self):
        return PremierManufacturerQuerySet(
            self.model,
            using=self._db
        )


class PremierProductManager(RelevancyBaseManager):
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

    def update_primary_image_from_media_root(self):
        msgs = []
        try:
            msgs += self.get_queryset().update_primary_image_from_media_root()
        except Exception as err:
            msgs.append(self.model.get_class_error_msg(str(err)))
        return msgs
