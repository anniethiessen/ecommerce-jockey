from django.db.models import (
    Manager,
    QuerySet,
    Count,
    Q
)

from core.utils import chunkify_list
from .clients import premier_client


class PremierManufacturerQuerySet(QuerySet):
    def with_admin_data(self):
        return self.prefetch_related(
            'products'
        ).annotate(
            _product_count=Count(
                'products',
                distinct=True
            ),
            _product_relevant_count=Count(
                'products',
                filter=Q(products__is_relevant=True),
                distinct=True
            )
        )


class PremierProductQuerySet(QuerySet):
    def with_admin_data(self):
        return self.select_related(
            'manufacturer'
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

    # <editor-fold desc="perform properties ...">
    def perform_inventory_update_from_api(self):
        msgs = []

        queryset = self.all()
        part_numbers = [obj.premier_part_number for obj in queryset]

        chunks = chunkify_list(part_numbers, chunk_size=50)
        for chunk in chunks:
            try:
                response = self.model.objects.retrieve_inventory_data_from_api(chunk)
                for items in response:
                    obj = queryset.get(premier_part_number=items['itemNumber'])
                    data = items['inventory']
                    update_fields = self.model.objects.parse_api_inventory_data(
                        data
                    )
                    msgs.append(
                        obj.perform_inventory_update_from_api_data(**update_fields)
                    )
            except Exception as err:
                msgs.append(f'Chunk Error: {chunk}, {err}')
                continue
        return msgs

    def perform_pricing_update_from_api(self):
        msgs = []

        queryset = self.all()
        part_numbers = [obj.premier_part_number for obj in queryset]

        chunks = chunkify_list(part_numbers, chunk_size=50)
        for chunk in chunks:
            try:
                response = self.model.objects.retrieve_pricing_data_from_api(chunk)
                for items in response:
                    obj = queryset.get(premier_part_number=items['itemNumber'])
                    data = items['pricing']
                    update_fields = self.model.objects.parse_api_pricing_data(
                        data
                    )
                    msgs.append(
                        obj.perform_pricing_update_from_api_data(**update_fields)
                    )
            except Exception as err:
                msgs.append(f'Chunk Error: {chunk}, {err}')
                continue
        return msgs

    def perform_primary_image_update_from_media_root(self):
        msgs = []
        for obj in self:
            try:
                msgs.append(obj.perform_primary_image_update_from_media_root())
            except Exception as err:
                msgs.append(self.model.get_class_error_msg(str(err)))
                continue
        if not msgs:
            msgs.append(self.model.get_class_up_to_date_msg())
        return msgs
    # </editor-fold>


class PremierManufacturerManager(Manager):
    def get_queryset(self):
        return PremierManufacturerQuerySet(
            self.model,
            using=self._db
        )

    def with_admin_data(self):
        return self.get_queryset().with_admin_data()


class PremierProductManager(Manager):
    def get_queryset(self):
        return PremierProductQuerySet(
            self.model,
            using=self._db
        )

    def with_admin_data(self):
        return self.get_queryset().with_admin_data()

    def has_all_inventory_data(self):
        return self.get_queryset().has_all_inventory_data()

    def has_missing_inventory_data(self):
        return self.get_queryset().has_missing_inventory_data()

    def has_all_pricing_data(self):
        return self.get_queryset().has_all_pricing_data()

    def has_missing_pricing_data(self):
        return self.get_queryset().has_missing_pricing_data()

    # <editor-fold desc="retrieve properties ...">
    @staticmethod
    def retrieve_inventory_data_from_api(part_numbers):
        try:
            return premier_client.retrieve_product_inventory(part_numbers)
        except Exception:
            raise

    @staticmethod
    def retrieve_pricing_data_from_api(part_numbers):
        try:
            return premier_client.retrieve_product_pricing(part_numbers)
        except Exception:
            raise
    # </editor-fold>

    # <editor-fold desc="update properties ...">
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
    # </editor-fold>

    # <editor-fold desc="perform properties ...">
    def perform_inventory_update_from_api(self):
        return self.get_queryset().perform_inventory_update_from_api()

    def perform_pricing_update_from_api(self):
        return self.get_queryset().perform_pricing_update_from_api()

    def perform_primary_image_update_from_media_root(self):
        msgs = []
        try:
            msgs += self.get_queryset().perform_primary_image_update_from_media_root()
        except Exception as err:
            msgs.append(self.model.get_class_error_msg(str(err)))
        return msgs
    # </editor-fold>
