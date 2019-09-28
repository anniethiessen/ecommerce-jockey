import json

import requests

from django.conf import settings


class ApiCoreMixin(object):
    def get_create_or_update_success_msg(self, created):
        action = 'created' if created else 'updated'
        return f'Success: {self} {action}'

    @classmethod
    def get_create_or_update_error_msg(cls, error):
        msg = f'Error: {cls}, {error}'
        return msg

    def get_update_success_msg(self, previous_data, new_data):
        msg = f'Success: {self} updated'
        for loc, inv in new_data.items():
            if not inv == previous_data[loc]:
                msg += f", {loc}: {previous_data[loc]} -> {inv}"
        return msg

    def get_update_error_msg(self, error):
        msg = f'Error: {self}, {error}'
        return msg


# <editor-fold desc="Premier">
class PremierApiCoreMixin(ApiCoreMixin):
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


class PremierApiProductMixin(PremierApiCoreMixin):
    @classmethod
    def retrieve_premier_api_inventory(cls, part_numbers, token=None):
        try:
            if not token:
                token = cls.retrieve_premier_api_token()

            url = f'{settings.PREMIER_BASE_URL}/inventory'
            params = {'itemNumbers': ','.join(part_numbers)}
            headers = cls.get_premier_api_headers(token)
            response = requests.get(url=url, headers=headers,
                                    params=params)
            return json.loads(response.text)
        except Exception:
            raise

    @classmethod
    def retrieve_premier_api_pricing(cls, part_numbers, token=None):
        try:
            if not token:
                token = cls.retrieve_premier_api_token()

            url = f'{settings.PREMIER_BASE_URL}/pricing'
            params = {'itemNumbers': ','.join(part_numbers)}
            headers = cls.get_premier_api_headers(token)
            response = requests.get(url=url, headers=headers,
                                    params=params)
            return json.loads(response.text)
        except Exception:
            raise


class PremierProductMixin(PremierApiProductMixin):
    # <editor-fold desc="Inventory">
    def clear_inventory_fields(self):
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

    def update_inventory_from_premier_api(self, token=None):
        if not self.premier_part_number:
            return self.get_update_error_msg(
                "Premier Part Number required")

        try:
            if not token:
                token = self.retrieve_premier_api_token()
            response = self.retrieve_premier_api_inventory(
                [self.premier_part_number], token)
            data = response[0]['inventory']
            return self.update_inventory_from_data(data)
        except Exception as err:
            return self.get_update_error_msg(str(err))

    def update_inventory_from_data(self, data):
        previous = self.get_inventory_data()

        try:
            self.clear_inventory_fields()
            for item in data:
                setattr(
                    self,
                    f'inventory_{item["warehouseCode"][:2].lower()}',
                    int(item['quantityAvailable'])
                )
                self.save()
        except Exception as err:
            return self.get_update_error_msg(str(err))

        self.refresh_from_db()
        new = self.get_inventory_data()
        return self.get_update_success_msg(previous, new)
    # </editor-fold>

    # <editor-fold desc="Pricing">
    def clear_pricing_fields(self):
        self.cost_cad = None
        self.cost_usd = None
        self.jobber_cad = None
        self.jobber_usd = None
        self.msrp_cad = None
        self.msrp_usd = None
        self.map_cad = None
        self.map_usd = None
        self.save()

    def get_pricing_data(self):
        return {
            'Cost CAD': self.cost_cad,
            'Cost USD': self.cost_usd,
            'Jobber CAD': self.jobber_cad,
            'Jobber USD': self.jobber_usd,
            'MSRP CAD': self.msrp_cad,
            'MSRP USD': self.msrp_usd,
            'MAP CAD': self.map_cad,
            'MAP USD': self.map_usd
        }

    def update_pricing_from_premier_api(self, token=None):
        if not self.premier_part_number:
            return self.get_update_error_msg(
                "Premier Part Number required")

        try:
            if not token:
                token = self.retrieve_premier_api_token()
            response = self.retrieve_premier_api_pricing(
                [self.premier_part_number], token)
            data = response[0]['pricing']
            return self.update_pricing_from_data(data)
        except Exception as err:
            return self.get_update_error_msg(str(err))

    def update_pricing_from_data(self, data):
        previous = self.get_pricing_data()

        try:
            self.clear_pricing_fields()
            for item in data:
                currency = item.pop('currency')
                item['msrp'] = item.pop('retail')
                for key, value in item.items():
                    setattr(
                        self,
                        f'{key.lower()}_{currency.lower()}',
                        value
                    )
                self.save()
        except Exception as err:
            return self.get_update_error_msg(str(err))

        self.refresh_from_db()
        new = self.get_pricing_data()
        return self.get_update_success_msg(previous, new)
    # </editor-fold>
# </editor-fold>


# <editor-fold desc="SEMA">
class SemaApiCoreMixin(ApiCoreMixin):
    @classmethod
    def retrieve_sema_api_token(cls):
        try:
            url = f'{settings.SEMA_BASE_URL}/token/get'
            params = {
                'userName': settings.SEMA_USERNAME,
                'password': settings.SEMA_PASSWORD
            }
            response = requests.get(url=url, params=params)
            response = json.loads(response.text)
            if response['success']:
                return response['token']
            else:
                raise Exception(str(response['message']))
        except Exception:
            raise


class SemaApiBrandMixin(SemaApiCoreMixin):
    @classmethod
    def retrieve_sema_brand_datasets(cls, token=None):
        try:
            if not token:
                token = cls.retrieve_sema_api_token()

            url = f'{settings.SEMA_BASE_URL}/export/branddatasets'
            params = {'token': token}
            response = requests.get(url=url, params=params)
            response = json.loads(response.text)
            if response['success']:
                return response['BrandDatasets']
            else:
                raise Exception(str(response['message']))
        except Exception:
            raise


class SemaBrandMixin(SemaApiBrandMixin):
    @classmethod
    def unauthorize_datasets(cls):
        from product.models import SemaDataset
        SemaDataset.objects.all().update(is_authorized=False)

    @classmethod
    def import_brand_datasets_from_sema_api(cls, token=None):
        try:
            if not token:
                token = cls.retrieve_sema_api_token()
            data = cls.retrieve_sema_brand_datasets(token)
            return cls.create_brand_datasets_from_data(data)
        except Exception as err:
            return cls.get_create_or_update_error_msg(str(err))

    @classmethod
    def create_brand_datasets_from_data(cls, data):
        from product.models import SemaDataset

        msgs = []

        try:
            cls.unauthorize_datasets()
            for item in data:
                try:
                    brand, c = cls.objects.update_or_create(
                        brand_id=item['AAIABrandId'],
                        defaults={'name': item['BrandName']}
                    )
                    msgs.append(brand.get_create_or_update_success_msg(c))
                    dataset, c = SemaDataset.objects.update_or_create(
                        dataset_id=item['DatasetId'],
                        defaults={
                            'name': item['DatasetName'],
                            'brand': brand,
                            'is_authorized': True
                        }
                    )
                    msgs.append(dataset.get_create_or_update_success_msg(c))
                except Exception as err:
                    msgs.append(cls.get_create_or_update_error_msg(str(err)))
        except Exception as err:
            msgs.append(cls.get_create_or_update_error_msg(str(err)))

        return msgs
# </editor-fold>
