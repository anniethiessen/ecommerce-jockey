"""
This module defines any API clients used by the Shopify app.

"""


import simplejson as json
import requests
from requests.exceptions import HTTPError
from retry import retry

from django.conf import settings

from core.exceptions import ApiRateLimitExceeded


class ShopifyApiClient(object):
    """
    This class defines the client used to perform calls to the Shopify
    API.

    """

    def __init__(self):
        """
        Initializes client by setting base url.

        """

        self.base_url = settings.SHOPIFY_BASE_URL

    def get_json_body(self, response):
        """
        Checks response and returns json response body as dictionary.

        :param response: requests Response object
        :type response: object

        :return: response body as dictionary
        :rtype: dict

        :raises ApiRateLimitExceeded: response status code is 429
        :raises Exception: response status code not in 200s
        :raises Exception:  on general exception

        """

        try:
            if response.status_code == requests.codes.too_many_requests:
                print("Waiting on Shopify API (rate exceeded)")
                raise ApiRateLimitExceeded
            response.raise_for_status()
            return json.loads(response.text)
        except HTTPError:
            error = json.loads(response.text).get('errors', '')
            raise Exception(f'API error: {error}')
        except Exception:
            raise

    @retry(exceptions=ApiRateLimitExceeded, tries=2, delay=2)
    def create_product(self, product_data):
        """
        Creates product by Shopify API.

        :param product_data: product data
        :type product_data: dict

        :return: product data
        :rtype: dict

        :raises Exception: on general exception

        .. Topic:: **-Retries-**

            Retries on `ApiRateLimitExceeded` exception

            (up to 2 times in 2 second delays)

        **-Expected Product Data Format-**
        ::
            ret = {
                "title": <str>, (required)
                "body_html": <str>, (optional)
                "vendor": <str>, (optional)
                "product_type": <str>, (optional)
                "is_published": (optional)
                "tags": <str>, (optional)
                "variants": [ (optional)
                    {
                        "title": <str>,
                        "position": <int>, (optional)
                        "option1": <str>, (optional)
                        "option2": <str>, (optional)
                        "option3": <str>, (optional)
                        "sku": <str>, (optional)
                        "barcode": <str>, (optional)
                        "price": <decimal>, (optional)
                        "compare_at_price": <decimal>, (optional)
                        "grams": <int>, (optional)
                        "weight": <decimal>, (optional)
                        "weight_unit": <str>, (optional)
                        "fulfillment_service": <str>, (optional)
                        "inventory_management": <str>, (optional)
                        "inventory_policy": <str>, (optional)
                        "inventory_quantity": <int>, (optional)
                        "taxable": <bool> (optional)
                    },
                    {...}
                ],
                "options": [ (optional)
                    {
                        "name": <str>,
                        "position": <int>,  (optional)
                        "values": [
                            <str>,
                            ...
                        ]
                    },
                    {...}
                ],
                "image": {
                    "admin_graphql_api_id": <str>,
                    "id": <int>,
                    "product_id": <int>,
                    "position": <int>,
                    "created_at": <datetime>,
                    "updated_at": <datetime>,
                    "alt": <str> or None,
                    "width": <int>,
                    "height": <int>,
                    "src": <url>,
                    "variant_ids": [
                        <int>,
                        ...
                    ] or []
                } or None,
                images: [
                    {
                        "admin_graphql_api_id": <str>,
                        "id": <int>,
                        "product_id": <int>,
                        "position": <int>,
                        "created_at": <datetime>,
                        "updated_at": <datetime>,
                        "alt": <str> or None,
                        "width": <int>,
                        "height": <int>,
                        "src": <url>,
                        "variant_ids": [
                            <int>,
                            ...
                        ]
                    },
                    {...}
                ] or []
            }

        **-Return Format-**
        ::
            ret = {
                "admin_graphql_api_id": <str>,
                "id": <int>,
                "created_at": <datetime>,
                "updated_at": <datetime>,
                "published_at": <datetime> or None,
                "published_scope": <str>,
                "template_suffix": <str> or None,
                "handle": <str>,
                "title": <str>,
                "body_html": <str> or None,
                "product_type": <str>,
                "vendor": <str>,
                "tags": <str>,
                "variants": [
                    {
                        "admin_graphql_api_id": '<str>,
                        "id": <int>,
                        "created_at": <datetime>,
                        "updated_at": <datetime>,
                        "product_id": <int>,
                        "image_id": <int> or None,
                        "inventory_item_id": <int>,
                        "title": <str>,
                        "position": <int>,
                        "option1": <str>,
                        "option2": <str> or None,
                        "option3": <str> or None,
                        "sku": <str>,
                        "barcode": <str> or None,
                        "price": <decimal>,
                        "compare_at_price": <decimal> or None,
                        "grams": <int>,
                        "weight": <decimal>,
                        "weight_unit": <str>,
                        "fulfillment_service": <str>,
                        "inventory_management": <str> or None,
                        "inventory_policy": <str>,
                        "inventory_quantity": <int>,
                        "old_inventory_quantity": <int>,
                        "requires_shipping": <bool>,
                        "taxable": <bool>
                    },
                    {...}
                ],
                "options": [
                    {
                        "id": <int>,
                        "name": <str>,
                        "position": <int>,
                        "product_id": <int>,
                        "values": [
                            <str>,
                            ...
                        ]
                    },
                    {...}
                ],
                "image": {
                    "admin_graphql_api_id": <str>,
                    "id": <int>,
                    "product_id": <int>,
                    "position": <int>,
                    "created_at": <datetime>,
                    "updated_at": <datetime>,
                    "alt": <str> or None,
                    "width": <int>,
                    "height": <int>,
                    "src": <url>,
                    "variant_ids": [
                        <int>,
                        ...
                    ] or []
                } or None,
                images: [
                    {
                        "admin_graphql_api_id": <str>,
                        "id": <int>,
                        "product_id": <int>,
                        "position": <int>,
                        "created_at": <datetime>,
                        "updated_at": <datetime>,
                        "alt": <str> or None,
                        "width": <int>,
                        "height": <int>,
                        "src": <url>,
                        "variant_ids": [
                            <int>,
                            ...
                        ]
                    },
                    {...}
                ] or []
            }

        """

        url = f'{self.base_url}/products.json'
        body = {
            'product': product_data
        }

        try:
            response = requests.post(url=url, json=body)
            return self.get_json_body(response)['product']
        except Exception as err:
            raise


shopify_client = ShopifyApiClient()
