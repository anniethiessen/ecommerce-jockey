import requests
import json
from retry import retry

from django.conf import settings

from core.exceptions import ApiInvalidToken


class PremierApiClient(object):
    def __init__(self):
        self.token = self.retrieve_token()

    def get_headers(self):
        return {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }

    def get_json_body(self, response):
        try:
            if response.status_code == requests.codes.unauthorized:
                self.token = self.retrieve_token()
                raise ApiInvalidToken
            response.raise_for_status()
            return json.loads(response.text)
        except Exception:
            raise

    def retrieve_token(self):
        url = f'{settings.PREMIER_BASE_URL}/authenticate'
        params = {
            'apiKey': settings.PREMIER_API_KEY
        }

        try:
            response = requests.get(url=url, params=params)
            return self.get_json_body(response)['sessionToken']
        except Exception as err:
            raise

    @retry(exceptions=ApiInvalidToken, tries=2)
    def retrieve_product_inventory(self, part_numbers):
        url = f'{settings.PREMIER_BASE_URL}/inventory'
        params = {'itemNumbers': ','.join(part_numbers)}
        headers = self.get_headers()

        try:
            response = requests.get(url=url, headers=headers, params=params)
            return self.get_json_body(response)
        except Exception:
            raise

    @retry(exceptions=ApiInvalidToken, tries=2)
    def retrieve_product_pricing(self, part_numbers):
        url = f'{settings.PREMIER_BASE_URL}/pricing'
        params = {'itemNumbers': ','.join(part_numbers)}
        headers = self.get_headers()

        try:
            response = requests.get(url=url, headers=headers, params=params)
            return self.get_json_body(response)
        except Exception:
            raise


premier_client = PremierApiClient()
