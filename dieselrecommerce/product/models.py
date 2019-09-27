import json

import requests

from django.conf import settings
from django.db.models import (
    Model,
    CharField,
    DecimalField,
    ForeignKey,
    IntegerField,
    CASCADE
)

from .managers import PremierProductManager


class PremierProduct(Model):
    premier_part_number = CharField(
        primary_key=True,
        max_length=20,
        unique=True
    )
    vendor_part_number = CharField(
        max_length=20,
    )
    description = CharField(
        max_length=300
    )
    manufacturer = CharField(
        max_length=30
    )
    msrp = DecimalField(
        max_digits=10,
        decimal_places=2
    )
    map = DecimalField(
        max_digits=10,
        decimal_places=2
    )
    jobber = DecimalField(
        max_digits=10,
        decimal_places=2
    )
    cost = DecimalField(
        max_digits=10,
        decimal_places=2
    )
    part_status = CharField(
        max_length=20
    )
    weight = DecimalField(
        blank=True,
        decimal_places=2,
        help_text='lbs',
        max_digits=10,
        null=True
    )
    length = DecimalField(
        blank=True,
        decimal_places=2,
        help_text='in',
        max_digits=10,
        null=True
    )
    width = DecimalField(
        blank=True,
        decimal_places=2,
        help_text='in',
        max_digits=10,
        null=True
    )
    height = DecimalField(
        blank=True,
        decimal_places=2,
        help_text='in',
        max_digits=10,
        null=True
    )
    upc = CharField(
        max_length=50,
        blank=True
    )
    inventory_ab = IntegerField(
        blank=True,
        null=True,
        verbose_name='Alberta inventory'
    )
    inventory_po = IntegerField(
        blank=True,
        null=True,
        verbose_name='PO inventory'
    )
    inventory_ut = IntegerField(
        blank=True,
        null=True,
        verbose_name='Utah inventory'
    )
    inventory_ky = IntegerField(
        blank=True,
        null=True,
        verbose_name='Kentucky inventory'
    )
    inventory_tx = IntegerField(
        blank=True,
        null=True,
        verbose_name='Texas inventory'
    )
    inventory_ca = IntegerField(
        blank=True,
        null=True,
        verbose_name='California inventory'
    )
    inventory_wa = IntegerField(
        blank=True,
        null=True,
        verbose_name='Washington inventory'
    )
    inventory_co = IntegerField(
        blank=True,
        null=True,
        verbose_name='Colorado inventory'
    )

    objects = PremierProductManager()

    def clear_inventory(self):
        self.inventory_ab = None
        self.inventory_po = None
        self.inventory_ut = None
        self.inventory_ky = None
        self.inventory_tx = None
        self.inventory_ca = None
        self.inventory_wa = None
        self.inventory_co = None
        self.save()

    def get_inventory_data(self):
        return {
            'AB': self.inventory_ab,
            'PO': self.inventory_po,
            'UT': self.inventory_ut,
            'KY': self.inventory_ky,
            'TX': self.inventory_tx,
            'CA': self.inventory_ca,
            'WA': self.inventory_wa,
            'CO': self.inventory_co
        }

    def get_inventory_update_success_msg(self, previous_inventory_data):
        previous = previous_inventory_data
        new = self.get_inventory_data()

        msg = f'Success: {self} updated'
        for loc, inv in new.items():
            if not inv == previous[loc]:
                msg += f", {loc}: {previous[loc]} -> {inv}"
        return msg

    def get_inventory_update_error_msg(self, error):
        msg = f'Error: {self}, {error}'
        return msg

    @classmethod
    def get_premier_api_headers(cls, token=None):
        if not token:
            token = cls.retrieve_premier_api_token()

        return {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

    @classmethod
    def retrieve_premier_api_token(cls):
        try:
            url = f'{settings.PREMIER_BASE_URL}/authenticate'
            params = {'apiKey': settings.PREMIER_API_KEY}
            response = requests.get(url=url, params=params)
            return json.loads(response.text)['sessionToken']
        except Exception:
            raise

    @classmethod
    def retrieve_premier_api_inventory(cls, part_numbers, token=None):
        try:
            if not token:
                token = cls.retrieve_premier_api_token()

            url = f'{settings.PREMIER_BASE_URL}/inventory'
            params = {'itemNumbers': ','.join(part_numbers)}
            headers = cls.get_premier_api_headers(token)
            response = requests.get(url=url, headers=headers, params=params)
            return json.loads(response.text)
        except Exception:
            raise

    def update_inventory_from_premier_api(self, token=None):
        if not self.premier_part_number:
            return self.get_inventory_update_error_msg(
                "Premier Part Number required")

        try:
            if not token:
                token = self.retrieve_premier_api_token()
            response = self.retrieve_premier_api_inventory(
                [self.premier_part_number], token)
            data = response[0]['inventory']
            return self.update_inventory_from_data(data)
        except Exception as err:
            return self.get_inventory_update_error_msg(str(err))

    def update_inventory_from_data(self, data):
        previous = self.get_inventory_data()

        try:
            self.clear_inventory()
            for item in data:
                setattr(
                    self,
                    f'inventory_{item["warehouseCode"][:2].lower()}',
                    int(item['quantityAvailable'])
                )
                self.save()
        except Exception as err:
            return self.get_inventory_update_error_msg(str(err))

        return self.get_inventory_update_success_msg(previous)

    def __str__(self):
        return f'{self.premier_part_number} :: {self.manufacturer}'


class SemaBrand(Model):
    brand_id = CharField(
        primary_key=True,
        max_length=10
    )
    name = CharField(
        max_length=50,
    )

    def __str__(self):
        return f'{self.brand_id} :: {self.name}'


class SemaDataset(Model):
    dataset_id = CharField(
        primary_key=True,
        max_length=10
    )
    name = CharField(
        max_length=100,
    )
    brand = ForeignKey(
        SemaBrand,
        on_delete=CASCADE,
        related_name='sema_datasets'
    )

    def __str__(self):
        return f'{self.dataset_id} :: {self.name}'


class SemaProduct(Model):
    product_id = CharField(
        primary_key=True,
        max_length=30
    )
    dataset = ForeignKey(
        SemaDataset,
        on_delete=CASCADE,
        related_name='sema_products',
    )

    def __str__(self):
        return f'{self.product_id}'
