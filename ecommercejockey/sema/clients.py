"""
This module defines any API clients used by the SEMA app.

"""


import requests
import json
from retry import retry

from django.conf import settings

from core.exceptions import (
    ApiInvalidContentToken,
    ApiInvalidToken,
    ApiRateLimitExceeded
)


class SemaApiClient(object):
    """
    This class defines the client used to perform calls to the SEMA API.

    """

    def __init__(self):
        """
        Initializes model by setting base url and retrieving token and
        content token.

        """

        self.base_url = settings.SEMA_BASE_URL
        self.token = self.retrieve_token()
        self.content_token = self.retrieve_content_token()

    def get_json_body(self, response):
        """
        Checks response and returns json response body as dictionary.

        :param response: requests Response object
        :type response: object

        :return: response body as dictionary
        :rtype: dict

        :raises ApiRateLimitExceeded: response status code is 409
        :raises HTTPError: response status code not in 200s
        :raises ApiInvalidToken: response body 'message' is "Invalid
        token" (after refreshing token)
        :raises Exception: response body 'success' not True or on
        general exception

        """

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
        """
        Checks response, then strips and returns HTML response body.

        :param response: requests Response object
        :type response: object

        :return: response body as text
        :rtype: str

        :raises ApiRateLimitExceeded: response status code is 409
        :raises HTTPError: response status code not in 200s
        :raises ApiInvalidToken: response body contains "Invalid
        token" (after refreshing token)
        :raises Exception: on general exception

        """

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

    @retry(exceptions=ApiRateLimitExceeded, tries=13, delay=5)
    def retrieve_token(self):
        """
        Retrieves token data from SEMA API.

        :return: token
        :rtype: str

        :raises Exception: on general exception

        .. Topic:: **-Retries-**

            Retries on `ApiRateLimitExceeded` exception

            (up to 13 times in 5 second delays)

        """

        url = f'{self.base_url}/token/get'
        params = {
            'userName': settings.SEMA_USERNAME,
            'password': settings.SEMA_PASSWORD
        }

        try:
            response = requests.get(url=url, params=params)
            return self.get_json_body(response)['token']
        except Exception as err:
            raise

    @retry(exceptions=ApiInvalidToken, tries=2)
    @retry(exceptions=ApiRateLimitExceeded, tries=13, delay=5)
    def retrieve_content_token(self):
        """
        Retrieves content token data from SEMA API.

        :return: content token
        :rtype: str

        :raises Exception: on general exception

        .. Topic:: **-Retries-**

            Retries on `ApiInvalidToken` exception
            (up to 2 times in 1 second delays)

            Retries on `ApiRateLimitExceeded` exception
            (up to 13 times in 5 second delays)

        """

        url = f'{self.base_url}/token/getcontenttoken'
        params = {'token': self.token}

        try:
            response = requests.get(url=url, params=params)
            return self.get_json_body(response)['contenttoken']
        except Exception:
            raise

    @retry(exceptions=ApiInvalidToken, tries=2)
    @retry(exceptions=ApiRateLimitExceeded, tries=13, delay=5)
    def retrieve_brand_datasets(self):
        """
        Retrieves brand datasets data from SEMA API.

        :return: brand datasets data
        :rtype: list

        :raises Exception: on general exception

        .. Topic:: **-Retries-**

            Retries on `ApiInvalidToken` exception
            (up to 2 times in 1 second delays)

            Retries on `ApiRateLimitExceeded` exception
            (up to 13 times in 5 second delays)

        **-Return Format-**
        ::
            ret = [
                {
                    "AAIABrandId": <str>,
                    "BrandName": <str>,
                    "DatasetId": <int>,
                    "DatasetName": <str>
                },
                {...}
            ]

        """

        url = f'{self.base_url}/export/branddatasets'
        params = {
            'token': self.token
        }

        try:
            response = requests.get(url=url, params=params)
            return self.get_json_body(response)['BrandDatasets']
        except Exception:
            raise

    @retry(exceptions=ApiInvalidToken, tries=2)
    @retry(exceptions=ApiRateLimitExceeded, tries=13, delay=5)
    def retrieve_years(self, brand_ids=None, dataset_ids=None):
        """
        Retrieves years data from SEMA API.

        :param brand_ids: brand IDs to on which to filter
        :type brand_ids: list
        :param dataset_ids: dataset IDs to on which to filter
        :type dataset_ids: list

        :return: years data
        :rtype: list

        :raises Exception: parameter misuse and on general exception

        .. Topic:: **-Parameters-**

            Only one of `brand_ids` or `dataset_ids` allowed

        .. Topic:: **-Retries-**

            Retries on `ApiInvalidToken` exception
            (up to 2 times in 1 second delays)

            Retries on `ApiRateLimitExceeded` exception
            (up to 13 times in 5 second delays)

        **-Return Format-**
        ::
            ret = [
                <int>,
                ...
            ]

        """

        if brand_ids and dataset_ids:
            raise Exception("Only one of brand IDs or dataset IDs allowed")

        url = f'{self.base_url}/lookup/years'
        params = {
            'token': self.token,
            'aaia_brandids': brand_ids,
            'branddatasetids': dataset_ids
        }

        try:
            response = requests.get(url=url, params=params)
            return self.get_json_body(response)['Years']
        except Exception:
            raise

    @retry(exceptions=ApiInvalidToken, tries=2)
    @retry(exceptions=ApiRateLimitExceeded, tries=13, delay=5)
    def retrieve_makes(self, brand_ids=None, dataset_ids=None, year=None):
        """
        Retrieves makes data from SEMA API.

        :param brand_ids: brand IDs to on which to filter
        :type brand_ids: list
        :param dataset_ids: dataset IDs to on which to filter
        :type dataset_ids: list
        :param year: year on which to filter
        :type year: int

        :return: makes data
        :rtype: list

        :raises Exception: parameter misuse and on general exception

        .. Topic:: **-Parameters-**

            Only one of `brand_ids` or `dataset_ids` allowed

        .. Topic:: **-Retries-**

            Retries on `ApiInvalidToken` exception
            (up to 2 times in 1 second delays)

            Retries on `ApiRateLimitExceeded` exception
            (up to 13 times in 5 second delays)

        **-Return Format-**
        ::
            ret = [
                {
                    "MakeID": <int>,
                    "MakeName": <str>
                },
                {...}
            ]

        """

        if brand_ids and dataset_ids:
            raise Exception("Only one of brand IDs or dataset IDs allowed")

        url = f'{self.base_url}/lookup/makes'
        params = {
            'token': self.token,
            'aaia_brandids': brand_ids,
            'branddatasetids': dataset_ids,
            'year': year
        }

        try:
            response = requests.get(url=url, params=params)
            return self.get_json_body(response)['Makes']
        except Exception:
            raise

    @retry(exceptions=ApiInvalidToken, tries=2)
    @retry(exceptions=ApiRateLimitExceeded, tries=13, delay=5)
    def retrieve_models(self, brand_ids=None, dataset_ids=None,
                        year=None, make_id=None):
        """
        Retrieves models data from SEMA API.

        :param brand_ids: brand IDs to on which to filter
        :type brand_ids: list
        :param dataset_ids: dataset IDs to on which to filter
        :type dataset_ids: list
        :param year: year on which to filter
        :type year: int
        :param make_id: make ID on which to filter
        :type make_id: int

        :return: models data
        :rtype: list

        :raises Exception: parameter misuse and on general exception

        .. Topic:: **-Parameters-**

            Only one of `brand_ids` or `dataset_ids` allowed

        .. Topic:: **-Retries-**

            Retries on `ApiInvalidToken` exception
            (up to 2 times in 1 second delays)

            Retries on `ApiRateLimitExceeded` exception
            (up to 13 times in 5 second delays)

        **-Return Format-**
        ::
            ret = [
                {
                    "BaseVehicleID": <int>,
                    "ModelID": <int>,
                    "ModelName": <str>
                },
                {...}
            ]

        """

        if brand_ids and dataset_ids:
            raise Exception("Only one of brand IDs or dataset IDs allowed")

        url = f'{self.base_url}/lookup/models'
        params = {
            'token': self.token,
            'aaia_brandids': brand_ids,
            'branddatasetids': dataset_ids,
            'year': year,
            'makeid': make_id
        }

        try:
            response = requests.get(url=url, params=params)
            return self.get_json_body(response)['Models']
        except Exception:
            raise

    @retry(exceptions=ApiInvalidToken, tries=2)
    @retry(exceptions=ApiRateLimitExceeded, tries=13, delay=5)
    def retrieve_submodels(self, brand_ids=None, dataset_ids=None,
                           year=None, make_id=None, model_id=None):
        """
        Retrieves submodels data from SEMA API.

        :param brand_ids: brand IDs to on which to filter
        :type brand_ids: list
        :param dataset_ids: dataset IDs to on which to filter
        :type dataset_ids: list
        :param year: year on which to filter
        :type year: int
        :param make_id: make ID on which to filter
        :type make_id: int
        :param model_id: model ID on which to filter
        :type model_id: int

        :return: submodels data
        :rtype: list

        :raises Exception: parameter misuse and on general exception

        .. Topic:: **-Parameters-**

            Only one of `brand_ids` or `dataset_ids` allowed

        .. Topic:: **-Retries-**

            Retries on `ApiInvalidToken` exception
            (up to 2 times in 1 second delays)

            Retries on `ApiRateLimitExceeded` exception
            (up to 13 times in 5 second delays)

        **-Return Format-**
        ::
            ret = [
                {
                    "VehicleID": <int>,
                    "SubmodelID": <int>,
                    "SubmodelName": <str>
                },
                {...}
            ]

        """

        if brand_ids and dataset_ids:
            raise Exception("Only one of brand IDs or dataset IDs allowed")

        url = f'{self.base_url}/lookup/submodels'
        params = {
            'token': self.token,
            'aaia_brandids': brand_ids,
            'branddatasetids': dataset_ids,
            'year': year,
            'makeid': make_id,
            'modelid': model_id
        }

        try:
            response = requests.get(url=url, params=params)
            return self.get_json_body(response)['Submodels']
        except Exception:
            raise

    @retry(exceptions=ApiInvalidToken, tries=2)
    @retry(exceptions=ApiRateLimitExceeded, tries=13, delay=5)
    def retrieve_engines(self, brand_ids=None, dataset_ids=None,
                         year=None, make_id=None, model_id=None):
        """
        Retrieves engines data from SEMA API.

        :param brand_ids: brand IDs to on which to filter
        :type brand_ids: list
        :param dataset_ids: dataset IDs to on which to filter
        :type dataset_ids: list
        :param year: year on which to filter
        :type year: int
        :param make_id: make ID on which to filter
        :type make_id: int
        :param model_id: model ID on which to filter
        :type model_id: int

        :return: engines data
        :rtype: list

        :raises Exception: parameter misuse and on general exception

        .. Topic:: **-Parameters-**

            Only one of `brand_ids` or `dataset_ids` allowed

        .. Topic:: **-Retries-**

            Retries on `ApiInvalidToken` exception
            (up to 2 times in 1 second delays)

            Retries on `ApiRateLimitExceeded` exception
            (up to 13 times in 5 second delays)

        **-Return Format-**
        ::
            ret = [
                {
                    "VehicleID": <int>,
                    "Liter": <str>,
                    "CC": <str>,
                    "CID": <str>,
                    "Cylinders": <str>,
                    "BlockType": <str>,
                    "EngBoreIn": <str>,
                    "EngBoreMetric": <str>,
                    "EngStrokeIn": <str>,
                    "EngStrokeMetric": <str>,
                    "ValvesPerEngine": "<str>,
                    "AspirationName": <str>,
                    "CylinderHeadTypeName": <str>,
                    "FuelTypeName": <str>,
                    "IgnitionSystemTypeName": <str>,
                    "MfrName": <str>,
                    "HorsePower": <str>,
                    "KilowattPower": <str>,
                    "EngineDesignationName": <str>
                },
                {...}
            ]

        """

        if brand_ids and dataset_ids:
            raise Exception("Only one of brand IDs or dataset IDs allowed")

        url = f'{self.base_url}/lookup/engines'
        params = {
            'token': self.token,
            'aaia_brandids': brand_ids,
            'branddatasetids': dataset_ids,
            'year': year,
            'makeid': make_id,
            'modelid': model_id
        }

        try:
            response = requests.get(url=url, params=params)
            return self.get_json_body(response)['Engines']
        except Exception:
            raise

    @retry(exceptions=ApiInvalidToken, tries=2)
    @retry(exceptions=ApiRateLimitExceeded, tries=13, delay=5)
    def retrieve_vehicle_info(self, base_vehicle_id=None, vehicle_id=None):
        """
        Retrieves vehicle info data from SEMA API.

        :param base_vehicle_id: base vehicle ID to on which to filter
        :type base_vehicle_id: int
        :param vehicle_id: vehicle ID to on which to filter
        :type vehicle_id: int

        :return: vehicle info data
        :rtype: list

        :raises Exception: parameter misuse and on general exception

        .. Topic:: **-Parameters-**

            Either `base_vehicle_id` or `vehicle_id` required

            Only one of `base_vehicle_id` or `vehicle_id` allowed

        .. Topic:: **-Retries-**

            Retries on `ApiInvalidToken` exception
            (up to 2 times in 1 second delays)

            Retries on `ApiRateLimitExceeded` exception
            (up to 13 times in 5 second delays)

        **-Return Format-**
        ::
            ret = [
                {
                    "Year": <int>,
                    "Make": <str>,
                    "Model": <str>,
                    "Submodel": <str>,
                    "Region": <str>,
                    "Liter": <str>,
                    "Cylinders": <str>,
                    "BlockType": <str>,
                    "FuelDeliveryTypeName": <str>,
                    "FuelTypeName": <str>,
                    "EngineDestinationName": <str>,
                    "EngineVINName": <str>,
                    "ValvesPerEngine": <str>,
                    "CC": <str>,
                    "CID": <str>,
                    "EngineBoreInches": <str>,
                    "EngineBoreMetric": <str>,
                    "EngineStrokeInches": <str>,
                    "EngineStrokeMetric": <str>,
                    "FuelDeliverySubtypeName": <str>,
                    "FuelSystemControlTypeName": <str>,
                    "FuelSystemDesignName": <str>,
                    "AspirationName": <str>,
                    "CylinderHeadTypeName": <str>,
                    "IgnitionSystemTypeName": <str>,
                    "EngineVersion": <str>,
                    "HorsePower": <str>,
                    "KilowattPower": <str>,
                    "BodyTypeName": <str>,
                    "BodyNumberOfDoors": <str>,
                    "ManufactureBodyCodeName": <str>,
                    "BedTypeName": <str>,
                    "BedLengthInches": <str>,
                    "BedLengthMetric": <str>,
                    "BrakeSystemName": <str>,
                    "BrakeFrontTypeName": <str>,
                    "BrakeRearTypeName": <str>,
                    "BrakeABSName": <str>,
                    "DriveTypeName": <str>,
                    "FrontSpringTypeName": <str>,
                    "RearSpringTypeName": <str>,
                    "SteeringTypeName": <str>,
                    "SteeringSystemName": <str>,
                    "TransmissionTypeName": <str>,
                    "TranmissionNumSpeeds": <str>,
                    "TransmissionControlTypeName": <str>,
                    "TransmissionElectronicControlled": <str>,
                    "TransmissionManufacturerName": <str>,
                    "WheelbaseInches": <str>,
                    "WheelbaseMetric": <str>
                },
                {...}
            ]

        """

        if not (base_vehicle_id or vehicle_id):
            raise Exception("Base vehicle ID or vehicle ID required")

        if base_vehicle_id and vehicle_id:
            raise Exception(
                "Only one of base vehicle ID or vehicle ID allowed"
            )

        url = f'{self.base_url}/lookup/expandedvehicleinfo'
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

    @retry(exceptions=ApiInvalidToken, tries=2)
    @retry(exceptions=ApiRateLimitExceeded, tries=13, delay=5)
    def retrieve_categories(self, brand_ids=None, dataset_ids=None,
                            base_vehicle_ids=None, vehicle_ids=None,
                            year=None, make_name=None,
                            model_name=None, submodel_name=None):
        """
        Retrieves categories data from SEMA API.

        :param brand_ids: brand IDs to on which to filter
        :type brand_ids: list
        :param dataset_ids: dataset IDs to on which to filter
        :type dataset_ids: list
        :param base_vehicle_ids: base vehicle IDs to on which to filter
        :type base_vehicle_ids: list
        :param vehicle_ids: vehicle IDs to on which to filter
        :type vehicle_ids: list
        :param year: year on which to filter
        :type year: int
        :param make_name: make name on which to filter
        :type make_name: str
        :param model_name: model name on which to filter
        :type model_name: str
        :param submodel_name: submodel name on which to filter
        :type submodel_name: str

        :return: categories data
        :rtype: list

        :raises Exception: parameter misuse and on general exception

        .. Topic:: **-Parameters-**

            Either `brand_ids` or `dataset_ids` required

            Only one of `brand_ids` or `dataset_ids` allowed

            `year` requires `make_name` and `model_name`

            `make_name` requires `year` and `model_name`

            `model_name` requires `year` and `make_name`

            `submodel_name` requires `year`, `make_name`, and `model_name`

            Only one of `base_vehicle_ids`, `vehicle_ids`, or named
            year/make/model group allowed

        .. Topic:: **-Retries-**

            Retries on `ApiInvalidToken` exception
            (up to 2 times in 1 second delays)

            Retries on `ApiRateLimitExceeded` exception
            (up to 13 times in 5 second delays)

        **-Return Format-**
        ::
            ret = [
                {
                    "ParentId": <int>,
                    "CategoryId": <int>,
                    "Name": <str>,
                    "Categories": [
                        {
                            "ParentId": <int>,
                            "CategoryId": <int>,
                            "Name": <str>,
                            "Categories": [
                                {
                                    "ParentId": <int>,
                                    "CategoryId": <int>,
                                    "Name": <str>,
                                    "Categories": [...]
                                },
                                {...}
                            ]
                        },
                        {...}
                    ]
                },
                {...}
            ]

        """

        if not (brand_ids or dataset_ids):
            raise Exception("Brand IDs or dataset IDs required")

        if brand_ids and dataset_ids:
            raise Exception("Only one of brand IDs or dataset IDs allowed")

        if base_vehicle_ids and vehicle_ids:
            raise Exception(
                "Only one of base vehicle IDs or vehicle IDs allowed"
            )

        if ((year or make_name or model_name or submodel_name)
                and (not (year and make_name and model_name))):
            raise Exception(
                "Year, make name, model name, and submodel name "
                "must be used in a year/make/model group"
            )

        if ((base_vehicle_ids or vehicle_ids)
                and (year or make_name or model_name or submodel_name)):
            raise Exception(
                "Only one of base vehicle IDs, vehicle IDs, "
                "or named year/make/model group allowed"
            )

        url = f'{self.base_url}/lookup/categories'
        data = {
            'token': self.token,
            'aaia_brandids': brand_ids,
            'branddatasetids': dataset_ids,
            'baseVehicleIds': base_vehicle_ids,
            'vehicleIds': vehicle_ids,
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

    # X Products PIES update
    @retry(exceptions=ApiInvalidToken, tries=2)
    @retry(exceptions=ApiRateLimitExceeded, tries=13, delay=5)
    def retrieve_products_by_brand(self, brand_ids=None, dataset_ids=None,
                                   base_vehicle_ids=None, vehicle_ids=None,
                                   year=None, make_name=None,
                                   model_name=None, submodel_name=None,
                                   part_numbers=None, pies_segments=None):
        """
        Retrieves products by brand data from SEMA API.

        :param brand_ids: brand IDs to on which to filter
        :type brand_ids: list
        :param dataset_ids: dataset IDs to on which to filter
        :type dataset_ids: list
        :param base_vehicle_ids: base vehicle IDs to on which to filter
        :type base_vehicle_ids: list
        :param vehicle_ids: vehicle IDs to on which to filter
        :type vehicle_ids: list
        :param year: year on which to filter
        :type year: int
        :param make_name: make name on which to filter
        :type make_name: str
        :param model_name: model name on which to filter
        :type model_name: str
        :param submodel_name: submodel name on which to filter
        :type submodel_name: str
        :param part_numbers: part numbers on which to filter
        :type part_numbers: list
        :param pies_segments: pies segments to include or ['all']
        :type pies_segments: list

        :return: products data
        :rtype: list

        :raises Exception: parameter misuse and on general exception

        .. Topic:: **-Parameters-**

            Either `brand_ids` or `dataset_ids` required

            Only one of `brand_ids` or `dataset_ids` allowed

            `year` requires `make_name` and `model_name`

            `make_name` requires `year` and `model_name`

            `model_name` requires `year` and `make_name`

            `submodel_name` requires `year`, `make_name`, and `model_name`

            Only one of `base_vehicle_ids`, `vehicle_ids`, or named
            year/make/model group allowed

        .. Topic:: **-Retries-**

            Retries on `ApiInvalidToken` exception
            (up to 2 times in 1 second delays)

            Retries on `ApiRateLimitExceeded` exception
            (up to 13 times in 5 second delays)

        **-Return Format-**
        ::
            ret = [
                {
                    "ProductId": <int>,
                    "PartNumber": <str>,
                    "PiesAttributes": [
                        {
                            "PiesName": <str>,
                            "PiesSegment": <str>,
                            "Value": <str> or null
                        },
                        {...}
                    ]
                },
                {...}
            ]

        """

        if not (brand_ids or dataset_ids):
            raise Exception("Brand IDs or dataset IDs required")

        if brand_ids and dataset_ids:
            raise Exception("Only one of brand IDs or dataset IDs allowed")

        if base_vehicle_ids and vehicle_ids:
            raise Exception(
                "Only one of base vehicle IDs or vehicle IDs allowed"
            )

        if ((year or make_name or model_name or submodel_name)
                and (not (year and make_name and model_name))):
            raise Exception(
                "Year, make name, model name, and submodel name "
                "must be used in a year/make/model group"
            )

        if ((base_vehicle_ids or vehicle_ids)
                and (year or make_name or model_name or submodel_name)):
            raise Exception(
                "Only one of base vehicle IDs, vehicle IDs, "
                "or named year/make/model group allowed"
            )

        url = f'{self.base_url}/lookup/products'
        data = {
            'token': self.token,
            'aaia_brandids': brand_ids,
            'branddatasetids': dataset_ids,
            'baseVehicleIds': base_vehicle_ids,
            'vehicleIds': vehicle_ids,
            'Year': year,
            'MakeName': make_name,
            'ModelName': model_name,
            'SubmodelName': submodel_name,
            'partNumbers': part_numbers,
            'piesSegments': pies_segments
        }

        try:
            response = requests.post(url=url, json=data)
            return self.get_json_body(response)['Products']
        except Exception:
            raise

    @retry(exceptions=ApiInvalidToken, tries=2)
    @retry(exceptions=ApiRateLimitExceeded, tries=13, delay=5)
    def retrieve_products_by_category(self, category_id,
                                      include_child_categories=True,
                                      brand_ids=None, dataset_ids=None,
                                      base_vehicle_ids=None, vehicle_ids=None,
                                      year=None, make_name=None,
                                      model_name=None, submodel_name=None,
                                      part_numbers=None, pies_segments=None):
        """
        Retrieves products by category data from SEMA API.

        :param category_id: category ID on which to filter
        :type category_id: int
        :param include_child_categories: whether or not to include child
            category products
        :type include_child_categories: bool
        :param brand_ids: brand IDs to on which to filter
        :type brand_ids: list
        :param dataset_ids: dataset IDs to on which to filter
        :type dataset_ids: list
        :param base_vehicle_ids: base vehicle IDs to on which to filter
        :type base_vehicle_ids: list
        :param vehicle_ids: vehicle IDs to on which to filter
        :type vehicle_ids: list
        :param year: year on which to filter
        :type year: int
        :param make_name: make name on which to filter
        :type make_name: str
        :param model_name: model name on which to filter
        :type model_name: str
        :param submodel_name: submodel name on which to filter
        :type submodel_name: str
        :param part_numbers: part numbers on which to filter
        :type part_numbers: list
        :param pies_segments: pies segments to include or ['all']
        :type pies_segments: list

        :return: products data
        :rtype: list

        :raises Exception: parameter misuse and on general exception

        .. Topic:: **-Parameters-**

            Either `brand_ids` or `dataset_ids` required

            Only one of `brand_ids` or `dataset_ids` allowed

            `year` requires `make_name` and `model_name`

            `make_name` requires `year` and `model_name`

            `model_name` requires `year` and `make_name`

            `submodel_name` requires `year`, `make_name`, and `model_name`

            Only one of `base_vehicle_ids`, `vehicle_ids`, or named
            year/make/model group allowed

        .. Topic:: **-Retries-**

            Retries on `ApiInvalidToken` exception
            (up to 2 times in 1 second delays)

            Retries on `ApiRateLimitExceeded` exception
            (up to 13 times in 5 second delays)

        **-Return Format-**
        ::
            ret = [
                {
                    "ProductId": <int>,
                    "PartNumber": <str>,
                    "PiesAttributes": [
                        {
                            "PiesName": <str>,
                            "PiesSegment": <str>,
                            "Value": <str> or null
                        },
                        {...}
                    ]
                },
                {...}
            ]

        """

        if not (brand_ids or dataset_ids):
            raise Exception("Brand IDs or dataset IDs required")

        if brand_ids and dataset_ids:
            raise Exception("Only one of brand IDs or dataset IDs allowed")

        if base_vehicle_ids and vehicle_ids:
            raise Exception(
                "Only one of base vehicle IDs or vehicle IDs allowed"
            )

        if ((year or make_name or model_name or submodel_name)
                and (not (year and make_name and model_name))):
            raise Exception(
                "Year, make name, model name, and submodel name "
                "must be used in a year/make/model group"
            )

        if ((base_vehicle_ids or vehicle_ids)
                and (year or make_name or model_name or submodel_name)):
            raise Exception(
                "Only one of base vehicle IDs, vehicle IDs, "
                "or named year/make/model group allowed"
            )

        url = f'{self.base_url}/lookup/productsbycategory'
        data = {
            'token': self.token,
            'CategoryId': category_id,
            'includeChildCategoryParts': (
                str(include_child_categories).lower()
                if include_child_categories else None
            ),
            'aaia_brandids': brand_ids,
            'branddatasetids': dataset_ids,
            'baseVehicleIds': base_vehicle_ids,
            'vehicleIds': vehicle_ids,
            'Year': year,
            'MakeName': make_name,
            'ModelName': model_name,
            'SubmodelName': submodel_name,
            'partNumbers': part_numbers,
            'piesSegments': pies_segments
        }

        try:
            response = requests.post(url=url, json=data)
            return self.get_json_body(response)['Products']
        except Exception:
            raise

    # X Product HTML update
    @retry(exceptions=ApiInvalidContentToken, tries=2)
    @retry(exceptions=ApiRateLimitExceeded, tries=13, delay=5)
    def retrieve_product_html(self, product_id, include_header_footer=False):
        """
        Retrieves product HTML data from SEMA API.

        :param product_id: product ID on which to filter
        :type product_id: int
        :param include_header_footer: whether or not to include header
            and footer
        :type include_header_footer: bool

        :return: product HTML
        :rtype: str

        :raises Exception: on general exception

        .. Topic:: **-Retries-**

            Retries on `ApiInvalidToken` exception
            (up to 2 times in 1 second delays)

            Retries on `ApiRateLimitExceeded` exception
            (up to 13 times in 5 second delays)

        """

        url = f'{self.base_url}/content/product'
        url += f'?contenttoken={self.content_token}'
        params = {
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

    @retry(exceptions=ApiInvalidToken, tries=2)
    @retry(exceptions=ApiRateLimitExceeded, tries=13, delay=5)
    def retrieve_vehicles_by_product(self, brand_id=None, dataset_id=None,
                                     part_numbers=None, group_by_part=True):
        """
        Retrieves vehicles by product data from SEMA API.

        :param brand_id: brand ID to on which to filter
        :type brand_id: str
        :param dataset_id: dataset ID to on which to filter
        :type dataset_id: int
        :param part_numbers: part numbers on which to filter
        :type part_numbers: list
        :param group_by_part: whether or not to group by part
        :type group_by_part: bool

        :return: vehicles data
        :rtype: list

        :raises Exception: parameter misuse and on general exception

        .. Topic:: **-Parameters-**

            Either `brand_id` or `dataset_id` required

            Only one of `brand_id` or `dataset_id` allowed

        .. Topic:: **-Retries-**

            Retries on `ApiInvalidToken` exception
            (up to 2 times in 1 second delays)

            Retries on `ApiRateLimitExceeded` exception
            (up to 13 times in 5 second delays)

        **-Return Format-**
        ::
            if group_by_part:
                ret = [
                    {
                        "PartNumber": <str>,
                        "Vehicles": [
                            {
                                "Year": <int>,
                                "MakeName": <str>,
                                "ModelName": <str>,
                                "SubmodelName": <str>
                            },
                            {...}
                        ]
                    },
                    {...}
                ]
            else:
                ret = [
                    {
                        "Year": <int>,
                        "MakeName": <str>,
                        "ModelName": <str>,
                        "SubmodelName": <str>
                    },
                    {...}
                ]

        """

        if not (brand_id or dataset_id):
            raise Exception("Brand ID or dataset ID required")

        if brand_id and dataset_id:
            raise Exception("Only one of brand ID or dataset ID allowed")

        url = f'{self.base_url}/lookup/vehiclesbyproduct'
        data = {
            'token': self.token,
            'aaia_brandid': brand_id,
            'branddatasetid': dataset_id,
            'partNumbers': part_numbers,
            'groupByPart': (
                str(group_by_part).lower()
                if group_by_part else None
            )
        }

        try:
            response = requests.post(url=url, json=data)
            if group_by_part:
                return self.get_json_body(response)['Parts']
            else:
                return self.get_json_body(response)['Vehicles']
        except Exception:
            raise

    @retry(exceptions=ApiInvalidToken, tries=2)
    @retry(exceptions=ApiRateLimitExceeded, tries=13, delay=5)
    def retrieve_vehicles_by_brand(self, brand_ids=None, dataset_ids=None):
        """
        Retrieves vehicles by brand data from SEMA API.

        :param brand_ids: brand IDs to on which to filter
        :type brand_ids: list
        :param dataset_ids: dataset IDs to on which to filter
        :type dataset_ids: list

        :return: vehicles data
        :rtype: list

        :raises Exception: parameter misuse and on general exception

        .. Topic:: **-Parameters-**

            Either `brand_ids` or `dataset_ids` required

            Only one of `brand_ids` or `dataset_ids` allowed

        .. Topic:: **-Retries-**

            Retries on `ApiInvalidToken` exception
            (up to 2 times in 1 second delays)

            Retries on `ApiRateLimitExceeded` exception
            (up to 13 times in 5 second delays)

        **-Return Format-**
        ::
            ret = [
                {
                    "AAIA_BrandID": <str>,
                    "BrandName": <str>,
                    "Year": <int>,
                    "MakeName": <str>,
                    "ModelName": <str>,
                    "SubmodelName": <str>
                },
                {...}
            ]

        """

        if not (brand_ids or dataset_ids):
            raise Exception("Brand IDs or dataset IDs required")

        if brand_ids and dataset_ids:
            raise Exception("Only one of brand IDs or dataset IDs allowed")

        url = f'{self.base_url}/lookup/vehiclesbybrand'
        data = {
            'token': self.token,
            'aaia_brandids': brand_ids,
            'branddatasetids': dataset_ids
        }

        try:
            response = requests.post(url=url, json=data)
            return self.get_json_body(response)['BrandVehicles']
        except Exception:
            raise


sema_client = SemaApiClient()
