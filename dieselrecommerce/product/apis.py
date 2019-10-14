import requests
import json
from retry import retry

from django.conf import settings

from .exceptions import (
    ApiInvalidContentToken,
    ApiInvalidToken,
    ApiRateLimitExceeded
)


class SemaApi(object):
    def __init__(self):
        self.token = self.retrieve_token()
        self.content_token = self.retrieve_content_token()

    def get_json_body(self, response):
        try:
            if response.status_code == requests.codes.conflict:
                print("Waiting on SEMA API (rate exceeded)")
                raise ApiRateLimitExceeded
            response.raise_for_status()
            body = json.loads(response.text)
            if body.get('success'):
                if body.get('message') == 'Invalid token':
                    self.token = self.retrieve_token()
                    raise ApiInvalidToken
            else:
                raise Exception(body.get('message', 'Bad request'))
            return body
        except Exception:
            raise

    def get_html_body(self, response):
        try:
            if response.status_code == requests.codes.conflict:
                raise ApiRateLimitExceeded
            response.raise_for_status()
            body = str(response.text).strip()
            if 'Invalid token' in body:
                self.content_token = self.retrieve_content_token()
                raise ApiInvalidContentToken
            return body
        except Exception:
            raise

    @retry(exceptions=ApiRateLimitExceeded, tries=12, delay=5)
    def retrieve_token(self):
        url = f'{settings.SEMA_BASE_URL}/token/get'
        params = {
            'userName': settings.SEMA_USERNAME,
            'password': settings.SEMA_PASSWORD
        }

        try:
            response = requests.get(url=url, params=params)
            return self.get_json_body(response)['token']
        except Exception as err:
            raise

    @retry(exceptions=ApiInvalidToken, tries=1)
    @retry(exceptions=ApiRateLimitExceeded, tries=12, delay=5)
    def retrieve_content_token(self):
        url = f'{settings.SEMA_BASE_URL}/token/getcontenttoken'
        params = {'token': self.token}

        try:
            response = requests.get(url=url, params=params)
            return self.get_json_body(response)['contenttoken']
        except Exception:
            raise

    @retry(exceptions=ApiInvalidToken, tries=1)
    @retry(exceptions=ApiRateLimitExceeded, tries=12, delay=5)
    def retrieve_brand_datasets(self):
        url = f'{settings.SEMA_BASE_URL}/export/branddatasets'
        params = {
            'token': self.token
        }

        try:
            response = requests.get(url=url, params=params)
            return self.get_json_body(response)['BrandDatasets']
        except Exception:
            raise

    @retry(exceptions=ApiInvalidToken, tries=1)
    @retry(exceptions=ApiRateLimitExceeded, tries=12, delay=5)
    def retrieve_years(self, brand_id=None, dataset_id=None):
        url = f'{settings.SEMA_BASE_URL}/lookup/years'
        params = {
            'token': self.token,
            'aaia_brandids': brand_id,
            'branddatasetids': dataset_id
        }

        try:
            response = requests.get(url=url, params=params)
            return self.get_json_body(response)['Years']
        except Exception:
            raise

    @retry(exceptions=ApiInvalidToken, tries=1)
    @retry(exceptions=ApiRateLimitExceeded, tries=12, delay=5)
    def retrieve_makes(self, brand_id=None, dataset_id=None, year=None):
        url = f'{settings.SEMA_BASE_URL}/lookup/makes'
        params = {
            'token': self.token,
            'aaia_brandids': brand_id,
            'branddatasetids': dataset_id,
            'years': year
        }

        try:
            response = requests.get(url=url, params=params)
            return self.get_json_body(response)['Makes']
        except Exception:
            raise

    @retry(exceptions=ApiInvalidToken, tries=1)
    @retry(exceptions=ApiRateLimitExceeded, tries=12, delay=5)
    def retrieve_models(self, brand_id=None, dataset_id=None,
                        year=None, make_id=None):
        url = f'{settings.SEMA_BASE_URL}/lookup/models'
        params = {
            'token': self.token,
            'aaia_brandids': brand_id,
            'branddatasetids': dataset_id,
            'years': year,
            'makeid': make_id
        }

        try:
            response = requests.get(url=url, params=params)
            return self.get_json_body(response)['Models']
        except Exception:
            raise

    @retry(exceptions=ApiInvalidToken, tries=1)
    @retry(exceptions=ApiRateLimitExceeded, tries=12, delay=5)
    def retrieve_submodels(self, brand_id=None, dataset_id=None,
                           year=None, make_id=None, model_id=None):
        url = f'{settings.SEMA_BASE_URL}/lookup/submodels'
        params = {
            'token': self.token,
            'aaia_brandids': brand_id,
            'branddatasetids': dataset_id,
            'years': year,
            'makeid': make_id,
            'modelid': model_id
        }

        try:
            response = requests.get(url=url, params=params)
            return self.get_json_body(response)['Submodels']
        except Exception:
            raise

    @retry(exceptions=ApiInvalidToken, tries=1)
    @retry(exceptions=ApiRateLimitExceeded, tries=12, delay=5)
    def retrieve_engines(self, brand_id=None, dataset_id=None,
                         year=None, make_id=None, model_id=None):
        url = f'{settings.SEMA_BASE_URL}/lookup/engines'
        params = {
            'token': self.token,
            'aaia_brandids': brand_id,
            'branddatasetids': dataset_id,
            'year': year,
            'makeid': make_id,
            'modelid': model_id
        }

        try:
            response = requests.get(url=url, params=params)
            return self.get_json_body(response)['Engines']
        except Exception:
            raise

    @retry(exceptions=ApiInvalidToken, tries=1)
    @retry(exceptions=ApiRateLimitExceeded, tries=12, delay=5)
    def retrieve_vehicle_info(self, base_vehicle_id, vehicle_id):
        url = f'{settings.SEMA_BASE_URL}/lookup/expandedvehicleinfo'
        params = {
            'token': self.token,
            'baseVehicleID': base_vehicle_id,
            'vehicleID': vehicle_id
        }

        try:
            response = requests.get(url=url, params=params)
            return self.get_json_body(response)['Vehicles']
        except Exception:
            raise

    @retry(exceptions=ApiInvalidToken, tries=1)
    @retry(exceptions=ApiRateLimitExceeded, tries=12, delay=5)
    def retrieve_categories(self, brand_id=None, dataset_id=None,
                            base_vehicle_id=None, vehicle_id=None,
                            year=None, make_name=None,
                            model_name=None, submodel_name=None):
        if not brand_id or dataset_id:
            raise Exception('Brand ID or dataset ID required')

        url = f'{settings.SEMA_BASE_URL}/lookup/categories'
        data = {
            'token': self.token,
            'aaia_brandids': brand_id,
            'branddatasetids': dataset_id,
            'baseVehicleIds': base_vehicle_id,
            'vehicleIds': vehicle_id,
            'Year': year,
            'MakeName': make_name,
            'ModelName': model_name,
            'SubmodelName': submodel_name
        }

        try:
            response = requests.post(url=url, json=data)
            return self.get_json_body(response)['Categories']
        except Exception:
            raise

    @retry(exceptions=ApiInvalidToken, tries=1)
    @retry(exceptions=ApiRateLimitExceeded, tries=12, delay=5)
    def retrieve_products_by_brand(self, brand_id=None, dataset_id=None,
                                   base_vehicle_id=None, vehicle_id=None,
                                   year=None, make_name=None,
                                   model_name=None, submodel_name=None,
                                   part_number=None, pies_segments=None):
        if not brand_id or dataset_id:
            raise Exception('Brand ID or dataset ID required')

        url = f'{settings.SEMA_BASE_URL}/lookup/products'
        data = {
            'token': self.token,
            'aaia_brandid': brand_id,
            'branddatasetid': dataset_id,
            'baseVehicleIds': base_vehicle_id,
            'vehicleIds': vehicle_id,
            'Year': year,
            'MakeName': make_name,
            'ModelName': model_name,
            'SubmodelName': submodel_name,
            'partNumbers': part_number,
            'piesSegments': pies_segments
        }

        try:
            response = requests.post(url=url, json=data)
            return self.get_json_body(response)['Products']
        except Exception:
            raise

    @retry(exceptions=ApiInvalidToken, tries=1)
    @retry(exceptions=ApiRateLimitExceeded, tries=12, delay=5)
    def retrieve_products_by_category(self, category_id,
                                      include_child_categories=False,
                                      brand_id=None, dataset_id=None,
                                      base_vehicle_id=None, vehicle_id=None,
                                      year=None, make_name=None,
                                      model_name=None, submodel_name=None,
                                      part_number=None, pies_segments=None):
        url = f'{settings.SEMA_BASE_URL}/lookup/productsbycategory'
        data = {
            'token': self.token,
            'CategoryId': category_id,
            'includeChildCategoryParts': (
                str(include_child_categories).lower()
                if include_child_categories else None
            ),
            'aaia_brandids': brand_id,
            'branddatasetids': dataset_id,
            'baseVehicleIds': base_vehicle_id,
            'vehicleIds': vehicle_id,
            'Year': year,
            'MakeName': make_name,
            'ModelName': model_name,
            'SubmodelName': submodel_name,
            'partNumbers': part_number,
            'piesSegments': pies_segments
        }

        try:
            response = requests.post(url=url, json=data)
            return self.get_json_body(response)['Products']
        except Exception:
            raise

    @retry(exceptions=ApiInvalidContentToken, tries=1)
    @retry(exceptions=ApiRateLimitExceeded, tries=12, delay=5)
    def retrieve_product_html(self, product_id, include_header_footer=False):
        url = f'{settings.SEMA_BASE_URL}/content/product'
        params = {
            'contenttoken': self.content_token,
            'productid': product_id,
            'stripHeaderFooter': (
                str(~include_header_footer).lower()
                if not include_header_footer else None
            )
        }

        try:
            response = requests.get(url=url, params=params)
            return self.get_html_body(response)
        except Exception:
            raise

    @retry(exceptions=ApiInvalidToken, tries=1)
    @retry(exceptions=ApiRateLimitExceeded, tries=12, delay=5)
    def retrieve_vehicles_by_product(self, brand_id=None, dataset_id=None,
                                     part_number=None, group_by_part=False):
        if not brand_id or dataset_id:
            raise Exception('Brand ID or dataset ID required')

        url = f'{settings.SEMA_BASE_URL}/lookup/vehiclesbyproduct'
        data = {
            'token': self.token,
            'aaia_brandid': brand_id,
            'branddatasetid': dataset_id,
            'partNumber': part_number,
            'groupByPart': (
                str(group_by_part).lower()
                if group_by_part else None
            )
        }

        try:
            response = requests.post(url=url, json=data)
            return self.get_json_body(response)['Vehicles']
        except Exception:
            raise

    @retry(exceptions=ApiInvalidToken, tries=1)
    @retry(exceptions=ApiRateLimitExceeded, tries=12, delay=5)
    def retrieve_vehicles_by_brand(self, brand_id=None, dataset_id=None):
        if not brand_id or dataset_id:
            raise Exception('Brand ID or dataset ID required')

        url = f'{settings.SEMA_BASE_URL}/lookup/vehiclesbybrand'
        data = {
            'token': self.token,
            'aaia_brandid': brand_id,
            'branddatasetid': dataset_id
        }

        try:
            response = requests.post(url=url, json=data)
            return self.get_json_body(response)['BrandVehicles']
        except Exception:
            raise
