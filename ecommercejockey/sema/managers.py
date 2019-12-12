"""
This module defines all managers and querysets for the SEMA app.

"""


from collections import defaultdict
from random import randint

from django.core.exceptions import MultipleObjectsReturned
from django.db.models import (
    Manager,
    QuerySet,
    Count,
    F,
    Q,
    ManyToManyField
)
from django.db.models.functions import Floor

from .clients import sema_client


class SemaBaseQuerySet(QuerySet):
    """
    This base queryset class defines base attributes for SEMA querysets.

    """

    # <editor-fold desc="unauthorize properties ...">
    def unauthorize(self):
        """
        Marks objects as unauthorized.

        :return: info, success, and/or error messages
        :rtype: list

        """

        msgs = []
        for obj in self:
            try:
                msgs.append(obj.unauthorize())
            except Exception as err:
                msgs.append(self.model.get_class_error_msg(str(err)))
        return msgs
    # </editor-fold>


class SemaBrandQuerySet(SemaBaseQuerySet):
    """
    This queryset class defines SEMA brand queryset methods.

    """

    def with_admin_data(self):
        return self.prefetch_related(
            'datasets',
        ).annotate(
            _dataset_count=Count(
                'datasets',
                distinct=True
            ),
            _dataset_relevant_count=Count(
                'datasets',
                filter=Q(datasets__is_relevant=True),
                distinct=True
            )
        )

    # <editor-fold desc="retrieve properties ...">
    def retrieve_years_data_from_api(self, annotated=False):
        """
        Retrieves brands years data from SEMA API.

        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: brands years data
        :rtype: list

        :raises Exception: on general exception

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_id_": <str>,
                        "years_": [
                            <int>,
                            ...
                        ]
                    }
                ]
            else:
                ret = [
                    <int>,
                    ...
                ]

        """

        try:
            if annotated:
                data = []
                for brand in self:
                    data += brand.retrieve_years_data_from_api(
                        annotated=annotated
                    )
            else:
                data = sema_client.retrieve_years(
                    brand_ids=[brand.brand_id for brand in self]
                )
            return data
        except Exception:
            raise

    def retrieve_makes_data_from_api(self, year=None, annotated=False):
        """
        Retrieves brands makes data from SEMA API.

        :param year: year on which to filter
        :type year: int
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: brands makes data
        :rtype: list

        :raises Exception: on general exception

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_id_": <str>,
                        "year_": <int>, (if defined)
                        "makes_": [
                            {
                                "MakeID": <int>,
                                "MakeName": <str>
                            },
                            {...}
                        ]
                    }
                ]
            else:
                ret = [
                    {
                        "MakeID": <int>,
                        "MakeName": <str>
                    },
                    {...}
            ]

        """

        try:
            if annotated:
                data = []
                for brand in self:
                    data += brand.retrieve_makes_data_from_api(
                        year=year,
                        annotated=annotated
                    )
            else:
                data = sema_client.retrieve_makes(
                    brand_ids=[brand.brand_id for brand in self],
                    year=year
                )
            return data
        except Exception:
            raise

    def retrieve_models_data_from_api(self, year=None,
                                      make_id=None, annotated=False):
        """
        Retrieves brands models data from SEMA API.

        :param year: year on which to filter
        :type year: int
        :param make_id: make ID on which to filter
        :type make_id: int
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: brands models data
        :rtype: list

        :raises Exception: on general exception

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_id_": <str>,
                        "year_": <int>, (if defined)
                        "make_id_": <int>, (if defined)
                        "models_": [
                            {
                                "BaseVehicleID": <int>,
                                "ModelID": <int>,
                                "ModelName": <str>
                            },
                            {...}
                        ]
                    }
                ]
            else:
                ret = [
                    {
                        "BaseVehicleID": <int>,
                        "ModelID": <int>,
                        "ModelName": <str>
                    },
                    {...}
            ]

        """

        try:
            if annotated:
                data = []
                for brand in self:
                    data += brand.retrieve_models_data_from_api(
                        year=year,
                        make_id=make_id,
                        annotated=annotated
                    )
            else:
                data = sema_client.retrieve_models(
                    brand_ids=[brand.brand_id for brand in self],
                    year=year,
                    make_id=make_id
                )
            return data
        except Exception:
            raise

    def retrieve_submodels_data_from_api(self, year=None, make_id=None,
                                         model_id=None, annotated=False):
        """
        Retrieves brands submodels data from SEMA API.

        :param year: year on which to filter
        :type year: int
        :param make_id: make ID on which to filter
        :type make_id: int
        :param model_id: model ID on which to filter
        :type model_id: int
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: brands submodels data
        :rtype: list

        :raises Exception: on general exception

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_id_": <str>,
                        "year_": <int>, (if defined)
                        "make_id_": <int>, (if defined)
                        "model_id_": <int>, (if defined)
                        "submodels_": [
                            {
                                "VehicleID": <int>,
                                "SubmodelID": <int>,
                                "SubmodelName": <str>
                            },
                            {...}
                        ]
                    }
                ]
            else:
                ret = [
                    {
                        "VehicleID": <int>,
                        "SubmodelID": <int>,
                        "SubmodelName": <str>
                    },
                    {...}
            ]

        """

        try:
            if annotated:
                data = []
                for brand in self:
                    data += brand.retrieve_submodels_data_from_api(
                        year=year,
                        make_id=make_id,
                        model_id=model_id,
                        annotated=annotated
                    )
            else:
                data = sema_client.retrieve_submodels(
                    brand_ids=[brand.brand_id for brand in self],
                    year=year,
                    make_id=make_id,
                    model_id=model_id
                )
            return data
        except Exception:
            raise

    def retrieve_engines_data_from_api(self, year=None, make_id=None,
                                       model_id=None, annotated=False):
        """
        Retrieves brands engines data from SEMA API.

        :param year: year on which to filter
        :type year: int
        :param make_id: make ID on which to filter
        :type make_id: int
        :param model_id: model ID on which to filter
        :type model_id: int
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: brands engines data
        :rtype: list

        :raises Exception: on general exception

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_id_": <str>,
                        "year_": <int>, (if defined)
                        "make_id_": <int>, (if defined)
                        "model_id_": <int>, (if defined)
                        "engines_": [
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
                    },
                    {...}
                ]
            else:
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

        try:
            if annotated:
                data = []
                for brand in self:
                    data += brand.retrieve_engines_data_from_api(
                        year=year,
                        make_id=make_id,
                        model_id=model_id,
                        annotated=annotated
                    )
            else:
                data = sema_client.retrieve_engines(
                    brand_ids=[brand.brand_id for brand in self],
                    year=year,
                    make_id=make_id,
                    model_id=model_id
                )
            return data
        except Exception:
            raise

    def retrieve_categories_data_from_api(self, base_vehicle_ids=None,
                                          vehicle_ids=None, year=None,
                                          make_name=None, model_name=None,
                                          submodel_name=None, annotated=False):
        """
        Retrieves brands categories data from SEMA API.

        :param base_vehicle_ids: base vehicle IDs on which to filter
        :type base_vehicle_ids: list
        :param vehicle_ids: vehicle IDs on which to filter
        :type vehicle_ids: list
        :param year: year on which to filter
        :type year: int
        :param make_name: make name on which to filter
        :type make_name: str
        :param model_name: model name on which to filter
        :type model_name: str
        :param submodel_name: submodel name on which to filter
        :type submodel_name: str
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: brands categories data
        :rtype: list

        :raises Exception: on general exception

        .. Topic:: **-Parameters-**

            `year` requires `make_name` and `model_name`

            `make_name` requires `year` and `model_name`

            `model_name` requires `year` and `make_name`

            `submodel_name` requires `year`, `make_name`, and `model_name`

            Only one of `base_vehicle_ids`, `vehicle_ids`, or named
            year/make/model group allowed

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_id_": <str>,
                        "base_vehicle_ids_": <list>, (if defined)
                        "vehicle_ids_": <list>, (if defined)
                        "year_": <int>, (if defined)
                        "make_name_": <str>, (if defined)
                        "model_name_": <str>, (if defined)
                        "submodel_name_": <str>, (if defined)
                        "categories_": [
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
                    }
                ]
            else:
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

        try:
            if annotated:
                data = []
                for brand in self:
                    data += brand.retrieve_categories_data_from_api(
                        base_vehicle_ids=base_vehicle_ids,
                        vehicle_ids=vehicle_ids,
                        year=year,
                        make_name=make_name,
                        model_name=model_name,
                        submodel_name=submodel_name,
                        annotated=annotated
                    )
            else:
                data = sema_client.retrieve_categories(
                    brand_ids=[brand.brand_id for brand in self],
                    base_vehicle_ids=base_vehicle_ids,
                    vehicle_ids=vehicle_ids,
                    year=year,
                    make_name=make_name,
                    model_name=model_name,
                    submodel_name=submodel_name
                )
            return data
        except Exception:
            raise

    def retrieve_products_by_brand_data_from_api(self, base_vehicle_ids=None,
                                                 vehicle_ids=None, year=None,
                                                 make_name=None,
                                                 model_name=None,
                                                 submodel_name=None,
                                                 part_numbers=None,
                                                 pies_segments=None,
                                                 annotated=False):
        """
        Retrieves brands products data from SEMA API.

        :param base_vehicle_ids: base vehicles IDs on which to filter
        :type base_vehicle_ids: list
        :param vehicle_ids: vehicle IDs on which to filter
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
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: brands products data
        :rtype: list

        :raises Exception: on general exception

        .. Topic:: **-Parameters-**

            `year` requires `make_name` and `model_name`

            `make_name` requires `year` and `model_name`

            `model_name` requires `year` and `make_name`

            `submodel_name` requires `year`, `make_name`, and `model_name`

            Only one of `base_vehicle_ids`, `vehicle_ids`, or named
            year/make/model group allowed

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_id_": <str>,
                        "base_vehicle_ids_": <list>, (if defined)
                        "vehicle_ids_": <list>, (if defined)
                        "year_": <int>, (if defined)
                        "make_name_": <str>, (if defined)
                        "model_name_": <str>, (if defined)
                        "submodel_name_": <str>, (if defined)
                        "part_numbers_": <list>, (if defined)
                        "products_": [
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
                    }
                ]
            else:
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

        try:
            if annotated:
                data = []
                for brand in self:
                    data += brand.retrieve_products_by_brand_data_from_api(
                        base_vehicle_ids=base_vehicle_ids,
                        vehicle_ids=vehicle_ids,
                        year=year,
                        make_name=make_name,
                        model_name=model_name,
                        submodel_name=submodel_name,
                        part_numbers=part_numbers,
                        pies_segments=pies_segments,
                        annotated=annotated
                    )
            else:
                data = sema_client.retrieve_products_by_brand(
                    brand_ids=[brand.brand_id for brand in self],
                    base_vehicle_ids=base_vehicle_ids,
                    vehicle_ids=vehicle_ids,
                    year=year,
                    make_name=make_name,
                    model_name=model_name,
                    submodel_name=submodel_name,
                    part_numbers=part_numbers,
                    pies_segments=pies_segments
                )
            return data
        except Exception:
            raise

    def retrieve_products_by_category_data_from_api(self, category_id,
                                                    base_vehicle_ids=None,
                                                    vehicle_ids=None,
                                                    year=None, make_name=None,
                                                    model_name=None,
                                                    submodel_name=None,
                                                    part_numbers=None,
                                                    pies_segments=None,
                                                    annotated=False):
        """
        Retrieves brands products by category data from SEMA API.

        :param category_id: category ID on which to filter
        :type category_id: int
        :param base_vehicle_ids: base vehicles IDs on which to filter
        :type base_vehicle_ids: list
        :param vehicle_ids: vehicle IDs on which to filter
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
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: brands products by category data
        :rtype: list

        :raises Exception: on general exception

        .. Topic:: **-Parameters-**

            `year` requires `make_name` and `model_name`

            `make_name` requires `year` and `model_name`

            `model_name` requires `year` and `make_name`

            `submodel_name` requires `year`, `make_name`, and `model_name`

            Only one of `base_vehicle_ids`, `vehicle_ids`, or named
            year/make/model group allowed

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_id_": <str>,
                        "category_id_": <int>,
                        "base_vehicle_ids_": <list>, (if defined)
                        "vehicle_ids_": <list>, (if defined)
                        "year_": <int>, (if defined)
                        "make_name_": <str>, (if defined)
                        "model_name_": <str>, (if defined)
                        "submodel_name_": <str>, (if defined)
                        "part_numbers_": <list>, (if defined)
                        "products_": [
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
                    },
                    {...}
                ]
            else:
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

        try:
            if annotated:
                data = []
                for brand in self:
                    data += brand.retrieve_products_by_category_data_from_api(
                        category_id=category_id,
                        base_vehicle_ids=base_vehicle_ids,
                        vehicle_ids=vehicle_ids,
                        year=year,
                        make_name=make_name,
                        model_name=model_name,
                        submodel_name=submodel_name,
                        part_numbers=part_numbers,
                        pies_segments=pies_segments,
                        annotated=annotated
                    )
            else:
                data = sema_client.retrieve_products_by_category(
                    category_id=category_id,
                    brand_ids=[brand.brand_id for brand in self],
                    base_vehicle_ids=base_vehicle_ids,
                    vehicle_ids=vehicle_ids,
                    year=year,
                    make_name=make_name,
                    model_name=model_name,
                    submodel_name=submodel_name,
                    part_numbers=part_numbers,
                    pies_segments=pies_segments
                )
            return data
        except Exception:
            raise

    def retrieve_vehicles_by_product_data_from_api(self, part_numbers=None,
                                                   annotated=False):
        """
        Retrieves brands vehicles by product data from SEMA API.

        :param part_numbers: part numbers on which to filter
        :type part_numbers: list
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: brands vehicles by product data
        :rtype: list

        :raises Exception: on general exception

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_id_": <str>,
                        "part_numbers_": <list>, (if defined)
                        "products_": [
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
                    }
                ]
            else:
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

        """

        try:
            data = []
            for brand in self:
                data += brand.retrieve_vehicles_by_product_data_from_api(
                    part_numbers=part_numbers,
                    annotated=annotated
                )
            return data
        except Exception:
            raise

    def retrieve_vehicles_by_brand_data_from_api(self, annotated=False):
        """
        Retrieves vehicles by brand data from SEMA API.

        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: vehicles by brand data
        :rtype: list

        :raises Exception: on general exception

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_id_": <str>,
                        "vehicles_": [
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
                    },
                    {...}
                ]
            else:
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

        try:
            if annotated:
                data = []
                for brand in self:
                    data += brand.retrieve_vehicles_by_brand_data_from_api(
                        annotated=annotated
                    )
            else:
                data = sema_client.retrieve_vehicles_by_brand(
                    brand_ids=[brand.brand_id for brand in self]
                )
            return data
        except Exception:
            raise
    # </editor-fold>


class SemaDatasetQuerySet(SemaBaseQuerySet):
    """
    This queryset class defines SEMA dataset queryset methods.

    """

    def with_admin_data(self):
        return self.select_related(
            'brand'
        ).prefetch_related(
            'categories',
            'vehicles',
            'products'
        ).annotate(
            _category_count=Count(
                'categories',
                distinct=True
            ),
            _category_relevant_count=Count(
                'categories',
                filter=Q(categories__is_relevant=True),
                distinct=True
            ),
            _vehicle_count=Count(
                'vehicles',
                distinct=True
            ),
            _vehicle_relevant_count=Count(
                'vehicles',
                filter=Q(vehicles__is_relevant=True),
                distinct=True
            ),
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

    # <editor-fold desc="retrieve properties ...">
    def retrieve_years_data_from_api(self, annotated=False):
        """
        Retrieves datasets years data from SEMA API.

        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: datasets years data
        :rtype: list

        :raises Exception: on general exception

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_id_": <str>,
                        "dataset_id_": <int>,
                        "years_": [
                            <int>,
                            ...
                        ]
                    }
                ]
            else:
                ret = [
                    <int>,
                    ...
                ]

        """

        try:
            if annotated:
                data = []
                for dataset in self:
                    data += dataset.retrieve_years_data_from_api(
                        annotated=annotated
                    )
            else:
                data = sema_client.retrieve_years(
                    dataset_ids=[dataset.dataset_id for dataset in self]
                )
            return data
        except Exception:
            raise

    def retrieve_makes_data_from_api(self, year=None, annotated=False):
        """
        Retrieves datasets makes data from SEMA API.

        :param year: year on which to filter
        :type year: int
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: datasets makes data
        :rtype: list

        :raises Exception: on general exception

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_id_": <str>,
                        "dataset_id_": <int>,
                        "year_": <int>, (if defined)
                        "makes_": [
                            {
                                "MakeID": <int>,
                                "MakeName": <str>
                            },
                            {...}
                        ]
                    }
                ]
            else:
                ret = [
                    {
                        "MakeID": <int>,
                        "MakeName": <str>
                    },
                    {...}
            ]

        """

        try:
            if annotated:
                data = []
                for dataset in self:
                    data += dataset.retrieve_makes_data_from_api(
                        year=year,
                        annotated=annotated
                    )
            else:
                data = sema_client.retrieve_makes(
                    dataset_ids=[dataset.dataset_id for dataset in self],
                    year=year
                )
            return data
        except Exception:
            raise

    def retrieve_models_data_from_api(self, year=None,
                                      make_id=None, annotated=False):
        """
        Retrieves datasets models data from SEMA API.

        :param year: year on which to filter
        :type year: int
        :param make_id: make ID on which to filter
        :type make_id: int
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: datasets models data
        :rtype: list

        :raises Exception: on general exception

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_id_": <str>,
                        "dataset_id_": <int>,
                        "year_": <int>, (if defined)
                        "make_id_": <int>, (if defined)
                        "models_": [
                            {
                                "BaseVehicleID": <int>,
                                "ModelID": <int>,
                                "ModelName": <str>
                            },
                            {...}
                        ]
                    }
                ]
            else:
                ret = [
                    {
                        "BaseVehicleID": <int>,
                        "ModelID": <int>,
                        "ModelName": <str>
                    },
                    {...}
            ]

        """

        try:
            if annotated:
                data = []
                for dataset in self:
                    data += dataset.retrieve_models_data_from_api(
                        year=year,
                        make_id=make_id,
                        annotated=annotated
                    )
            else:
                data = sema_client.retrieve_models(
                    dataset_ids=[dataset.dataset_id for dataset in self],
                    year=year,
                    make_id=make_id
                )
            return data
        except Exception:
            raise

    def retrieve_submodels_data_from_api(self, year=None, make_id=None,
                                         model_id=None, annotated=False):
        """
        Retrieves datasets submodels data from SEMA API.

        :param year: year on which to filter
        :type year: int
        :param make_id: make ID on which to filter
        :type make_id: int
        :param model_id: model ID on which to filter
        :type model_id: int
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: datasets submodels data
        :rtype: list

        :raises Exception: on general exception

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_id_": <str>,
                        "dataset_id_": <int>,
                        "year_": <int>, (if defined)
                        "make_id_": <int>, (if defined)
                        "model_id_": <int>, (if defined)
                        "submodels_": [
                            {
                                "VehicleID": <int>,
                                "SubmodelID": <int>,
                                "SubmodelName": <str>
                            },
                            {...}
                        ]
                    }
                ]
            else:
                ret = [
                    {
                        "VehicleID": <int>,
                        "SubmodelID": <int>,
                        "SubmodelName": <str>
                    },
                    {...}
            ]

        """

        try:
            if annotated:
                data = []
                for dataset in self:
                    data += dataset.retrieve_submodels_data_from_api(
                        year=year,
                        make_id=make_id,
                        model_id=model_id,
                        annotated=annotated
                    )
            else:
                data = sema_client.retrieve_submodels(
                    dataset_ids=[dataset.dataset_id for dataset in self],
                    year=year,
                    make_id=make_id,
                    model_id=model_id
                )
            return data
        except Exception:
            raise

    def retrieve_engines_data_from_api(self, year=None, make_id=None,
                                       model_id=None, annotated=False):
        """
        Retrieves datasets engines data from SEMA API.

        :param year: year on which to filter
        :type year: int
        :param make_id: make ID on which to filter
        :type make_id: int
        :param model_id: model ID on which to filter
        :type model_id: int
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: datasets engines data
        :rtype: list

        :raises Exception: on general exception

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_id_": <str>,
                        "dataset_id_": <int>,
                        "year_": <int>, (if defined)
                        "make_id_": <int>, (if defined)
                        "model_id_": <int>, (if defined)
                        "engines_": [
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
                    },
                    {...}
                ]
            else:
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

        try:
            if annotated:
                data = []
                for dataset in self:
                    data += dataset.retrieve_engines_data_from_api(
                        year=year,
                        make_id=make_id,
                        model_id=model_id,
                        annotated=annotated
                    )
            else:
                data = sema_client.retrieve_engines(
                    dataset_ids=[dataset.dataset_id for dataset in self],
                    year=year,
                    make_id=make_id,
                    model_id=model_id
                )
            return data
        except Exception:
            raise

    def retrieve_categories_data_from_api(self, base_vehicle_ids=None,
                                          vehicle_ids=None, year=None,
                                          make_name=None, model_name=None,
                                          submodel_name=None, annotated=False):
        """
        Retrieves datasets categories data from SEMA API.

        :param base_vehicle_ids: base vehicle IDs on which to filter
        :type base_vehicle_ids: list
        :param vehicle_ids: vehicle IDs on which to filter
        :type vehicle_ids: list
        :param year: year on which to filter
        :type year: int
        :param make_name: make name on which to filter
        :type make_name: str
        :param model_name: model name on which to filter
        :type model_name: str
        :param submodel_name: submodel name on which to filter
        :type submodel_name: str
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: datasets categories data
        :rtype: list

        :raises Exception: on general exception

        .. Topic:: **-Parameters-**

            `year` requires `make_name` and `model_name`

            `make_name` requires `year` and `model_name`

            `model_name` requires `year` and `make_name`

            `submodel_name` requires `year`, `make_name`, and `model_name`

            Only one of `base_vehicle_ids`, `vehicle_ids`, or named
            year/make/model group allowed

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_id_": <str>,
                        "dataset_id_": <int>,
                        "base_vehicle_ids_": <list>, (if defined)
                        "vehicle_ids_": <list>, (if defined)
                        "year_": <int>, (if defined)
                        "make_name_": <str>, (if defined)
                        "model_name_": <str>, (if defined)
                        "submodel_name_": <str>, (if defined)
                        "categories_": [
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
                    }
                ]
            else:
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

        try:
            if annotated:
                data = []
                for dataset in self:
                    data += dataset.retrieve_categories_data_from_api(
                        base_vehicle_ids=base_vehicle_ids,
                        vehicle_ids=vehicle_ids,
                        year=year,
                        make_name=make_name,
                        model_name=model_name,
                        submodel_name=submodel_name,
                        annotated=annotated
                    )
            else:
                data = sema_client.retrieve_categories(
                    dataset_ids=[dataset.dataset_id for dataset in self],
                    base_vehicle_ids=base_vehicle_ids,
                    vehicle_ids=vehicle_ids,
                    year=year,
                    make_name=make_name,
                    model_name=model_name,
                    submodel_name=submodel_name
                )
            return data
        except Exception:
            raise

    def retrieve_products_by_brand_data_from_api(self, base_vehicle_ids=None,
                                                 vehicle_ids=None, year=None,
                                                 make_name=None,
                                                 model_name=None,
                                                 submodel_name=None,
                                                 part_numbers=None,
                                                 pies_segments=None,
                                                 annotated=False):
        """
        Retrieves datasets products data from SEMA API.

        :param base_vehicle_ids: base vehicles IDs on which to filter
        :type base_vehicle_ids: list
        :param vehicle_ids: vehicle IDs on which to filter
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
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: datasets products data
        :rtype: list

        :raises Exception: on general exception

        .. Topic:: **-Parameters-**

            `year` requires `make_name` and `model_name`

            `make_name` requires `year` and `model_name`

            `model_name` requires `year` and `make_name`

            `submodel_name` requires `year`, `make_name`, and `model_name`

            Only one of `base_vehicle_ids`, `vehicle_ids`, or named
            year/make/model group allowed

        .. Topic:: **-Parameters-**

            `year` requires `make_name` and `model_name`

            `make_name` requires `year` and `model_name`

            `model_name` requires `year` and `make_name`

            `submodel_name` requires `year`, `make_name`, and `model_name`

            Only one of `base_vehicle_ids`, `vehicle_ids`, or named
            year/make/model group allowed

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_id_": <str>,
                        "dataset_id_": <int>,
                        "base_vehicle_ids_": <list>, (if defined)
                        "vehicle_ids_": <list>, (if defined)
                        "year_": <int>, (if defined)
                        "make_name_": <str>, (if defined)
                        "model_name_": <str>, (if defined)
                        "submodel_name_": <str>, (if defined)
                        "part_numbers_": <list>, (if defined)
                        "products_": [
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
                    }
                ]
            else:
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

        try:
            if annotated:
                data = []
                for dataset in self:
                    data += dataset.retrieve_products_by_brand_data_from_api(
                        base_vehicle_ids=base_vehicle_ids,
                        vehicle_ids=vehicle_ids,
                        year=year,
                        make_name=make_name,
                        model_name=model_name,
                        submodel_name=submodel_name,
                        part_numbers=part_numbers,
                        pies_segments=pies_segments,
                        annotated=annotated
                    )
            else:
                data = sema_client.retrieve_products_by_brand(
                    dataset_ids=[dataset.dataset_id for dataset in self],
                    base_vehicle_ids=base_vehicle_ids,
                    vehicle_ids=vehicle_ids,
                    year=year,
                    make_name=make_name,
                    model_name=model_name,
                    submodel_name=submodel_name,
                    part_numbers=part_numbers,
                    pies_segments=pies_segments
                )
            return data
        except Exception:
            raise

    def retrieve_products_by_category_data_from_api(self, category_id,
                                                    base_vehicle_ids=None,
                                                    vehicle_ids=None,
                                                    year=None, make_name=None,
                                                    model_name=None,
                                                    submodel_name=None,
                                                    part_numbers=None,
                                                    pies_segments=None,
                                                    annotated=False):
        """
        Retrieves datasets products by category data from SEMA API.

        :param category_id: category ID on which to filter
        :type category_id: int
        :param base_vehicle_ids: base vehicles IDs on which to filter
        :type base_vehicle_ids: list
        :param vehicle_ids: vehicle IDs on which to filter
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
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: datasets products by category data
        :rtype: list

        :raises Exception: on general exception

        .. Topic:: **-Parameters-**

            `year` requires `make_name` and `model_name`

            `make_name` requires `year` and `model_name`

            `model_name` requires `year` and `make_name`

            `submodel_name` requires `year`, `make_name`, and `model_name`

            Only one of `base_vehicle_ids`, `vehicle_ids`, or named
            year/make/model group allowed

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_id_": <str>,
                        "dataset_id_": <int>,
                        "category_id_": <int>,
                        "base_vehicle_ids_": <list>, (if defined)
                        "vehicle_ids_": <list>, (if defined)
                        "year_": <int>, (if defined)
                        "make_name_": <str>, (if defined)
                        "model_name_": <str>, (if defined)
                        "submodel_name_": <str>, (if defined)
                        "part_numbers_": <list>, (if defined)
                        "products_": [
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
                    }
                ]
            else:
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

        try:
            if annotated:
                data = []
                for dataset in self:
                    data += dataset.retrieve_products_by_category_data_from_api(
                        category_id=category_id,
                        base_vehicle_ids=base_vehicle_ids,
                        vehicle_ids=vehicle_ids,
                        year=year,
                        make_name=make_name,
                        model_name=model_name,
                        submodel_name=submodel_name,
                        part_numbers=part_numbers,
                        pies_segments=pies_segments,
                        annotated=annotated
                    )
            else:
                data = sema_client.retrieve_products_by_category(
                    category_id=category_id,
                    dataset_ids=[dataset.dataset_id for dataset in self],
                    base_vehicle_ids=base_vehicle_ids,
                    vehicle_ids=vehicle_ids,
                    year=year,
                    make_name=make_name,
                    model_name=model_name,
                    submodel_name=submodel_name,
                    part_numbers=part_numbers,
                    pies_segments=pies_segments
                )
            return data
        except Exception:
            raise

    def retrieve_vehicles_by_product_data_from_api(self, part_numbers=None,
                                                   annotated=False):
        """
        Retrieves datasets vehicles by product data from SEMA API.

        :param part_numbers: part numbers on which to filter
        :type part_numbers: list
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: datasets vehicles by product data
        :rtype: list

        :raises Exception: on general exception

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_id_": <str>,
                        "dataset_id_": <int>,
                        "part_numbers_": <list>, (if defined)
                        "products_": [
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
                    },
                    {...}
                ]
            else:
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

        """

        try:
            data = []
            for dataset in self:
                data += dataset.retrieve_vehicles_by_product_data_from_api(
                    part_numbers=part_numbers,
                    annotated=annotated
                )
            return data
        except Exception:
            raise

    def retrieve_vehicles_by_brand_data_from_api(self, annotated=False):
        """
        Retrieves datasets vehicles by brand data from SEMA API.

        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: datasets vehicles by brand data
        :rtype: list

        :raises Exception: on general exception

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_id_": <str>,
                        "dataset_id_": <int>,
                        "vehicles_": [
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
                    },
                    {...}
                ]
            else:
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

        try:
            if annotated:
                data = []
                for dataset in self:
                    data += dataset.retrieve_vehicles_by_brand_data_from_api(
                        annotated=annotated
                    )
            else:
                data = sema_client.retrieve_vehicles_by_brand(
                    dataset_ids=[dataset.dataset_id for dataset in self]
                )
            return data
        except Exception:
            raise
    # </editor-fold>

    # <editor-fold desc="perform properties ...">
    def perform_dataset_categories_update_from_api(self, **filters):
        msgs = []
        for dataset in self:
            try:
                msgs += dataset.perform_dataset_categories_update_from_api(
                    **filters
                )
            except Exception as err:
                msgs.append(self.model.get_class_error_msg(str(err)))

        if not msgs:
            msgs.append(self.model.get_class_up_to_date_msg())
        return msgs

    def perform_dataset_vehicles_update_from_api(self):
        msgs = []
        for dataset in self:
            try:
                msgs += dataset.perform_dataset_vehicles_update_from_api()
            except Exception as err:
                msgs.append(self.model.get_class_error_msg(str(err)))

        if not msgs:
            msgs.append(self.model.get_class_up_to_date_msg())
        return msgs
    # </editor-fold>


class SemaYearQuerySet(SemaBaseQuerySet):
    """
    This queryset class defines SEMA vehicle year queryset methods.

    """

    def with_admin_data(self):
        return self.prefetch_related(
            'make_years'
        ).annotate(
            _make_year_count=Count(
                'make_years',
                distinct=True
            ),
            _make_year_relevant_count=Count(
                'make_years',
                filter=Q(make_years__is_relevant=True),
                distinct=True
            )
        )

    def with_year_data(self):
        """
        Annotates decade field to queryset.

        :return: annotated queryset
        :rtype: django.db.models.QuerySet

        """

        return self.annotate(
            decade=Floor(F('year') / 10) * 10
        )

    # <editor-fold desc="retrieve properties ...">
    def retrieve_makes_data_from_api(self, brand_ids=None,
                                     dataset_ids=None, annotated=False):
        """
        Retrieves years makes data from SEMA API.

        :param brand_ids: brand IDs on which to filter
        :type brand_ids: list
        :param dataset_ids: dataset IDs on which to filter
        :type dataset_ids: list
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: years makes data
        :rtype: list

        :raises Exception: on general exception

        .. Topic:: **-Parameters-**

            Only one of `brand_ids` or `dataset_ids` allowed

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_ids_": <str>, (if defined)
                        "dataset_ids_": <int>, (if defined)
                        "year_": <int>
                        "makes_": [
                            {
                                "MakeID": <int>,
                                "MakeName": <str>
                            },
                            {...}
                        ]
                    }
                ]
            else:
                ret = [
                    {
                        "MakeID": <int>,
                        "MakeName": <str>
                    },
                    {...}
            ]

        """

        try:
            data = []
            for year in self:
                data += year.retrieve_makes_data_from_api(
                    brand_ids=brand_ids,
                    dataset_ids=dataset_ids,
                    annotated=annotated
                )
            return data
        except Exception:
            raise

    def retrieve_models_data_from_api(self, brand_ids=None, dataset_ids=None,
                                      make_id=None, annotated=False):
        """
        Retrieves years models data from SEMA API.

        :param brand_ids: brand IDs on which to filter
        :type brand_ids: list
        :param dataset_ids: dataset IDs on which to filter
        :type dataset_ids: list
        :param make_id: make ID on which to filter
        :type make_id: int
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: years models data
        :rtype: list

        :raises Exception: on general exception

        .. Topic:: **-Parameters-**

            Only one of `brand_ids` or `dataset_ids` allowed

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_ids_": <list>, (if defined)
                        "dataset_ids_": <list>, (if defined)
                        "year_": <int>,
                        "make_id_": <int>, (if defined)
                        "models_": [
                            {
                                "BaseVehicleID": <int>,
                                "ModelID": <int>,
                                "ModelName": <str>
                            },
                            {...}
                        ]
                    }
                ]
            else:
                ret = [
                    {
                        "BaseVehicleID": <int>,
                        "ModelID": <int>,
                        "ModelName": <str>
                    },
                    {...}
            ]

        """

        try:
            data = []
            for year in self:
                data += year.retrieve_models_data_from_api(
                    brand_ids=brand_ids,
                    dataset_ids=dataset_ids,
                    make_id=make_id,
                    annotated=annotated
                )
            return data
        except Exception:
            raise

    def retrieve_submodels_data_from_api(self, brand_ids=None,
                                         dataset_ids=None, make_id=None,
                                         model_id=None, annotated=False):
        """
        Retrieves years submodels data from SEMA API.

        :param brand_ids: brand IDs on which to filter
        :type brand_ids: list
        :param dataset_ids: dataset IDs on which to filter
        :type dataset_ids: list
        :param make_id: make ID on which to filter
        :type make_id: int
        :param model_id: model ID on which to filter
        :type model_id: int
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: years submodels data
        :rtype: list

        :raises Exception: on general exception

        .. Topic:: **-Parameters-**

            Only one of `brand_ids` or `dataset_ids` allowed

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_ids_": <list>, (if defined)
                        "dataset_ids_": <list>, (if defined)
                        "year_": <int>,
                        "make_id_": <int>, (if defined)
                        "model_id_": <int>, (if defined)
                        "submodels_": [
                            {
                                "VehicleID": <int>,
                                "SubmodelID": <int>,
                                "SubmodelName": <str>
                            },
                            {...}
                        ]
                    }
                ]
            else:
                ret = [
                    {
                        "VehicleID": <int>,
                        "SubmodelID": <int>,
                        "SubmodelName": <str>
                    },
                    {...}
            ]

        """

        try:
            data = []
            for year in self:
                data += year.retrieve_submodels_data_from_api(
                    brand_ids=brand_ids,
                    dataset_ids=dataset_ids,
                    make_id=make_id,
                    model_id=model_id,
                    annotated=annotated
                )
            return data
        except Exception:
            raise

    def retrieve_engines_data_from_api(self, brand_ids=None, dataset_ids=None,
                                       make_id=None, model_id=None,
                                       annotated=False):
        """
        Retrieves years engines data from SEMA API.

        :param brand_ids: brand IDs on which to filter
        :type brand_ids: list
        :param dataset_ids: dataset IDs on which to filter
        :type dataset_ids: list
        :param make_id: make ID on which to filter
        :type make_id: int
        :param model_id: model ID on which to filter
        :type model_id: int
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: years engines data
        :rtype: list

        :raises Exception: on general exception

        .. Topic:: **-Parameters-**

            Only one of `brand_ids` or `dataset_ids` allowed

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_ids_": <list>, (if defined)
                        "dataset_ids_": <list>, (if defined)
                        "year_": <int>,
                        "make_id_": <int>, (if defined)
                        "model_id_": <int>, (if defined)
                        "engines_": [
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
                    },
                    {...}
                ]
            else:
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

        try:
            data = []
            for year in self:
                data += year.retrieve_engines_data_from_api(
                    brand_ids=brand_ids,
                    dataset_ids=dataset_ids,
                    make_id=make_id,
                    model_id=model_id,
                    annotated=annotated
                )
            return data
        except Exception:
            raise
    # </editor-fold>


class SemaMakeQuerySet(SemaBaseQuerySet):
    """
    This queryset class defines SEMA vehicle make queryset methods.

    """

    def with_admin_data(self):
        return self.prefetch_related(
            'make_years'
        ).annotate(
            _make_year_count=Count(
                'make_years',
                distinct=True
            ),
            _make_year_relevant_count=Count(
                'make_years',
                filter=Q(make_years__is_relevant=True),
                distinct=True
            )
        )

    # <editor-fold desc="retrieve properties ...">
    def retrieve_models_data_from_api(self, brand_ids=None, dataset_ids=None,
                                      year=None, annotated=False):
        """
        Retrieves makes models data from SEMA API.

        :param brand_ids: brand IDs on which to filter
        :type brand_ids: list
        :param dataset_ids: dataset IDs on which to filter
        :type dataset_ids: list
        :param year: year on which to filter
        :type year: int
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: makes models data
        :rtype: list

        :raises Exception: on general exception

        .. Topic:: **-Parameters-**

            Only one of `brand_ids` or `dataset_ids` allowed

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_ids_": <list>, (if defined)
                        "dataset_ids_": <list>, (if defined)
                        "year_": <int>, (if defined)
                        "make_id_": <int>,
                        "models_": [
                            {
                                "BaseVehicleID": <int>,
                                "ModelID": <int>,
                                "ModelName": <str>
                            },
                            {...}
                        ]
                    }
                ]
            else:
                ret = [
                    {
                        "BaseVehicleID": <int>,
                        "ModelID": <int>,
                        "ModelName": <str>
                    },
                    {...}
            ]

        """

        try:
            data = []
            for make in self:
                data += make.retrieve_models_data_from_api(
                    brand_ids=brand_ids,
                    dataset_ids=dataset_ids,
                    year=year,
                    annotated=annotated
                )
            return data
        except Exception:
            raise

    def retrieve_submodels_data_from_api(self, brand_ids=None,
                                         dataset_ids=None, year=None,
                                         model_id=None, annotated=False):
        """
        Retrieves makes submodels data from SEMA API.

        :param brand_ids: brand IDs on which to filter
        :type brand_ids: list
        :param dataset_ids: dataset IDs on which to filter
        :type dataset_ids: list
        :param year: year on which to filter
        :type year: int
        :param model_id: model ID on which to filter
        :type model_id: int
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: makes submodels data
        :rtype: list

        :raises Exception: on general exception

        .. Topic:: **-Parameters-**

            Only one of `brand_ids` or `dataset_ids` allowed

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_ids_": <list>, (if defined)
                        "dataset_ids_": <list>, (if defined)
                        "year_": <int>, (if defined)
                        "make_id_": <int>,
                        "model_id_": <int>, (if defined)
                        "submodels_": [
                            {
                                "VehicleID": <int>,
                                "SubmodelID": <int>,
                                "SubmodelName": <str>
                            },
                            {...}
                        ]
                    }
                ]
            else:
                ret = [
                    {
                        "VehicleID": <int>,
                        "SubmodelID": <int>,
                        "SubmodelName": <str>
                    },
                    {...}
            ]

        """

        try:
            data = []
            for make in self:
                data += make.retrieve_submodels_data_from_api(
                    brand_ids=brand_ids,
                    dataset_ids=dataset_ids,
                    year=year,
                    model_id=model_id,
                    annotated=annotated
                )
            return data
        except Exception:
            raise

    def retrieve_engines_data_from_api(self, brand_ids=None, dataset_ids=None,
                                       year=None, model_id=None,
                                       annotated=False):
        """
        Retrieves makes engines data from SEMA API.

        :param brand_ids: brand IDs on which to filter
        :type brand_ids: list
        :param dataset_ids: dataset IDs on which to filter
        :type dataset_ids: list
        :param year: year on which to filter
        :type year: int
        :param model_id: model ID on which to filter
        :type model_id: int
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: makes engines data
        :rtype: list

        :raises Exception: on general exception

        .. Topic:: **-Parameters-**

            Only one of `brand_ids` or `dataset_ids` allowed

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_ids_": <list>, (if defined)
                        "dataset_ids_": <list>, (if defined)
                        "year_": <int>, (if defined)
                        "make_id_": <int>,
                        "model_id_": <int>, (if defined)
                        "engines_": [
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
                    },
                    {...}
                ]
            else:
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

        try:
            data = []
            for make in self:
                data += make.retrieve_engines_data_from_api(
                    brand_ids=brand_ids,
                    dataset_ids=dataset_ids,
                    year=year,
                    model_id=model_id,
                    annotated=annotated
                )
            return data
        except Exception:
            raise
    # </editor-fold>


class SemaModelQuerySet(SemaBaseQuerySet):
    """
    This queryset class defines SEMA vehicle model queryset methods.

    """

    def with_admin_data(self):
        return self.prefetch_related(
            'base_vehicles'
        ).annotate(
            _base_vehicle_count=Count(
                'base_vehicles',
                distinct=True
            ),
            _base_vehicle_relevant_count=Count(
                'base_vehicles',
                filter=Q(base_vehicles__is_relevant=True),
                distinct=True
            )
        )

    # <editor-fold desc="retrieve properties ...">
    def retrieve_submodels_data_from_api(self, brand_ids=None,
                                         dataset_ids=None, year=None,
                                         make_id=None, annotated=False):
        """
        Retrieves models submodels data from SEMA API.

        :param brand_ids: brand IDs on which to filter
        :type brand_ids: list
        :param dataset_ids: dataset IDs on which to filter
        :type dataset_ids: list
        :param year: year on which to filter
        :type year: int
        :param make_id: make ID on which to filter
        :type make_id: int
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: models submodels data
        :rtype: list

        :raises Exception: on general exception

        .. Topic:: **-Parameters-**

            Only one of `brand_ids` or `dataset_ids` allowed

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_ids_": <list>, (if defined)
                        "dataset_ids_": <list>, (if defined)
                        "year_": <int>, (if defined)
                        "make_id_": <int>, (if defined)
                        "model_id_": <int>,
                        "submodels_": [
                            {
                                "VehicleID": <int>,
                                "SubmodelID": <int>,
                                "SubmodelName": <str>
                            },
                            {...}
                        ]
                    }
                ]
            else:
                ret = [
                    {
                        "VehicleID": <int>,
                        "SubmodelID": <int>,
                        "SubmodelName": <str>
                    },
                    {...}
            ]

        """

        try:
            data = []
            for model in self:
                data += model.retrieve_submodels_data_from_api(
                    brand_ids=brand_ids,
                    dataset_ids=dataset_ids,
                    year=year,
                    make_id=make_id,
                    annotated=annotated
                )
            return data
        except Exception:
            raise

    def retrieve_engines_data_from_api(self, brand_ids=None, dataset_ids=None,
                                       year=None, make_id=None,
                                       annotated=False):
        """
        Retrieves models engines data from SEMA API.

        :param brand_ids: brand IDs on which to filter
        :type brand_ids: list
        :param dataset_ids: dataset IDs on which to filter
        :type dataset_ids: list
        :param year: year on which to filter
        :type year: int
        :param make_id: make ID on which to filter
        :type make_id: int
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: models engines data
        :rtype: list

        :raises Exception: on general exception

        .. Topic:: **-Parameters-**

            Only one of `brand_ids` or `dataset_ids` allowed

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_ids_": <list>, (if defined)
                        "dataset_ids_": <list>, (if defined)
                        "year_": <int>, (if defined)
                        "make_id_": <int>, (if defined)
                        "model_id_": <int>,
                        "engines_": [
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
                    },
                    {...}
                ]
            else:
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

        try:
            data = []
            for model in self:
                data += model.retrieve_engines_data_from_api(
                    brand_ids=brand_ids,
                    dataset_ids=dataset_ids,
                    year=year,
                    make_id=make_id,
                    annotated=annotated
                )
            return data
        except Exception:
            raise
    # </editor-fold>


class SemaSubmodelQuerySet(SemaBaseQuerySet):
    """
    This queryset class defines SEMA vehicle submodel queryset methods.

    """

    def with_admin_data(self):
        return self.prefetch_related(
            'vehicles'
        ).annotate(
            _vehicle_count=Count(
                'vehicles',
                distinct=True
            ),
            _vehicle_relevant_count=Count(
                'vehicles',
                filter=Q(vehicles__is_relevant=True),
                distinct=True
            )
        )


class SemaMakeYearQuerySet(SemaBaseQuerySet):
    """
    This queryset class defines SEMA vehicle make year queryset methods.

    """

    def with_admin_data(self):
        return self.select_related(
            'year',
            'make'
        ).prefetch_related(
            'base_vehicles'
        ).annotate(
            _base_vehicle_count=Count(
                'base_vehicles',
                distinct=True
            ),
            _base_vehicle_relevant_count=Count(
                'base_vehicles',
                filter=Q(base_vehicles__is_relevant=True),
                distinct=True
            )
        )

    # <editor-fold desc="retrieve properties ...">
    def retrieve_models_data_from_api(self, brand_ids=None,
                                      dataset_ids=None, annotated=False):
        """
        Retrieves make years models data from SEMA API.

        :param brand_ids: brand IDs on which to filter
        :type brand_ids: list
        :param dataset_ids: dataset IDs on which to filter
        :type dataset_ids: list
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: make years models data
        :rtype: list

        :raises Exception: on general exception

        .. Topic:: **-Parameters-**

            Only one of `brand_ids` or `dataset_ids` allowed

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_ids_": <list>, (if defined)
                        "dataset_ids_": <list>, (if defined)
                        "make_year_id_" <int>,
                        "year_": <int>,
                        "make_id_": <int>,
                        "models_": [
                            {
                                "BaseVehicleID": <int>,
                                "ModelID": <int>,
                                "ModelName": <str>
                            },
                            {...}
                        ]
                    }
                ]
            else:
                ret = [
                    {
                        "BaseVehicleID": <int>,
                        "ModelID": <int>,
                        "ModelName": <str>
                    },
                    {...}
            ]

        """

        try:
            data = []
            for make_year in self:
                data += make_year.retrieve_models_data_from_api(
                    brand_ids=brand_ids,
                    dataset_ids=dataset_ids,
                    annotated=annotated
                )
            return data
        except Exception:
            raise

    def retrieve_submodels_data_from_api(self, brand_ids=None,
                                         dataset_ids=None, model_id=None,
                                         annotated=False):
        """
        Retrieves make years submodels data from SEMA API.

        :param brand_ids: brand IDs on which to filter
        :type brand_ids: list
        :param dataset_ids: dataset IDs on which to filter
        :type dataset_ids: list
        :param model_id: model ID on which to filter
        :type model_id: int
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: make years submodels data
        :rtype: list

        :raises Exception: on general exception

        .. Topic:: **-Parameters-**

            Only one of `brand_ids` or `dataset_ids` allowed

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_ids_": <list>, (if defined)
                        "dataset_ids_": <list>, (if defined)
                        "make_year_id_": <int>,
                        "year_": <int>,
                        "make_id_": <int>,
                        "model_id_": <int>, (if defined)
                        "submodels_": [
                            {
                                "VehicleID": <int>,
                                "SubmodelID": <int>,
                                "SubmodelName": <str>
                            },
                            {...}
                        ]
                    }
                ]
            else:
                ret = [
                    {
                        "VehicleID": <int>,
                        "SubmodelID": <int>,
                        "SubmodelName": <str>
                    },
                    {...}
            ]

        """

        try:
            data = []
            for make_year in self:
                data += make_year.retrieve_submodels_data_from_api(
                    brand_ids=brand_ids,
                    dataset_ids=dataset_ids,
                    model_id=model_id,
                    annotated=annotated
                )
            return data
        except Exception:
            raise

    def retrieve_engines_data_from_api(self, brand_ids=None, dataset_ids=None,
                                       model_id=None, annotated=False):
        """
        Retrieves make years engines data from SEMA API.

        :param brand_ids: brand IDs on which to filter
        :type brand_ids: list
        :param dataset_ids: dataset IDs on which to filter
        :type dataset_ids: list
        :param model_id: model ID on which to filter
        :type model_id: int
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: make years engines data
        :rtype: list

        :raises Exception: on general exception

        .. Topic:: **-Parameters-**

            Only one of `brand_ids` or `dataset_ids` allowed

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_ids_": <list>, (if defined)
                        "dataset_ids_": <list>, (if defined)
                        "make_year_id_": <int>,
                        "year_": <int>,
                        "make_id_": <int>,
                        "model_id_": <int>, (if defined)
                        "engines_": [
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
                    },
                    {...}
                ]
            else:
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

        try:
            data = []
            for make_year in self:
                data += make_year.retrieve_engines_data_from_api(
                    brand_ids=brand_ids,
                    dataset_ids=dataset_ids,
                    model_id=model_id,
                    annotated=annotated
                )
            return data
        except Exception:
            raise
    # </editor-fold>


class SemaBaseVehicleQuerySet(SemaBaseQuerySet):
    """
    This queryset class defines SEMA base vehicle queryset methods.

    """

    def with_admin_data(self):
        return self.select_related(
            'make_year',
            'model'
        ).prefetch_related(
            'vehicles'
        ).annotate(
            _vehicle_count=Count(
                'vehicles',
                distinct=True
            ),
            _vehicle_relevant_count=Count(
                'vehicles',
                filter=Q(vehicles__is_relevant=True),
                distinct=True
            )
        )

    # <editor-fold desc="retrieve properties ...">
    def retrieve_submodels_data_from_api(self, brand_ids=None,
                                         dataset_ids=None, annotated=False):
        """
        Retrieves base vehicles submodels data from SEMA API.

        :param brand_ids: brand IDs on which to filter
        :type brand_ids: list
        :param dataset_ids: dataset IDs on which to filter
        :type dataset_ids: list
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: base vehicles submodels data
        :rtype: list

        :raises Exception: on general exception

        .. Topic:: **-Parameters-**

            Only one of `brand_ids` or `dataset_ids` allowed

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_ids_": <list>, (if defined)
                        "dataset_ids_": <list>, (if defined)
                        "base_vehicle_id_": <int>,
                        "year_": <int>,
                        "make_id_": <int>,
                        "model_id_": <int>,
                        "submodels_": [
                            {
                                "VehicleID": <int>,
                                "SubmodelID": <int>,
                                "SubmodelName": <str>
                            },
                            {...}
                        ]
                    }
                ]
            else:
                ret = [
                    {
                        "VehicleID": <int>,
                        "SubmodelID": <int>,
                        "SubmodelName": <str>
                    },
                    {...}
            ]

        """

        try:
            data = []
            for base_vehicle in self:
                data += base_vehicle.retrieve_submodels_data_from_api(
                    brand_ids=brand_ids,
                    dataset_ids=dataset_ids,
                    annotated=annotated
                )
            return data
        except Exception:
            raise

    def retrieve_engines_data_from_api(self, brand_ids=None,
                                       dataset_ids=None, annotated=False):
        """
        Retrieves base vehicles engines data from SEMA API.

        :param brand_ids: brand IDs on which to filter
        :type brand_ids: list
        :param dataset_ids: dataset IDs on which to filter
        :type dataset_ids: list
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: base vehicles engines data
        :rtype: list

        :raises Exception: on general exception

        .. Topic:: **-Parameters-**

            Only one of `brand_ids` or `dataset_ids` allowed

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_ids_": <list>, (if defined)
                        "dataset_ids_": <list>, (if defined)
                        "base_vehicle_id_": <int>,
                        "year_": <int>,
                        "make_id_": <int>,
                        "model_id_": <int>,
                        "engines_": [
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
                    }
                ]
            else:
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

        try:
            data = []
            for base_vehicle in self:
                data += base_vehicle.retrieve_engines_data_from_api(
                    brand_ids=brand_ids,
                    dataset_ids=dataset_ids,
                    annotated=annotated
                )
            return data
        except Exception:
            raise

    def retrieve_vehicle_info_data_from_api(self, annotated=False):
        """
        Retrieves base vehicles vehicle info data from SEMA API.

        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: base vehicles vehicle info data
        :rtype: list

        :raises Exception: on general exception

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "base_vehicle_id_": <int>,
                        "vehicles_": [
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
                    },
                    {...}
                ]
            else:
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

        try:
            data = []
            for base_vehicle in self:
                data += base_vehicle.retrieve_vehicle_info_data_from_api(
                    annotated=annotated
                )
            return data
        except Exception:
            raise

    def retrieve_categories_data_from_api(self, brand_ids=None,
                                          dataset_ids=None, by_names=False,
                                          annotated=False):
        """
        Retrieves base vehicles categories data from SEMA API.

        :param brand_ids: brand IDs on which to filter
        :type brand_ids: list
        :param dataset_ids: dataset IDs on which to filter
        :type dataset_ids: list
        :param by_names: whether or not to filter by names rather than
            ID
        :type by_names: bool
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: base vehicles categories data
        :rtype: list

        :raises Exception: on general exception

        .. Topic:: **-Parameters-**

            Only one of `brand_ids` or `dataset_ids` allowed

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_ids_": <list>, (if defined)
                        "dataset_ids_": <list>, (if defined)
                        "base_vehicle_id_": <int>,
                        "year_": <int>,
                        "make_id_": <int>,
                        "make_name_": <str>,
                        "model_id_": <int>,
                        "model_name_": <str>,
                        "categories_": [
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
                    }
                ]
            else:
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

        try:
            if not by_names and not annotated:
                data = sema_client.retrieve_categories(
                    brand_ids=brand_ids,
                    dataset_ids=dataset_ids,
                    base_vehicle_ids=[
                        base_vehicle.base_vehicle_id for base_vehicle in self
                    ]
                )
            else:
                data = []
                for base_vehicle in self:
                    data += base_vehicle.retrieve_categories_data_from_api(
                        brand_ids=brand_ids,
                        dataset_ids=dataset_ids,
                        by_names=by_names,
                        annotated=annotated
                    )
            return data
        except Exception:
            raise

    def retrieve_products_by_brand_data_from_api(self, brand_ids=None,
                                                 dataset_ids=None,
                                                 part_numbers=None,
                                                 pies_segments=None,
                                                 by_names=False,
                                                 annotated=False):
        """
        Retrieves base vehicles products by brand data from SEMA API.

        :param brand_ids: brand IDs on which to filter
        :type brand_ids: list
        :param dataset_ids: dataset IDs on which to filter
        :type dataset_ids: list
        :param part_numbers: part numbers on which to filter
        :type part_numbers: list
        :param pies_segments: pies segments to include or ['all']
        :type pies_segments: list
        :param by_names: whether or not to filter by names rather than
            ID
        :type by_names: bool
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: base vehicles products data
        :rtype: list

        :raises Exception: on general exception

        .. Topic:: **-Parameters-**

            Only one of `brand_ids` or `dataset_ids` allowed

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_ids_": <list>, (if defined)
                        "dataset_ids_": <list>, (if defined)
                        "base_vehicle_id_": <int>,
                        "year_": <int>,
                        "make_id_": <int>,
                        "make_name_": <str>,
                        "model_id_": <int>,
                        "model_name_": <str>,
                        "part_numbers_": <list>, (if defined)
                        "products_": [
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
                    }
                ]
            else:
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

        try:
            if not by_names and not annotated:
                data = sema_client.retrieve_products_by_brand(
                    brand_ids=brand_ids,
                    dataset_ids=dataset_ids,
                    part_numbers=part_numbers,
                    pies_segments=pies_segments,
                    base_vehicle_ids=[
                        base_vehicle.base_vehicle_id for base_vehicle in self
                    ]
                )
            else:
                data = []
                for base_vehicle in self:
                    data += base_vehicle.retrieve_products_by_brand_data_from_api(
                        brand_ids=brand_ids,
                        dataset_ids=dataset_ids,
                        part_numbers=part_numbers,
                        pies_segments=pies_segments,
                        by_names=by_names,
                        annotated=annotated
                    )
            return data
        except Exception:
            raise

    def retrieve_products_by_category_data_from_api(self, category_id,
                                                    brand_ids=None,
                                                    dataset_ids=None,
                                                    part_numbers=None,
                                                    pies_segments=None,
                                                    by_names=False,
                                                    annotated=False):
        """
        Retrieves base vehicles products by category data from SEMA API.

        :param category_id: category ID on which to filter
        :type category_id: int
        :param brand_ids: brand IDs on which to filter
        :type brand_ids: list
        :param dataset_ids: dataset IDs on which to filter
        :type dataset_ids: list
        :param part_numbers: part numbers on which to filter
        :type part_numbers: list
        :param pies_segments: pies segments to include or ['all']
        :type pies_segments: list
        :param by_names: whether or not to filter by names rather than
            ID
        :type by_names: bool
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: base vehicles products by category data
        :rtype: list

        :raises Exception: on general exception

        .. Topic:: **-Parameters-**

            Only one of `brand_ids` or `dataset_ids` allowed

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_ids_": <list>, (if defined)
                        "dataset_ids_": <list>, (if defined)
                        "base_vehicle_id_": <int>,
                        "year_": <int>,
                        "make_id_": <int>,
                        "make_name_": <str>,
                        "model_id_": <int>,
                        "model_name_": <str>,
                        "part_numbers_": <list>, (if defined)
                        "products_": [
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
                    },
                    {...}
                ]
            else:
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

        try:
            if not by_names and not annotated:
                data = sema_client.retrieve_products_by_category(
                    category_id=category_id,
                    brand_ids=brand_ids,
                    dataset_ids=dataset_ids,
                    base_vehicle_ids=[
                        base_vehicle.base_vehicle_id for base_vehicle in self
                    ],
                    part_numbers=part_numbers,
                    pies_segments=pies_segments,
                )
            else:
                data = []
                for base_vehicle in self:
                    data += base_vehicle.retrieve_products_by_category_data_from_api(
                        category_id=category_id,
                        brand_ids=brand_ids,
                        dataset_ids=dataset_ids,
                        part_numbers=part_numbers,
                        pies_segments=pies_segments,
                        by_names=by_names,
                        annotated=annotated
                    )
            return data
        except Exception:
            raise
    # </editor-fold>


class SemaVehicleQuerySet(SemaBaseQuerySet):
    """
    This queryset class defines SEMA vehicle queryset methods.

    """

    def with_admin_data(self):
        return self.select_related(
            'base_vehicle',
            'submodel'
        ).prefetch_related(
            'engines',
            'datasets',
            'products'
        ).annotate(
            _engine_count=Count(
                'engines',
                distinct=True
            ),
            _engine_relevant_count=Count(
                'engines',
                filter=Q(engines__is_relevant=True),
                distinct=True
            ),
            _dataset_count=Count(
                'datasets',
                distinct=True
            ),
            _dataset_relevant_count=Count(
                'datasets',
                filter=Q(datasets__is_relevant=True),
                distinct=True
            ),
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

    # <editor-fold desc="retrieve properties ...">
    def retrieve_vehicle_info_data_from_api(self, annotated=False):
        """
        Retrieves vehicles vehicle info data from SEMA API.

        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: vehicles vehicle info data
        :rtype: list

        :raises Exception: on general exception

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "base_vehicle_id_": <int>,
                        "vehicle_id_": <int>,
                        "vehicles_": [
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
                    },
                    {...}
                ]
            else:
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

        try:
            data = []
            for vehicle in self:
                data += vehicle.retrieve_vehicle_info_data_from_api(
                    annotated=annotated
                )
            return data
        except Exception:
            raise

    def retrieve_categories_data_from_api(self, brand_ids=None,
                                          dataset_ids=None, by_names=False,
                                          annotated=False):
        """
        Retrieves vehicles categories data from SEMA API.

        :param brand_ids: brand IDs on which to filter
        :type brand_ids: list
        :param dataset_ids: dataset IDs on which to filter
        :type dataset_ids: list
        :param by_names: whether or not to filter by names rather than
            ID
        :type by_names: bool
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: vehicles categories data
        :rtype: list

        :raises Exception: on general exception

        .. Topic:: **-Parameters-**

            Only one of `brand_ids` or `dataset_ids` allowed

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_ids_": <list>, (if defined)
                        "dataset_ids_": <list>, (if defined)
                        "base_vehicle_id_": <int>,
                        "vehicle_id_": <int>,
                        "year_": <int>,
                        "make_id_": <int>,
                        "make_name_": <str>,
                        "model_id_": <int>,
                        "model_name_": <str>,
                        "submodel_id_": <int>,
                        "submodel_name_": <str>,
                        "categories_": [
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
                    }
                ]
            else:
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

        try:
            if not by_names and not annotated:
                data = sema_client.retrieve_categories(
                    brand_ids=brand_ids,
                    dataset_ids=dataset_ids,
                    vehicle_ids=[vehicle.vehicle_id for vehicle in self]
                )
            else:
                data = []
                for vehicle in self:
                    data += vehicle.retrieve_categories_data_from_api(
                        brand_ids=brand_ids,
                        dataset_ids=dataset_ids,
                        by_names=by_names,
                        annotated=annotated
                    )
            return data
        except Exception:
            raise

    def retrieve_products_by_brand_data_from_api(self, brand_ids=None,
                                                 dataset_ids=None,
                                                 part_numbers=None,
                                                 pies_segments=None,
                                                 by_names=False,
                                                 annotated=False):
        """
        Retrieves vehicles products by brand data from SEMA API.

        :param brand_ids: brand IDs on which to filter
        :type brand_ids: list
        :param dataset_ids: dataset IDs on which to filter
        :type dataset_ids: list
        :param part_numbers: part numbers on which to filter
        :type part_numbers: list
        :param pies_segments: pies segments to include or ['all']
        :type pies_segments: list
        :param by_names: whether or not to filter by names rather than
            ID
        :type by_names: bool
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: vehicles products data
        :rtype: list

        :raises Exception: on general exception

        .. Topic:: **-Parameters-**

            Only one of `brand_ids` or `dataset_ids` allowed

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_ids_": <list>, (if defined)
                        "dataset_ids_": <list>, (if defined)
                        "base_vehicle_id_": <int>,
                        "vehicle_id_": <int>,
                        "year_": <int>,
                        "make_id_": <int>,
                        "make_name_": <str>,
                        "model_id_": <int>,
                        "model_name_": <str>,
                        "submodel_id_": <int>,
                        "submodel_name_": <str>,
                        "part_numbers_": <list>, (if defined)
                        "products_": [
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
                    }
                ]
            else:
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

        try:
            if not by_names and not annotated:
                data = sema_client.retrieve_products_by_brand(
                    brand_ids=brand_ids,
                    dataset_ids=dataset_ids,
                    part_numbers=part_numbers,
                    pies_segments=pies_segments,
                    vehicle_ids=[vehicle.vehicle_id for vehicle in self]
                )
            else:
                data = []
                for vehicle in self:
                    data += vehicle.retrieve_products_by_brand_data_from_api(
                        brand_ids=brand_ids,
                        dataset_ids=dataset_ids,
                        part_numbers=part_numbers,
                        pies_segments=pies_segments,
                        by_names=by_names,
                        annotated=annotated
                    )
            return data
        except Exception:
            raise

    def retrieve_products_by_category_data_from_api(self, category_id,
                                                    brand_ids=None,
                                                    dataset_ids=None,
                                                    part_numbers=None,
                                                    pies_segments=None,
                                                    by_names=False,
                                                    annotated=False):
        """
        Retrieves vehicles products by category data from SEMA API.

        :param category_id: category ID on which to filter
        :type category_id: int
        :param brand_ids: brand IDs on which to filter
        :type brand_ids: list
        :param dataset_ids: dataset IDs on which to filter
        :type dataset_ids: list
        :param part_numbers: part numbers on which to filter
        :type part_numbers: list
        :param pies_segments: pies segments to include or ['all']
        :type pies_segments: list
        :param by_names: whether or not to filter by names rather than
            ID
        :type by_names: bool
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: vehicles products by category data
        :rtype: list

        :raises Exception: on general exception

        .. Topic:: **-Parameters-**

            Only one of `brand_ids` or `dataset_ids` allowed

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_ids_": <list>, (if defined)
                        "dataset_ids_": <list>, (if defined)
                        "base_vehicle_id_": <int>,
                        "vehicle_id_": <int>,
                        "year_": <int>,
                        "make_id_": <int>,
                        "make_name_": <str>,
                        "model_id_": <int>,
                        "model_name_": <str>,
                        "submodel_id_": <int>,
                        "submodel_name_": <str>,
                        "part_numbers_": <list>, (if defined)
                        "products_": [
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
                    }
                ]
            else:
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

        try:
            if not by_names and not annotated:
                data = sema_client.retrieve_products_by_category(
                    category_id=category_id,
                    brand_ids=brand_ids,
                    dataset_ids=dataset_ids,
                    vehicle_ids=[vehicle.vehicle_id for vehicle in self],
                    part_numbers=part_numbers,
                    pies_segments=pies_segments,
                )
            else:
                data = []
                for vehicle in self:
                    data += vehicle.retrieve_products_by_category_data_from_api(
                        category_id=category_id,
                        brand_ids=brand_ids,
                        dataset_ids=dataset_ids,
                        part_numbers=part_numbers,
                        pies_segments=pies_segments,
                        by_names=by_names,
                        annotated=annotated
                    )
            return data
        except Exception:
            raise
    # </editor-fold>


class SemaEngineQuerySet(SemaBaseQuerySet):
    """
    This queryset class defines SEMA vehicle engines queryset methods.

    """

    def with_admin_data(self):
        return self.select_related(
            'vehicle'
        )


class SemaCategoryQuerySet(SemaBaseQuerySet):
    """
    This queryset class defines SEMA category queryset methods.

    """

    def with_admin_data(self):
        return self.prefetch_related(
            'parent_categories',
            'child_categories',
            'datasets',
            'products'
        ).annotate(
            _parent_category_count=Count(
                'parent_categories',
                distinct=True
            ),
            _parent_category_relevant_count=Count(
                'parent_categories',
                filter=Q(parent_categories__is_relevant=True),
                distinct=True
            ),
            _child_category_count=Count(
                'child_categories',
                distinct=True
            ),
            _child_category_relevant_count=Count(
                'child_categories',
                filter=Q(child_categories__is_relevant=True),
                distinct=True
            ),
            _dataset_count=Count(
                'datasets',
                distinct=True
            ),
            _dataset_relevant_count=Count(
                'datasets',
                filter=Q(datasets__is_relevant=True),
                distinct=True
            ),
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

    # <editor-fold desc="retrieve properties ...">
    def retrieve_products_by_category_data_from_api(self, brand_ids=None,
                                                    dataset_ids=None,
                                                    base_vehicle_ids=None,
                                                    vehicle_ids=None,
                                                    year=None, make_name=None,
                                                    model_name=None,
                                                    submodel_name=None,
                                                    part_numbers=None,
                                                    pies_segments=None,
                                                    annotated=False):
        """
        Retrieves categories products data from SEMA API.

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
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: categories products data
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

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "category_id_": <int>,
                        "brand_ids_": <list>, (if defined)
                        "dataset_ids_": <list>, (if defined)
                        "base_vehicle_ids_": <list>, (if defined)
                        "vehicle_ids_": <list>, (if defined)
                        "year_": <int>, (if defined)
                        "make_name_": <str>, (if defined)
                        "model_name_": <str>, (if defined)
                        "submodel_name_": <str>, (if defined)
                        "part_numbers_": <list>, (if defined)
                        "products_": [
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
                    }
                ]
            else:
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

        try:
            data = []
            for category in self:
                data += category.retrieve_products_by_category_data_from_api(
                    brand_ids=brand_ids,
                    dataset_ids=dataset_ids,
                    base_vehicle_ids=base_vehicle_ids,
                    vehicle_ids=vehicle_ids,
                    part_numbers=part_numbers,
                    year=year,
                    make_name=make_name,
                    model_name=model_name,
                    submodel_name=submodel_name,
                    pies_segments=pies_segments,
                    annotated=annotated
                )
            return data
        except Exception:
            raise
    # </editor-fold>

    # <editor-fold desc="perform properties ...">
    def perform_category_products_update_from_api(self, **filters):
        msgs = []
        for category in self:
            try:
                msgs += category.perform_category_products_update_from_api(
                    **filters
                )
            except Exception as err:
                msgs.append(self.model.get_class_error_msg(str(err)))

        if not msgs:
            msgs.append(self.model.get_class_up_to_date_msg())
        return msgs
    # </editor-fold>


class SemaProductQuerySet(SemaBaseQuerySet):
    """
    This queryset class defines SEMA product queryset methods.

    """

    def with_admin_data(self):
        return self.select_related(
            'dataset'
        ).prefetch_related(
            'description_pies_attributes',
            'digital_assets_pies_attributes',
            'categories',
            'vehicles'
        ).annotate(
            _description_pies_attribute_count=Count(
                'description_pies_attributes',
                distinct=True
            ),
            _digital_assets_pies_attribute_count=Count(
                'digital_assets_pies_attributes',
                distinct=True
            ),
            _category_count=Count(
                'categories',
                distinct=True
            ),
            _category_relevant_count=Count(
                'categories',
                filter=Q(categories__is_relevant=True),
                distinct=True
            ),
            _vehicle_count=Count(
                'vehicles',
                distinct=True
            ),
            _vehicle_relevant_count=Count(
                'vehicles',
                filter=Q(vehicles__is_relevant=True),
                distinct=True
            )
        )

    # <editor-fold desc="retrieve properties ...">
    def retrieve_products_by_brand_data_from_api(self, base_vehicle_ids=None,
                                                 vehicle_ids=None, year=None,
                                                 make_name=None,
                                                 model_name=None,
                                                 submodel_name=None,
                                                 pies_segments=None,
                                                 annotated=False):
        """
        Retrieves products by brand data from SEMA API.

        :param base_vehicle_ids: base vehicle IDs on which to filter
        :type base_vehicle_ids: list
        :param vehicle_ids: vehicle IDs on which to filter
        :type vehicle_ids: list
        :param year: year on which to filter
        :type year: int
        :param make_name: make name on which to filter
        :type make_name: str
        :param model_name: model name on which to filter
        :type model_name: str
        :param submodel_name: submodel name on which to filter
        :type submodel_name: str
        :param pies_segments: pies segments to include or ['all']
        :type pies_segments: list
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: product data
        :rtype: list

        :raises Exception: on general exception

        .. Topic:: **-Parameters-**

            `year` requires `make_name` and `model_name`

            `make_name` requires `year` and `model_name`

            `model_name` requires `year` and `make_name`

            `submodel_name` requires `year`, `make_name`, and `model_name`

            Only one of `base_vehicle_ids`, `vehicle_ids`, or named
            year/make/model group allowed

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_id_": <str>,
                        "dataset_id_": <int>,
                        "base_vehicle_ids_": <list>, (if defined)
                        "vehicle_ids_": <list>, (if defined)
                        "year_": <int>, (if defined)
                        "make_name_": <str>, (if defined)
                        "model_name_": <str>, (if defined)
                        "submodel_name_": <str>, (if defined)
                        "part_numbers_": <list>,
                        "products_": [
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
                    }
                ]
            else:
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

        try:
            dataset_products = defaultdict(list)
            for product in self:
                dataset_products[product.dataset].append(product.part_number)

            data = []
            for dataset, part_numbers in dataset_products.items():
                data += dataset.retrieve_products_by_brand_data_from_api(
                    base_vehicle_ids=base_vehicle_ids,
                    vehicle_ids=vehicle_ids,
                    year=year,
                    make_name=make_name,
                    model_name=model_name,
                    submodel_name=submodel_name,
                    part_numbers=part_numbers,
                    pies_segments=pies_segments,
                    annotated=annotated
                )
            return data
        except Exception:
            raise

    def retrieve_products_by_category_data_from_api(self, category_id,
                                                    base_vehicle_ids=None,
                                                    vehicle_ids=None,
                                                    year=None, make_name=None,
                                                    model_name=None,
                                                    submodel_name=None,
                                                    pies_segments=None,
                                                    annotated=False):
        """
        Retrieves products by category data from SEMA API.

        :param category_id: category ID on which to filter
        :type category_id: int
        :type base_vehicle_ids: int
        :param base_vehicle_ids: base vehicles IDs on which to filter
        :type base_vehicle_ids: list
        :param vehicle_ids: vehicle IDs on which to filter
        :type vehicle_ids: list
        :param year: year on which to filter
        :type year: int
        :param make_name: make name on which to filter
        :type make_name: str
        :param model_name: model name on which to filter
        :type model_name: str
        :param submodel_name: submodel name on which to filter
        :type submodel_name: str
        :param pies_segments: pies segments to include or ['all']
        :type pies_segments: list
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: products by category data
        :rtype: list

        :raises Exception: on general exception

        .. Topic:: **-Parameters-**

            `year` requires `make_name` and `model_name`

            `make_name` requires `year` and `model_name`

            `model_name` requires `year` and `make_name`

            `submodel_name` requires `year`, `make_name`, and `model_name`

            Only one of `base_vehicle_ids`, `vehicle_ids`, or named
            year/make/model group allowed

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "category_id_": <int>,
                        "brand_id_": <str>,
                        "dataset_id_": <int>,
                        "base_vehicle_ids_": <list>, (if defined)
                        "vehicle_ids_": <list>, (if defined)
                        "year_": <int>, (if defined)
                        "make_name_": <str>, (if defined)
                        "model_name_": <str>, (if defined)
                        "submodel_name_": <str>, (if defined)
                        "part_numbers_": <list>,
                        "products_": [
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
                    },
                    {...}
                ]
            else:
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

        try:
            dataset_products = defaultdict(list)
            for product in self:
                dataset_products[product.dataset].append(product.part_number)

            data = []
            for dataset, part_numbers in dataset_products.items():
                data += dataset.retrieve_products_by_category_data_from_api(
                    category_id=category_id,
                    base_vehicle_ids=base_vehicle_ids,
                    vehicle_ids=vehicle_ids,
                    year=year,
                    make_name=make_name,
                    model_name=model_name,
                    submodel_name=submodel_name,
                    part_numbers=part_numbers,
                    pies_segments=pies_segments,
                    annotated=annotated
                )
            return data
        except Exception:
            raise

    def retrieve_vehicles_by_product_data_from_api(self, annotated=False):
        """
        Retrieves vehicles by product data from SEMA API.

        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: vehicles by product data
        :rtype: list

        :raises Exception: on general exception

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "dataset_id_": <int>,
                        "products_": [
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
                    }
                ]
            else:
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

        """

        try:
            dataset_products = defaultdict(list)
            for product in self:
                dataset_products[product.dataset].append(product.part_number)

            data = []
            for dataset, part_numbers in dataset_products.items():
                data += dataset.retrieve_vehicles_by_product_data_from_api(
                    part_numbers=part_numbers,
                    annotated=annotated
                )
            return data
        except Exception:
            raise

    def retrieve_product_html_data_from_api(self, annotated=False):
        """
        Retrieves products HTML data from SEMA API object.

        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: products HTML
        :rtype: list

        :raises: Exception on SEMA API object method exception

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "product_id_": <int>,
                        "html_": <str>
                    },
                    {...}
                ]
            else:
                ret = [
                    <str>,
                    ...
                ]
        """

        try:
            data = []
            for product in self:
                data.append(
                    product.retrieve_product_html_data_from_api(
                        annotated=annotated
                    )
                )
            return data
        except Exception:
            raise
    # </editor-fold>

    # <editor-fold desc="perform properties ...">
    def perform_product_vehicles_update_from_api(self):
        msgs = []
        for product in self:
            try:
                msgs += product.perform_product_vehicles_update_from_api()
            except Exception as err:
                msgs.append(self.model.get_class_error_msg(str(err)))

        if not msgs:
            msgs.append(self.model.get_class_up_to_date_msg())
        return msgs

    def perform_pies_attribute_update_from_api(self, pies_attr_model,
                                               new_only=False, **filters):
        """
        Retrieves products PIES attribute data from SEMA API, and
        creates and/or updates products PIES attribute objects.

        :param pies_attr_model: SEMA PIES Attribute model class
        :type pies_attr_model: sema.models.SemaBasePiesAttributeModel
        :param new_only: whether or not to skip updating existing
            objects
        :type new_only: bool
        :param filters: kwargs by which to filter data retrieve

        :return: info, success, and/or error messages
        :rtype: list

        """

        msgs = []
        try:
            msgs += pies_attr_model.objects.perform_import_from_api(
                products=self,
                new_only=new_only,
                **filters
            )
        except Exception as err:
            msgs.append(self.model.get_class_error_msg(str(err)))
            return msgs

        if not msgs:
            msgs.append(self.model.get_class_up_to_date_msg())
        return msgs

    def perform_product_html_update_from_api(self):
        """
        Retrieves products HTML data from SEMA API, and updates HTML
        fields.

        :return: update or error messages
        :rtype: list

        """

        msgs = []
        for product in self:
            try:
                msgs.append(product.perform_product_html_update_from_api())
            except Exception as err:
                msgs.append(product.get_instance_error_msg(str(err)))

        if not msgs:
            msgs.append(self.model.get_class_up_to_date_msg())
        return msgs
    # </editor-fold>


class SemaBasePiesAttributeQuerySet(SemaBaseQuerySet):
    """
    This base queryset class defines base attributes for SEMA PIES
    attribute querysets.

    """

    pass


class SemaDescriptionPiesAttributeQuerySet(SemaBasePiesAttributeQuerySet):
    """
    This queryset class defines SEMA description PIES attribute queryset
    methods.

    """

    pass


class SemaDigitalAssetsPiesAttributeQuerySet(SemaBasePiesAttributeQuerySet):
    """
    This queryset class defines SEMA digital assets PIES attribute
    queryset methods.

    """

    # <editor-fold desc="perform properties ...">
    def perform_relevancy_update(self):
        msgs = []

        for pies_attr in self:
            if pies_attr.may_be_relevant:
                try:
                    if pies_attr.is_broken:
                        relevant = False
                        relevancy_exception = 'Broken'
                    else:
                        relevant = True
                        relevancy_exception = ''
                except Exception as err:
                    relevant = False
                    relevancy_exception = str(err)[:100]
            else:
                relevant = False
                relevancy_exception = ''

            if not pies_attr.is_relevant == relevant:
                pies_attr.is_relevant = relevant
                pies_attr.relevancy_exception = relevancy_exception
                pies_attr.save()
                msgs.append(
                    pies_attr.get_update_success_msg(
                        previous_data={'relevant': not relevant},
                        new_data={'relevant': relevant},
                    )
                )
            else:
                msgs.append(pies_attr.get_up_to_date_msg())

        if not msgs:
            msgs.append(self.model.get_class_up_to_date_msg())
        return msgs
    # </editor-fold>


class SemaBaseManager(Manager):
    """
    This base manager class defines base attributes for SEMA managers.

    """

    def get_queryset(self):
        """
        Returns custom QuerySet object.

        :return: QuerySet object
        :rtype: object

        """

        return SemaBaseQuerySet(
            self.model,
            using=self._db
        )

    # <editor-fold desc="perform properties ...">
    def perform_import_from_api(self, new_only=False, **filters):
        """
        Retrieves data from SEMA API, and creates and/or updates
        objects.

        :param new_only: whether or not to skip updating existing
            objects
        :type new_only: bool
        :param filters: kwargs by which to filter data retrieve

        :return: info, success, and/or error messages
        :rtype: list

        """

        msgs = []

        try:
            data = self.get_api_data(**filters)
            msgs += self.import_from_api_data(data=data, new_only=new_only)
        except Exception as err:
            msgs.append(self.model.get_class_error_msg(str(err)))
            return msgs

        if not msgs:
            msgs.append(self.model.get_class_up_to_date_msg())
        return msgs

    def perform_unauthorize_from_api(self):
        """
        Retrieves data from SEMA API, and unauthorizes existing objects
        not in data.

        :return: info, success, and/or error messages
        :rtype: list

        """

        msgs = []

        try:
            data = self.get_api_data()
            msgs += self.unauthorize_from_api_data(data=data)
        except Exception as err:
            msgs.append(self.model.get_class_error_msg(str(err)))
            return msgs

        return msgs

    def perform_api_sync(self):
        """
        Retrieves data from SEMA API, and creates and updates objects in
        data, and unauthorizes existing objects not in data.

        :return: info, success, and/or error messages
        :rtype: list

        """

        msgs = []

        try:
            data = self.get_api_data()
            msgs += self.import_from_api_data(data=data, new_only=False)
            msgs += self.unauthorize_from_api_data(data=data)
        except Exception as err:
            msgs.append(self.model.get_class_error_msg(str(err)))
            return msgs

        if not msgs:
            msgs.append(self.model.get_class_up_to_date_msg())
        return msgs
    # </editor-fold>

    # <editor-fold desc="data properties ...">
    def get_api_data(self, **filters):
        """
        Retrieves and cleans data from SEMA API.

        :param filters: kwargs by which to filter data retrieve

        :return: clean API data
        :rtype: list

        """

        try:
            filters = self.get_retrieve_data_from_api_params(**filters)
            data = self.retrieve_data_from_api(**filters)
            clean_data = self.clean_api_data(data=data)
            return clean_data
        except Exception:
            raise

    def get_retrieve_data_from_api_params(self, **params):
        """
        Returns params. Can be overridden to add required retrieve
        params.

        :param params: param kwargs to which to add additional params

        :return: param kwargs
        :rtype: dict

        """

        return params

    def retrieve_data_from_api(self, **filters):
        """
        Raises exception. Must be overridden with method that retrieves
        API data.

        :param filters: kwargs by which to filter data retrieve

        :raises Exception: if not overridden

        """

        raise Exception('Retrieve data from API must be defined')

    def clean_api_data(self, data):
        """
        Cleans object data by flattening nested data and removing
        duplicates.

        :param data: API data
        :type data: list

        :return: clean API data
        :rtype: list

        :raises Exception: on general exception

        """

        try:
            return self.remove_duplicates_from_api_data(
                data=self.flatten_api_data(data=data)
            )
        except Exception:
            raise

    def flatten_api_data(self, data):
        """
        Returns data. Can be overridden for data flattening.

        :param data: API data
        :type data: list

        :return: flat API data
        :rtype: list

        """

        return data

    @staticmethod
    def remove_duplicates_from_api_data(data):
        """
        Removes duplicate items from list of items or dictionaries.

        :param data: API data
        :type data: list

        :return: reduced API data
        :rtype: list

        """

        try:
            return [dict(t) for t in {tuple(i.items()) for i in data}]
        except AttributeError:
            try:
                return list(dict.fromkeys(data))
            except Exception:
                raise
        except Exception:
            raise
    # </editor-fold>

    # <editor-fold desc="import properties ...">
    def import_from_api_data(self, data, new_only=False):
        """
        Retrieves and creates and/or updates objects from API data.

        :param data: API data
        :type data: list
        :param new_only: whether or not to skip updating existing
            objects
        :type new_only: bool

        :return: info, success, and/or error messages
        :rtype: list

        """

        msgs = []
        for item in data:
            try:
                pk, fields = self.parse_api_data(data=item)
            except Exception as err:
                msgs.append(self.model.get_class_error_msg(f"{item}: {err}"))
                continue

            try:
                obj = self.get_object_from_api_data(pk=pk, **fields)
                if not new_only:
                    msgs.append(obj.update_from_api_data(**fields))
            except self.model.DoesNotExist:
                msgs.append(self.create_from_api_data(pk=pk, **fields))
            except Exception as err:
                msgs.append(self.model.get_class_error_msg(f"{item}: {err}"))
        return msgs

    def parse_api_data(self, data):
        """
        Raises exception. Must be overridden with method that returns
        PK and field/value dictionary from API data item.

        :param data: API data item

        :raises Exception: if not overridden

        """

        raise Exception('Parse API data must be defined')

    def get_object_from_api_data(self, pk, **fields):
        """
        Returns object by PK. Can be overridden to retrieve object by
        fields.

        :param pk: object PK
        :param fields: object field/value kwargs

        :return: model instance
        :rtype: object

        :raises Exception: on general exception

        """

        try:
            return self.get(pk=pk)
        except Exception:
            raise

    def create_from_api_data(self, pk, **fields):
        """
        Creates object from PK and field/value kwargs.

        :param pk: object PK
        :param fields: object field/value kwargs

        :return: success or error message
        :rtype: str

        """

        try:
            m2m_fields = {}
            create_fields = {}
            for attr, value in fields.items():
                if isinstance(
                        self.model._meta.get_field(attr), ManyToManyField):
                    m2m_fields[attr] = value
                else:
                    create_fields[attr] = value
            obj = self.create(
                pk=pk,
                **create_fields
            )
            for attr, value in m2m_fields.items():
                getattr(obj, attr).add(value)
                obj.save()
            msg = obj.get_create_success_msg()
        except Exception as err:
            msg = self.model.get_class_error_msg(f"{pk}, {fields}, {err}")
        return msg
    # </editor-fold>

    # <editor-fold desc="unauthorize properties ...">
    def unauthorize_from_api_data(self, data):
        """
        Retrieves PKs of objects in data and unauthorizes any objects
        not in data.

        :param data: API data
        :type data: list

        :return: info, success, and/or error messages
        :rtype: list

        """

        msgs = []

        try:
            authorized_pks = self.get_pk_list_from_api_data(data=data)
            unauthorized = self.model.objects.filter(~Q(pk__in=authorized_pks))
            msgs += unauthorized.unauthorize()
        except Exception as err:
            msgs.append(self.model.get_class_error_msg(str(err)))
            return msgs

        return msgs

    def get_pk_list_from_api_data(self, data):
        """
        Raises exception. Must be overridden with method that returns a
        list of object PKs.

        :param data: API data
        :type data: list

        :raises Exception: if not overridden

        """

        raise Exception('Get PK list must be defined')

    def unauthorize(self):
        """
        Retrieves queryset and marks queryset objects as unauthorized.

        :return: info, success, and/or error messages
        :rtype: list

        """
        return self.get_queryset().unauthorize()
    # </editor-fold>


class SemaBrandManager(SemaBaseManager):
    """
    This manager class defines SEMA brand methods.

    """

    def get_queryset(self):
        return SemaBrandQuerySet(
            self.model,
            using=self._db
        )

    def with_admin_data(self):
        return self.get_queryset().with_admin_data()

    # <editor-fold desc="retrieve properties ...">
    def retrieve_data_from_api(self):
        """
        Retrieves brand data from SEMA API.

        :return: brand data
        :rtype: list

        :raises Exception: on general exception

        **-Return Format-**
        ::
            ret = [
                {
                    "AAIABrandId": <str>,
                    "BrandName": <str>
                },
                {...}
            ]

        """

        try:
            data = sema_client.retrieve_brand_datasets()
            for item in data:
                del item['DatasetId']
                del item['DatasetName']
            return data
        except Exception:
            raise

    def retrieve_years_data_from_api(self, annotated=False):
        """
        Retrieves brands years data from SEMA API.

        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: brands years data
        :rtype: list

        :raises Exception: on general exception

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_id_": <str>,
                        "years_": [
                            <int>,
                            ...
                        ]
                    }
                ]
            else:
                ret = [
                    <int>,
                    ...
                ]

        """

        try:
            return self.get_queryset().retrieve_years_data_from_api(
                annotated=annotated
            )
        except Exception:
            raise

    def retrieve_makes_data_from_api(self, year=None, annotated=False):
        """
        Retrieves brands makes data from SEMA API.

        :param year: year on which to filter
        :type year: int
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: brands makes data
        :rtype: list

        :raises Exception: on general exception

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_id_": <str>,
                        "year_": <int>, (if defined)
                        "makes_": [
                            {
                                "MakeID": <int>,
                                "MakeName": <str>
                            },
                            {...}
                        ]
                    }
                ]
            else:
                ret = [
                    {
                        "MakeID": <int>,
                        "MakeName": <str>
                    },
                    {...}
            ]

        """

        try:
            return self.get_queryset().retrieve_makes_data_from_api(
                year=year,
                annotated=annotated
            )
        except Exception:
            raise

    def retrieve_models_data_from_api(self, year=None,
                                      make_id=None, annotated=False):
        """
        Retrieves brands models data from SEMA API.

        :param year: year on which to filter
        :type year: int
        :param make_id: make ID on which to filter
        :type make_id: int
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: brands models data
        :rtype: list

        :raises Exception: on general exception

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_id_": <str>,
                        "year_": <int>, (if defined)
                        "make_id_": <int>, (if defined)
                        "models_": [
                            {
                                "BaseVehicleID": <int>,
                                "ModelID": <int>,
                                "ModelName": <str>
                            },
                            {...}
                        ]
                    }
                ]
            else:
                ret = [
                    {
                        "BaseVehicleID": <int>,
                        "ModelID": <int>,
                        "ModelName": <str>
                    },
                    {...}
            ]

        """

        try:
            return self.get_queryset().retrieve_models_data_from_api(
                year=year,
                make_id=make_id,
                annotated=annotated
            )
        except Exception:
            raise

    def retrieve_submodels_data_from_api(self, year=None, make_id=None,
                                         model_id=None, annotated=False):
        """
        Retrieves brands submodels data from SEMA API.

        :param year: year on which to filter
        :type year: int
        :param make_id: make ID on which to filter
        :type make_id: int
        :param model_id: model ID on which to filter
        :type model_id: int
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: brands submodels data
        :rtype: list

        :raises Exception: on general exception

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_id_": <str>,
                        "year_": <int>, (if defined)
                        "make_id_": <int>, (if defined)
                        "model_id_": <int>, (if defined)
                        "submodels_": [
                            {
                                "VehicleID": <int>,
                                "SubmodelID": <int>,
                                "SubmodelName": <str>
                            },
                            {...}
                        ]
                    }
                ]
            else:
                ret = [
                    {
                        "VehicleID": <int>,
                        "SubmodelID": <int>,
                        "SubmodelName": <str>
                    },
                    {...}
            ]

        """

        try:
            return self.get_queryset().retrieve_submodels_data_from_api(
                year=year,
                make_id=make_id,
                model_id=model_id,
                annotated=annotated
            )
        except Exception:
            raise

    def retrieve_engines_data_from_api(self, year=None, make_id=None,
                                       model_id=None, annotated=False):
        """
        Retrieves brands engines data from SEMA API.

        :param year: year on which to filter
        :type year: int
        :param make_id: make ID on which to filter
        :type make_id: int
        :param model_id: model ID on which to filter
        :type model_id: int
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: brands engines data
        :rtype: list

        :raises Exception: on general exception

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_id_": <str>,
                        "year_": <int>, (if defined)
                        "make_id_": <int>, (if defined)
                        "model_id_": <int>, (if defined)
                        "engines_": [
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
                    },
                    {...}
                ]
            else:
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

        try:
            return self.get_queryset().retrieve_engines_data_from_api(
                year=year,
                make_id=make_id,
                model_id=model_id,
                annotated=annotated
            )
        except Exception:
            raise

    def retrieve_categories_data_from_api(self, base_vehicle_ids=None,
                                          vehicle_ids=None, year=None,
                                          make_name=None, model_name=None,
                                          submodel_name=None, annotated=False):
        """
        Retrieves brands categories data from SEMA API.

        :param base_vehicle_ids: base vehicle IDs on which to filter
        :type base_vehicle_ids: list
        :param vehicle_ids: vehicle IDs on which to filter
        :type vehicle_ids: list
        :param year: year on which to filter
        :type year: int
        :param make_name: make name on which to filter
        :type make_name: str
        :param model_name: model name on which to filter
        :type model_name: str
        :param submodel_name: submodel name on which to filter
        :type submodel_name: str
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: brands categories data
        :rtype: list

        :raises Exception: on general exception

        .. Topic:: **-Parameters-**

            `year` requires `make_name` and `model_name`

            `make_name` requires `year` and `model_name`

            `model_name` requires `year` and `make_name`

            `submodel_name` requires `year`, `make_name`, and `model_name`

            Only one of `base_vehicle_ids`, `vehicle_ids`, or named
            year/make/model group allowed

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_id_": <str>,
                        "base_vehicle_ids_": <list>, (if defined)
                        "vehicle_ids_": <list>, (if defined)
                        "year_": <int>, (if defined)
                        "make_name_": <str>, (if defined)
                        "model_name_": <str>, (if defined)
                        "submodel_name_": <str>, (if defined)
                        "categories_": [
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
                    }
                ]
            else:
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

        try:
            return self.get_queryset().retrieve_categories_data_from_api(
                base_vehicle_ids=base_vehicle_ids,
                vehicle_ids=vehicle_ids,
                year=year,
                make_name=make_name,
                model_name=model_name,
                submodel_name=submodel_name,
                annotated=annotated
            )
        except Exception:
            raise

    def retrieve_products_by_brand_data_from_api(self, base_vehicle_ids=None,
                                                 vehicle_ids=None, year=None,
                                                 make_name=None,
                                                 model_name=None,
                                                 submodel_name=None,
                                                 part_numbers=None,
                                                 pies_segments=None,
                                                 annotated=False):
        """
        Retrieves brands products data from SEMA API.

        :param base_vehicle_ids: base vehicles IDs on which to filter
        :type base_vehicle_ids: list
        :param vehicle_ids: vehicle IDs on which to filter
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
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: brands products data
        :rtype: list

        :raises Exception: on general exception

        .. Topic:: **-Parameters-**

            `year` requires `make_name` and `model_name`

            `make_name` requires `year` and `model_name`

            `model_name` requires `year` and `make_name`

            `submodel_name` requires `year`, `make_name`, and `model_name`

            Only one of `base_vehicle_ids`, `vehicle_ids`, or named
            year/make/model group allowed

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_id_": <str>,
                        "base_vehicle_ids_": <list>, (if defined)
                        "vehicle_ids_": <list>, (if defined)
                        "year_": <int>, (if defined)
                        "make_name_": <str>, (if defined)
                        "model_name_": <str>, (if defined)
                        "submodel_name_": <str>, (if defined)
                        "part_numbers_": <list>, (if defined)
                        "products_": [
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
                    }
                ]
            else:
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

        try:
            return self.get_queryset().retrieve_products_by_brand_data_from_api(
                base_vehicle_ids=base_vehicle_ids,
                vehicle_ids=vehicle_ids,
                year=year,
                make_name=make_name,
                model_name=model_name,
                submodel_name=submodel_name,
                part_numbers=part_numbers,
                pies_segments=pies_segments,
                annotated=annotated
            )
        except Exception:
            raise

    def retrieve_products_by_category_data_from_api(self, category_id,
                                                    base_vehicle_ids=None,
                                                    vehicle_ids=None,
                                                    year=None, make_name=None,
                                                    model_name=None,
                                                    submodel_name=None,
                                                    part_numbers=None,
                                                    pies_segments=None,
                                                    annotated=False):
        """
        Retrieves brands products by category data from SEMA API.

        :param category_id: category ID on which to filter
        :type category_id: int
        :param base_vehicle_ids: base vehicles IDs on which to filter
        :type base_vehicle_ids: list
        :param vehicle_ids: vehicle IDs on which to filter
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
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: brands products by category data
        :rtype: list

        :raises Exception: on general exception

        .. Topic:: **-Parameters-**

            `year` requires `make_name` and `model_name`

            `make_name` requires `year` and `model_name`

            `model_name` requires `year` and `make_name`

            `submodel_name` requires `year`, `make_name`, and `model_name`

            Only one of `base_vehicle_ids`, `vehicle_ids`, or named
            year/make/model group allowed

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_id_": <str>,
                        "category_id_": <int>,
                        "base_vehicle_ids_": <list>, (if defined)
                        "vehicle_ids_": <list>, (if defined)
                        "year_": <int>, (if defined)
                        "make_name_": <str>, (if defined)
                        "model_name_": <str>, (if defined)
                        "submodel_name_": <str>, (if defined)
                        "part_numbers_": <list>, (if defined)
                        "products_": [
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
                    },
                    {...}
                ]
            else:
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

        try:
            return self.get_queryset().retrieve_products_by_category_data_from_api(
                category_id=category_id,
                base_vehicle_ids=base_vehicle_ids,
                vehicle_ids=vehicle_ids,
                year=year,
                make_name=make_name,
                model_name=model_name,
                submodel_name=submodel_name,
                part_numbers=part_numbers,
                pies_segments=pies_segments,
                annotated=annotated
            )
        except Exception:
            raise

    def retrieve_vehicles_by_product_data_from_api(self, part_numbers=None,
                                                   annotated=False):
        """
        Retrieves brands vehicles by product data from SEMA API.

        :param part_numbers: part numbers on which to filter
        :type part_numbers: list
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: brands vehicles by product data
        :rtype: list

        :raises Exception: on general exception

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_id_": <str>,
                        "part_numbers_": <list>, (if defined)
                        "products_": [
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
                    }
                ]
            else:
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

        """

        try:
            return self.get_queryset().retrieve_vehicles_by_product_data_from_api(
                part_numbers=part_numbers,
                annotated=annotated
            )
        except Exception:
            raise

    def retrieve_vehicles_by_brand_data_from_api(self, annotated=False):
        """
        Retrieves vehicles by brand data from SEMA API.

        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: vehicles by brand data
        :rtype: list

        :raises Exception: on general exception

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_id_": <str>,
                        "vehicles_": [
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
                    },
                    {...}
                ]
            else:
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

        try:
            return self.get_queryset().retrieve_vehicles_by_brand_data_from_api(
                annotated=annotated
            )
        except Exception:
            raise
    # </editor-fold>

    # <editor-fold desc="import properties ...">
    def parse_api_data(self, data):
        """
        Returns object PK and field/value dictionary from API data item.

        :param data: API data item
        :type data: dict

        :return: object PK and field/value dictionary
        :rtype: tuple

        :raises Exception: on general exception

        **-Expected Data Format-**
        ::
            data = {
                "AAIABrandId": <str>,
                "BrandName": <str>
            }

        **-Return Format-**
        ::
            pk = <str>
            fields = {
                "is_authorized": <bool>,
                "name": <str>
            }

        """

        try:
            pk = data['AAIABrandId']
            fields = {
                'is_authorized': True,
                'name': data['BrandName']
            }
            return pk, fields
        except Exception:
            raise
    # </editor-fold>

    # <editor-fold desc="unauthorize properties ...">
    def get_pk_list_from_api_data(self, data):
        """
        Returns a list of object PKs from full API data.

        :param data: API data
        :type data: list

        :return: list of PKs
        :rtype: list

        :raises Exception: on general exception

        **-Expected Data Format-**
        ::
            data = [
                {
                    "AAIABrandId": <str>
                },
                {..}
            ]

        **-Return Format-**
        ::
            ret = [
                <str>,
                ...
            ]

        """

        try:
            return [item['AAIABrandId'] for item in data]
        except Exception:
            raise
    # </editor-fold>


class SemaDatasetManager(SemaBaseManager):
    """
    This manager class defines SEMA dataset methods.

    """

    def get_queryset(self):
        return SemaDatasetQuerySet(
            self.model,
            using=self._db
        )

    def with_admin_data(self):
        return self.get_queryset().with_admin_data()

    # <editor-fold desc="retrieve properties ...">
    def retrieve_data_from_api(self):
        """
        Retrieves dataset data from SEMA API.

        :return: dataset data
        :rtype: list

        :raises Exception: on general exception

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

        try:
            return sema_client.retrieve_brand_datasets()
        except Exception:
            raise

    def retrieve_years_data_from_api(self, annotated=False):
        """
        Retrieves datasets years data from SEMA API.

        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: datasets years data
        :rtype: list

        :raises Exception: on general exception

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_id_": <str>,
                        "dataset_id_": <int>,
                        "years_": [
                            <int>,
                            ...
                        ]
                    }
                ]
            else:
                ret = [
                    <int>,
                    ...
                ]

        """

        try:
            return self.get_queryset().retrieve_years_data_from_api(
                annotated=annotated
            )
        except Exception:
            raise

    def retrieve_makes_data_from_api(self, year=None, annotated=False):
        """
        Retrieves datasets makes data from SEMA API.

        :param year: year on which to filter
        :type year: int
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: datasets makes data
        :rtype: list

        :raises Exception: on general exception

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_id_": <str>,
                        "dataset_id_": <int>,
                        "year_": <int>, (if defined)
                        "makes_": [
                            {
                                "MakeID": <int>,
                                "MakeName": <str>
                            },
                            {...}
                        ]
                    }
                ]
            else:
                ret = [
                    {
                        "MakeID": <int>,
                        "MakeName": <str>
                    },
                    {...}
            ]

        """

        try:
            return self.get_queryset().retrieve_makes_data_from_api(
                year=year,
                annotated=annotated
            )
        except Exception:
            raise

    def retrieve_models_data_from_api(self, year=None,
                                      make_id=None, annotated=False):
        """
        Retrieves datasets models data from SEMA API.

        :param year: year on which to filter
        :type year: int
        :param make_id: make ID on which to filter
        :type make_id: int
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: datasets models data
        :rtype: list

        :raises Exception: on general exception

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_id_": <str>,
                        "dataset_id_": <int>,
                        "year_": <int>, (if defined)
                        "make_id_": <int>, (if defined)
                        "models_": [
                            {
                                "BaseVehicleID": <int>,
                                "ModelID": <int>,
                                "ModelName": <str>
                            },
                            {...}
                        ]
                    }
                ]
            else:
                ret = [
                    {
                        "BaseVehicleID": <int>,
                        "ModelID": <int>,
                        "ModelName": <str>
                    },
                    {...}
            ]

        """

        try:
            return self.get_queryset().retrieve_models_data_from_api(
                year=year,
                make_id=make_id,
                annotated=annotated
            )
        except Exception:
            raise

    def retrieve_submodels_data_from_api(self, year=None, make_id=None,
                                         model_id=None, annotated=False):
        """
        Retrieves datasets submodels data from SEMA API.

        :param year: year on which to filter
        :type year: int
        :param make_id: make ID on which to filter
        :type make_id: int
        :param model_id: model ID on which to filter
        :type model_id: int
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: datasets submodels data
        :rtype: list

        :raises Exception: on general exception

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_id_": <str>,
                        "dataset_id_": <int>,
                        "year_": <int>, (if defined)
                        "make_id_": <int>, (if defined)
                        "model_id_": <int>, (if defined)
                        "submodels_": [
                            {
                                "VehicleID": <int>,
                                "SubmodelID": <int>,
                                "SubmodelName": <str>
                            },
                            {...}
                        ]
                    }
                ]
            else:
                ret = [
                    {
                        "VehicleID": <int>,
                        "SubmodelID": <int>,
                        "SubmodelName": <str>
                    },
                    {...}
            ]

        """

        try:
            return self.get_queryset().retrieve_submodels_data_from_api(
                year=year,
                make_id=make_id,
                model_id=model_id,
                annotated=annotated
            )
        except Exception:
            raise

    def retrieve_engines_data_from_api(self, year=None, make_id=None,
                                       model_id=None, annotated=False):
        """
        Retrieves datasets engines data from SEMA API.

        :param year: year on which to filter
        :type year: int
        :param make_id: make ID on which to filter
        :type make_id: int
        :param model_id: model ID on which to filter
        :type model_id: int
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: datasets engines data
        :rtype: list

        :raises Exception: on general exception

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_id_": <str>,
                        "dataset_id_": <int>,
                        "year_": <int>, (if defined)
                        "make_id_": <int>, (if defined)
                        "model_id_": <int>, (if defined)
                        "engines_": [
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
                    },
                    {...}
                ]
            else:
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

        try:
            return self.get_queryset().retrieve_engines_data_from_api(
                year=year,
                make_id=make_id,
                model_id=model_id,
                annotated=annotated
            )
        except Exception:
            raise

    def retrieve_categories_data_from_api(self, base_vehicle_ids=None,
                                          vehicle_ids=None, year=None,
                                          make_name=None, model_name=None,
                                          submodel_name=None, annotated=False):
        """
        Retrieves datasets categories data from SEMA API.

        :param base_vehicle_ids: base vehicle IDs on which to filter
        :type base_vehicle_ids: list
        :param vehicle_ids: vehicle IDs on which to filter
        :type vehicle_ids: list
        :param year: year on which to filter
        :type year: int
        :param make_name: make name on which to filter
        :type make_name: str
        :param model_name: model name on which to filter
        :type model_name: str
        :param submodel_name: submodel name on which to filter
        :type submodel_name: str
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: datasets categories data
        :rtype: list

        :raises Exception: on general exception

        .. Topic:: **-Parameters-**

            `year` requires `make_name` and `model_name`

            `make_name` requires `year` and `model_name`

            `model_name` requires `year` and `make_name`

            `submodel_name` requires `year`, `make_name`, and `model_name`

            Only one of `base_vehicle_ids`, `vehicle_ids`, or named
            year/make/model group allowed

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_id_": <str>,
                        "dataset_id_": <int>,
                        "base_vehicle_ids_": <list>, (if defined)
                        "vehicle_ids_": <list>, (if defined)
                        "year_": <int>, (if defined)
                        "make_name_": <str>, (if defined)
                        "model_name_": <str>, (if defined)
                        "submodel_name_": <str>, (if defined)
                        "categories_": [
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
                    }
                ]
            else:
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

        try:
            return self.get_queryset().retrieve_categories_data_from_api(
                base_vehicle_ids=base_vehicle_ids,
                vehicle_ids=vehicle_ids,
                year=year,
                make_name=make_name,
                model_name=model_name,
                submodel_name=submodel_name,
                annotated=annotated
            )
        except Exception:
            raise

    def retrieve_products_by_brand_data_from_api(self, base_vehicle_ids=None,
                                                 vehicle_ids=None, year=None,
                                                 make_name=None,
                                                 model_name=None,
                                                 submodel_name=None,
                                                 part_numbers=None,
                                                 pies_segments=None,
                                                 annotated=False):
        """
        Retrieves datasets products data from SEMA API.

        :param base_vehicle_ids: base vehicles IDs on which to filter
        :type base_vehicle_ids: list
        :param vehicle_ids: vehicle IDs on which to filter
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
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: datasets products data
        :rtype: list

        :raises Exception: on general exception

        .. Topic:: **-Parameters-**

            `year` requires `make_name` and `model_name`

            `make_name` requires `year` and `model_name`

            `model_name` requires `year` and `make_name`

            `submodel_name` requires `year`, `make_name`, and `model_name`

            Only one of `base_vehicle_ids`, `vehicle_ids`, or named
            year/make/model group allowed

        .. Topic:: **-Parameters-**

            `year` requires `make_name` and `model_name`

            `make_name` requires `year` and `model_name`

            `model_name` requires `year` and `make_name`

            `submodel_name` requires `year`, `make_name`, and `model_name`

            Only one of `base_vehicle_ids`, `vehicle_ids`, or named
            year/make/model group allowed

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_id_": <str>,
                        "dataset_id_": <int>,
                        "base_vehicle_ids_": <list>, (if defined)
                        "vehicle_ids_": <list>, (if defined)
                        "year_": <int>, (if defined)
                        "make_name_": <str>, (if defined)
                        "model_name_": <str>, (if defined)
                        "submodel_name_": <str>, (if defined)
                        "part_numbers_": <list>, (if defined)
                        "products_": [
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
                    }
                ]
            else:
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

        try:
            return self.get_queryset().retrieve_products_by_brand_data_from_api(
                base_vehicle_ids=base_vehicle_ids,
                vehicle_ids=vehicle_ids,
                year=year,
                make_name=make_name,
                model_name=model_name,
                submodel_name=submodel_name,
                part_numbers=part_numbers,
                pies_segments=pies_segments,
                annotated=annotated
            )
        except Exception:
            raise

    def retrieve_products_by_category_data_from_api(self, category_id,
                                                    base_vehicle_ids=None,
                                                    vehicle_ids=None,
                                                    year=None, make_name=None,
                                                    model_name=None,
                                                    submodel_name=None,
                                                    part_numbers=None,
                                                    pies_segments=None,
                                                    annotated=False):
        """
        Retrieves datasets products by category data from SEMA API.

        :param category_id: category ID on which to filter
        :type category_id: int
        :param base_vehicle_ids: base vehicles IDs on which to filter
        :type base_vehicle_ids: list
        :param vehicle_ids: vehicle IDs on which to filter
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
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: datasets products by category data
        :rtype: list

        :raises Exception: on general exception

        .. Topic:: **-Parameters-**

            `year` requires `make_name` and `model_name`

            `make_name` requires `year` and `model_name`

            `model_name` requires `year` and `make_name`

            `submodel_name` requires `year`, `make_name`, and `model_name`

            Only one of `base_vehicle_ids`, `vehicle_ids`, or named
            year/make/model group allowed

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_id_": <str>,
                        "dataset_id_": <int>,
                        "category_id_": <int>,
                        "base_vehicle_ids_": <list>, (if defined)
                        "vehicle_ids_": <list>, (if defined)
                        "year_": <int>, (if defined)
                        "make_name_": <str>, (if defined)
                        "model_name_": <str>, (if defined)
                        "submodel_name_": <str>, (if defined)
                        "part_numbers_": <list>, (if defined)
                        "products_": [
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
                    }
                ]
            else:
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

        try:
            return self.get_queryset().retrieve_products_by_category_data_from_api(
                category_id=category_id,
                base_vehicle_ids=base_vehicle_ids,
                vehicle_ids=vehicle_ids,
                year=year,
                make_name=make_name,
                model_name=model_name,
                submodel_name=submodel_name,
                part_numbers=part_numbers,
                pies_segments=pies_segments,
                annotated=annotated
            )
        except Exception:
            raise

    def retrieve_vehicles_by_product_data_from_api(self, part_numbers=None,
                                                   annotated=False):
        """
        Retrieves datasets vehicles by product data from SEMA API.

        :param part_numbers: part numbers on which to filter
        :type part_numbers: list
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: datasets vehicles by product data
        :rtype: list

        :raises Exception: on general exception

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_id_": <str>,
                        "dataset_id_": <int>,
                        "part_numbers_": <list>, (if defined)
                        "products_": [
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
                    },
                    {...}
                ]
            else:
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

        """

        try:
            return self.get_queryset().retrieve_vehicles_by_product_data_from_api(
                part_numbers=part_numbers,
                annotated=annotated
            )
        except Exception:
            raise

    def retrieve_vehicles_by_brand_data_from_api(self, annotated=False):
        """
        Retrieves datasets vehicles by brand data from SEMA API.

        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: datasets vehicles by brand data
        :rtype: list

        :raises Exception: on general exception

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_id_": <str>,
                        "dataset_id_": <int>,
                        "vehicles_": [
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
                    },
                    {...}
                ]
            else:
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

        try:
            return self.get_queryset().retrieve_vehicles_by_brand_data_from_api(
                annotated=annotated
            )
        except Exception:
            raise
    # </editor-fold>

    # <editor-fold desc="import properties ...">
    def parse_api_data(self, data):
        """
        Returns object PK and field/value dictionary from API data item.

        :param data: API data item
        :type data: dict

        :return: object PK and field/value dictionary
        :rtype: tuple

        :raises Exception: on general exception

        **-Expected Data Format-**
        ::
            data = {
                "AAIABrandId": <str>,
                "DatasetId": <int>,
                "DatasetName": <str>
            }

        **-Return Format-**
        ::
            pk = <int>
            fields = {
                "is_authorized": <bool>,
                "name": <str>,
                "brand_id": <str>
            }

        """

        try:
            pk = data['DatasetId']
            fields = {
                'is_authorized': True,
                'name': data['DatasetName'],
                'brand_id': data['AAIABrandId']
            }
            return pk, fields
        except Exception:
            raise
    # </editor-fold>

    # <editor-fold desc="unauthorize properties ...">
    def get_pk_list_from_api_data(self, data):
        """
        Returns a list of object PKs from full API data.

        :param data: API data
        :type data: list

        :return: list of PKs
        :rtype: list

        :raises Exception: on general exception

        **-Expected Data Format-**
        ::
            data = [
                {
                    "DatasetId": <int>
                },
                {..}
            ]

        **-Return Format-**
        ::
            ret = [
                <int>,
                ...
            ]

        """

        try:
            return [item['DatasetId'] for item in data]
        except Exception:
            raise
    # </editor-fold>

    # <editor-fold desc="perform properties ...">
    def perform_dataset_categories_update_from_api(self, **filters):
        msgs = []
        try:
            msgs += self.get_queryset().perform_dataset_categories_update_from_api(
                **filters
            )
        except Exception as err:
            msgs.append(self.model.get_class_error_msg(str(err)))

        if not msgs:
            msgs.append(self.model.get_class_up_to_date_msg())
        return msgs

    def perform_dataset_vehicles_update_from_api(self):
        msgs = []
        try:
            msgs += self.get_queryset().perform_dataset_vehicles_update_from_api()
        except Exception as err:
            msgs.append(self.model.get_class_error_msg(str(err)))

        if not msgs:
            msgs.append(self.model.get_class_up_to_date_msg())
        return msgs
    # </editor-fold>


class SemaYearManager(SemaBaseManager):
    """
    This manager class defines SEMA vehicle year methods.

    """

    def get_queryset(self):
        return SemaYearQuerySet(
            self.model,
            using=self._db
        )

    def with_admin_data(self):
        return self.get_queryset().with_admin_data()

    def with_year_data(self):
        """
        Retrieves queryset and annotates decade field.

        :return: annotated queryset
        :rtype: django.db.models.QuerySet

        """

        return self.get_queryset().with_year_data()

    # <editor-fold desc="retrieve properties ...">
    def retrieve_data_from_api(self, brand_ids=None,
                               dataset_ids=None):
        """
        Retrieves year data from SEMA API.

        :param brand_ids: brand IDs to on which to filter
        :type brand_ids: list
        :param dataset_ids: dataset IDs to on which to filter
        :type dataset_ids: list

        :return: year data
        :rtype: list

        :raises Exception: on general exception

        .. Topic:: **-Parameters-**

            Only one of `brand_ids` or `dataset_ids` allowed

        **-Return Format-**
        ::
            ret = [
                <int>,
                ...
            ]

        """

        try:
            return sema_client.retrieve_years(
                brand_ids=brand_ids,
                dataset_ids=dataset_ids
            )
        except Exception:
            raise

    def retrieve_makes_data_from_api(self, brand_ids=None,
                                     dataset_ids=None, annotated=False):
        """
        Retrieves years makes data from SEMA API.

        :param brand_ids: brand IDs on which to filter
        :type brand_ids: list
        :param dataset_ids: dataset IDs on which to filter
        :type dataset_ids: list
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: years makes data
        :rtype: list

        :raises Exception: on general exception

        .. Topic:: **-Parameters-**

            Only one of `brand_ids` or `dataset_ids` allowed

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_ids_": <str>, (if defined)
                        "dataset_ids_": <int>, (if defined)
                        "year_": <int>
                        "makes_": [
                            {
                                "MakeID": <int>,
                                "MakeName": <str>
                            },
                            {...}
                        ]
                    }
                ]
            else:
                ret = [
                    {
                        "MakeID": <int>,
                        "MakeName": <str>
                    },
                    {...}
            ]

        """

        try:
            return self.get_queryset().retrieve_makes_data_from_api(
                brand_ids=brand_ids,
                dataset_ids=dataset_ids,
                annotated=annotated
            )
        except Exception:
            raise

    def retrieve_models_data_from_api(self, brand_ids=None, dataset_ids=None,
                                      make_id=None, annotated=False):
        """
        Retrieves years models data from SEMA API.

        :param brand_ids: brand IDs on which to filter
        :type brand_ids: list
        :param dataset_ids: dataset IDs on which to filter
        :type dataset_ids: list
        :param make_id: make ID on which to filter
        :type make_id: int
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: years models data
        :rtype: list

        :raises Exception: on general exception

        .. Topic:: **-Parameters-**

            Only one of `brand_ids` or `dataset_ids` allowed

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_ids_": <list>, (if defined)
                        "dataset_ids_": <list>, (if defined)
                        "year_": <int>,
                        "make_id_": <int>, (if defined)
                        "models_": [
                            {
                                "BaseVehicleID": <int>,
                                "ModelID": <int>,
                                "ModelName": <str>
                            },
                            {...}
                        ]
                    }
                ]
            else:
                ret = [
                    {
                        "BaseVehicleID": <int>,
                        "ModelID": <int>,
                        "ModelName": <str>
                    },
                    {...}
            ]

        """

        try:
            return self.get_queryset().retrieve_models_data_from_api(
                brand_ids=brand_ids,
                dataset_ids=dataset_ids,
                make_id=make_id,
                annotated=annotated
            )
        except Exception:
            raise

    def retrieve_submodels_data_from_api(self, brand_ids=None,
                                         dataset_ids=None, make_id=None,
                                         model_id=None, annotated=False):
        """
        Retrieves years submodels data from SEMA API.

        :param brand_ids: brand IDs on which to filter
        :type brand_ids: list
        :param dataset_ids: dataset IDs on which to filter
        :type dataset_ids: list
        :param make_id: make ID on which to filter
        :type make_id: int
        :param model_id: model ID on which to filter
        :type model_id: int
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: years submodels data
        :rtype: list

        :raises Exception: on general exception

        .. Topic:: **-Parameters-**

            Only one of `brand_ids` or `dataset_ids` allowed

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_ids_": <list>, (if defined)
                        "dataset_ids_": <list>, (if defined)
                        "year_": <int>,
                        "make_id_": <int>, (if defined)
                        "model_id_": <int>, (if defined)
                        "submodels_": [
                            {
                                "VehicleID": <int>,
                                "SubmodelID": <int>,
                                "SubmodelName": <str>
                            },
                            {...}
                        ]
                    }
                ]
            else:
                ret = [
                    {
                        "VehicleID": <int>,
                        "SubmodelID": <int>,
                        "SubmodelName": <str>
                    },
                    {...}
            ]

        """

        try:
            return self.get_queryset().retrieve_submodels_data_from_api(
                brand_ids=brand_ids,
                dataset_ids=dataset_ids,
                make_id=make_id,
                model_id=model_id,
                annotated=annotated
            )
        except Exception:
            raise

    def retrieve_engines_data_from_api(self, brand_ids=None, dataset_ids=None,
                                       make_id=None, model_id=None,
                                       annotated=False):
        """
        Retrieves years engines data from SEMA API.

        :param brand_ids: brand IDs on which to filter
        :type brand_ids: list
        :param dataset_ids: dataset IDs on which to filter
        :type dataset_ids: list
        :param make_id: make ID on which to filter
        :type make_id: int
        :param model_id: model ID on which to filter
        :type model_id: int
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: years engines data
        :rtype: list

        :raises Exception: on general exception

        .. Topic:: **-Parameters-**

            Only one of `brand_ids` or `dataset_ids` allowed

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_ids_": <list>, (if defined)
                        "dataset_ids_": <list>, (if defined)
                        "year_": <int>,
                        "make_id_": <int>, (if defined)
                        "model_id_": <int>, (if defined)
                        "engines_": [
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
                    },
                    {...}
                ]
            else:
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

        try:
            return self.get_queryset().retrieve_engines_data_from_api(
                brand_ids=brand_ids,
                dataset_ids=dataset_ids,
                make_id=make_id,
                model_id=model_id,
                annotated=annotated
            )
        except Exception:
            raise
    # </editor-fold>

    # <editor-fold desc="import properties ...">
    def parse_api_data(self, data):
        """
        Returns object PK and field/value dictionary from API data item.

        :param data: API data item
        :type data: dict

        :return: object PK and field/value dictionary
        :rtype: tuple

        **-Expected Data Format-**
        ::
            data = <int>

        **-Return Format-**
        ::
            pk = <int>
            fields = {
                "is_authorized": <bool>
            }

        """

        pk = data
        fields = {
            'is_authorized': True
        }
        return data, fields
    # </editor-fold>

    # <editor-fold desc="unauthorize properties ...">
    def get_pk_list_from_api_data(self, data):
        """
        Returns a list of object PKs from full API data.

        :param data: API data
        :type data: list

        :return: list of PKs
        :rtype: list

        :raises Exception: on general exception

        **-Expected Data Format-**
        ::
            data = [
                <int>,
                ...
            ]

        **-Return Format-**
        ::
            ret = [
                <int>,
                ...
            ]

        """

        return data
    # </editor-fold>


class SemaMakeManager(SemaBaseManager):
    """
    This manager class defines SEMA vehicle make methods.

    """

    def get_queryset(self):
        return SemaMakeQuerySet(
            self.model,
            using=self._db
        )

    def with_admin_data(self):
        return self.get_queryset().with_admin_data()

    def get_or_create_by_names(self, make_name):
        try:
            make = self.get(name=make_name)
            created = False
        except self.model.DoesNotExist:
            pk = randint(1000000, 9999999)
            while self.model.objects.filter(pk=pk).exists():
                pk = randint(1000000, 9999999)
            make = self.create(
                make_id=pk,
                name=make_name,
                is_authorized=False
            )
            created = True
            print(f'Created unauthorized make {make}')
        return make, created

    # <editor-fold desc="retrieve properties ...">
    def retrieve_data_from_api(self, brand_ids=None,
                               dataset_ids=None, year=None):
        """
        Retrieves make data from SEMA API.

        :param brand_ids: brand IDs to on which to filter
        :type brand_ids: list
        :param dataset_ids: dataset IDs to on which to filter
        :type dataset_ids: list
        :param year: year on which to filter
        :type year: int

        :return: make data
        :rtype: list

        :raises Exception: on general exception

        .. Topic:: **-Parameters-**

            Only one of `brand_ids` or `dataset_ids` allowed

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

        try:
            return sema_client.retrieve_makes(
                brand_ids=brand_ids,
                dataset_ids=dataset_ids,
                year=year
            )
        except Exception:
            raise

    def retrieve_models_data_from_api(self, brand_ids=None, dataset_ids=None,
                                      year=None, annotated=False):
        """
        Retrieves makes models data from SEMA API.

        :param brand_ids: brand IDs on which to filter
        :type brand_ids: list
        :param dataset_ids: dataset IDs on which to filter
        :type dataset_ids: list
        :param year: year on which to filter
        :type year: int
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: makes models data
        :rtype: list

        :raises Exception: on general exception

        .. Topic:: **-Parameters-**

            Only one of `brand_ids` or `dataset_ids` allowed

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_ids_": <list>, (if defined)
                        "dataset_ids_": <list>, (if defined)
                        "year_": <int>, (if defined)
                        "make_id_": <int>,
                        "models_": [
                            {
                                "BaseVehicleID": <int>,
                                "ModelID": <int>,
                                "ModelName": <str>
                            },
                            {...}
                        ]
                    }
                ]
            else:
                ret = [
                    {
                        "BaseVehicleID": <int>,
                        "ModelID": <int>,
                        "ModelName": <str>
                    },
                    {...}
            ]

        """

        try:
            return self.get_queryset().retrieve_models_data_from_api(
                brand_ids=brand_ids,
                dataset_ids=dataset_ids,
                year=year,
                annotated=annotated
            )
        except Exception:
            raise

    def retrieve_submodels_data_from_api(self, brand_ids=None,
                                         dataset_ids=None, year=None,
                                         model_id=None, annotated=False):
        """
        Retrieves makes submodels data from SEMA API.

        :param brand_ids: brand IDs on which to filter
        :type brand_ids: list
        :param dataset_ids: dataset IDs on which to filter
        :type dataset_ids: list
        :param year: year on which to filter
        :type year: int
        :param model_id: model ID on which to filter
        :type model_id: int
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: makes submodels data
        :rtype: list

        :raises Exception: on general exception

        .. Topic:: **-Parameters-**

            Only one of `brand_ids` or `dataset_ids` allowed

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_ids_": <list>, (if defined)
                        "dataset_ids_": <list>, (if defined)
                        "year_": <int>, (if defined)
                        "make_id_": <int>,
                        "model_id_": <int>, (if defined)
                        "submodels_": [
                            {
                                "VehicleID": <int>,
                                "SubmodelID": <int>,
                                "SubmodelName": <str>
                            },
                            {...}
                        ]
                    }
                ]
            else:
                ret = [
                    {
                        "VehicleID": <int>,
                        "SubmodelID": <int>,
                        "SubmodelName": <str>
                    },
                    {...}
            ]

        """

        try:
            return self.get_queryset().retrieve_submodels_data_from_api(
                brand_ids=brand_ids,
                dataset_ids=dataset_ids,
                year=year,
                model_id=model_id,
                annotated=annotated
            )
        except Exception:
            raise

    def retrieve_engines_data_from_api(self, brand_ids=None, dataset_ids=None,
                                       year=None, model_id=None,
                                       annotated=False):
        """
        Retrieves makes engines data from SEMA API.

        :param brand_ids: brand IDs on which to filter
        :type brand_ids: list
        :param dataset_ids: dataset IDs on which to filter
        :type dataset_ids: list
        :param year: year on which to filter
        :type year: int
        :param model_id: model ID on which to filter
        :type model_id: int
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: makes engines data
        :rtype: list

        :raises Exception: on general exception

        .. Topic:: **-Parameters-**

            Only one of `brand_ids` or `dataset_ids` allowed

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_ids_": <list>, (if defined)
                        "dataset_ids_": <list>, (if defined)
                        "year_": <int>, (if defined)
                        "make_id_": <int>,
                        "model_id_": <int>, (if defined)
                        "engines_": [
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
                    },
                    {...}
                ]
            else:
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

        try:
            return self.get_queryset().retrieve_engines_data_from_api(
                brand_ids=brand_ids,
                dataset_ids=dataset_ids,
                year=year,
                model_id=model_id,
                annotated=annotated
            )
        except Exception:
            raise
    # </editor-fold>

    # <editor-fold desc="import properties ...">
    def parse_api_data(self, data):
        """
        Returns object PK and field/value dictionary from API data item.

        :param data: API data item
        :type data: dict

        :return: object PK and field/value dictionary
        :rtype: tuple

        :raises Exception: on general exception

        **-Expected Data Format-**
        ::
            data = {
                "MakeID": <int>,
                "MakeName": <str>
            }

        **-Return Format-**
        ::
            pk = <int>
            fields = {
                "is_authorized": <bool>,
                "name": <str>
            }

        """

        try:
            pk = data['MakeID']
            fields = {
                'is_authorized': True,
                'name': data['MakeName']
            }
            return pk, fields
        except Exception:
            raise
    # </editor-fold>

    # <editor-fold desc="unauthorize properties ...">
    def get_pk_list_from_api_data(self, data):
        """
        Returns a list of object PKs from full API data.

        :param data: API data
        :type data: list

        :return: list of PKs
        :rtype: list

        :raises Exception: on general exception

        **-Expected Data Format-**
        ::
            data = [
                {
                    "MakeID": <int>
                },
                {..}
            ]

        **-Return Format-**
        ::
            ret = [
                <int>,
                ...
            ]

        """

        try:
            return [item['MakeID'] for item in data]
        except Exception:
            raise
    # </editor-fold>


class SemaModelManager(SemaBaseManager):
    """
    This manager class defines SEMA vehicle model methods.

    """

    def get_queryset(self):
        return SemaModelQuerySet(
            self.model,
            using=self._db
        )

    def with_admin_data(self):
        return self.get_queryset().with_admin_data()

    def get_or_create_by_names(self, model_name):
        try:
            model = self.get(name=model_name)
            created = False
        except MultipleObjectsReturned:
            raise
        except self.model.DoesNotExist:
            pk = randint(1000000, 9999999)
            while self.model.objects.filter(pk=pk).exists():
                pk = randint(1000000, 9999999)
            model = self.create(
                model_id=pk,
                name=model_name,
                is_authorized=False
            )
            created = True
            print(f'Created unauthorized model {model}')
        return model, created

    # <editor-fold desc="retrieve properties ...">
    def retrieve_data_from_api(self, brand_ids=None, dataset_ids=None,
                               year=None, make_id=None):
        """
        Retrieves model data from SEMA API.

        :param brand_ids: brand IDs to on which to filter
        :type brand_ids: list
        :param dataset_ids: dataset IDs to on which to filter
        :type dataset_ids: list
        :param year: year on which to filter
        :type year: int
        :param make_id: make ID on which to filter
        :type make_id: int

        :return: model data
        :rtype: list

        :raises Exception: on general exception

        .. Topic:: **-Parameters-**

            Only one of `brand_ids` or `dataset_ids` allowed

        **-Return Format-**
        ::
            ret = [
                {
                    "ModelID": <int>,
                    "ModelName": <str>
                },
                {...}
            ]

        """

        try:
            data = sema_client.retrieve_models(
                brand_ids=brand_ids,
                dataset_ids=dataset_ids,
                year=year,
                make_id=make_id
            )
            for item in data:
                del item['BaseVehicleID']
            return data
        except Exception:
            raise

    def retrieve_submodels_data_from_api(self, brand_ids=None,
                                         dataset_ids=None, year=None,
                                         make_id=None, annotated=False):
        """
        Retrieves models submodels data from SEMA API.

        :param brand_ids: brand IDs on which to filter
        :type brand_ids: list
        :param dataset_ids: dataset IDs on which to filter
        :type dataset_ids: list
        :param year: year on which to filter
        :type year: int
        :param make_id: make ID on which to filter
        :type make_id: int
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: models submodels data
        :rtype: list

        :raises Exception: on general exception

        .. Topic:: **-Parameters-**

            Only one of `brand_ids` or `dataset_ids` allowed

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_ids_": <list>, (if defined)
                        "dataset_ids_": <list>, (if defined)
                        "year_": <int>, (if defined)
                        "make_id_": <int>, (if defined)
                        "model_id_": <int>,
                        "submodels_": [
                            {
                                "VehicleID": <int>,
                                "SubmodelID": <int>,
                                "SubmodelName": <str>
                            },
                            {...}
                        ]
                    }
                ]
            else:
                ret = [
                    {
                        "VehicleID": <int>,
                        "SubmodelID": <int>,
                        "SubmodelName": <str>
                    },
                    {...}
            ]

        """

        try:
            return self.get_queryset().retrieve_submodels_data_from_api(
                brand_ids=brand_ids,
                dataset_ids=dataset_ids,
                year=year,
                make_id=make_id,
                annotated=annotated
            )
        except Exception:
            raise

    def retrieve_engines_data_from_api(self, brand_ids=None, dataset_ids=None,
                                       year=None, make_id=None,
                                       annotated=False):
        """
        Retrieves models engines data from SEMA API.

        :param brand_ids: brand IDs on which to filter
        :type brand_ids: list
        :param dataset_ids: dataset IDs on which to filter
        :type dataset_ids: list
        :param year: year on which to filter
        :type year: int
        :param make_id: make ID on which to filter
        :type make_id: int
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: models engines data
        :rtype: list

        :raises Exception: on general exception

        .. Topic:: **-Parameters-**

            Only one of `brand_ids` or `dataset_ids` allowed

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_ids_": <list>, (if defined)
                        "dataset_ids_": <list>, (if defined)
                        "year_": <int>, (if defined)
                        "make_id_": <int>, (if defined)
                        "model_id_": <int>,
                        "engines_": [
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
                    },
                    {...}
                ]
            else:
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

        try:
            return self.get_queryset().retrieve_engines_data_from_api(
                brand_ids=brand_ids,
                dataset_ids=dataset_ids,
                year=year,
                make_id=make_id,
                annotated=annotated
            )
        except Exception:
            raise
    # </editor-fold>

    # <editor-fold desc="import properties ...">
    def parse_api_data(self, data):
        """
        Returns object PK and field/value dictionary from API data item.

        :param data: API data item
        :type data: dict

        :return: object PK and field/value dictionary
        :rtype: tuple

        :raises Exception: on general exception

        **-Expected Data Format-**
        ::
            data = {
                "ModelID": <int>,
                "ModelName": <str>
            }

        **-Return Format-**
        ::
            pk = <int>
            fields = {
                "is_authorized": <bool>,
                "name": <str>
            }

        """

        try:
            pk = data['ModelID']
            fields = {
                'is_authorized': True,
                'name': data['ModelName']
            }
            return pk, fields
        except Exception:
            raise
    # </editor-fold>

    # <editor-fold desc="unauthorize properties ...">
    def get_pk_list_from_api_data(self, data):
        """
        Returns a list of object PKs from full API data.

        :param data: API data
        :type data: list

        :return: list of PKs
        :rtype: list

        :raises Exception: on general exception

        **-Expected Data Format-**
        ::
            data = [
                {
                    "ModelID": <int>
                },
                {..}
            ]

        **-Return Format-**
        ::
            ret = [
                <int>,
                ...
            ]

        """

        try:
            return [item['ModelID'] for item in data]
        except Exception:
            raise
    # </editor-fold>


class SemaSubmodelManager(SemaBaseManager):
    """
    This manager class defines SEMA vehicle submodel methods.

    """

    def get_queryset(self):
        return SemaSubmodelQuerySet(
            self.model,
            using=self._db
        )

    def with_admin_data(self):
        return self.get_queryset().with_admin_data()

    def get_or_create_by_names(self, submodel_name):
        try:
            submodel = self.get(name=submodel_name)
            created = False
        except self.model.DoesNotExist:
            pk = randint(1000000, 9999999)
            while self.model.objects.filter(pk=pk).exists():
                pk = randint(1000000, 9999999)
            submodel = self.create(
                submodel_id=pk,
                name=submodel_name,
                is_authorized=False
            )
            created = True
            print(f'Created unauthorized submodel {submodel_name}')
        return submodel, created

    # <editor-fold desc="retrieve properties ...">
    def retrieve_data_from_api(self, brand_ids=None, dataset_ids=None,
                               year=None, make_id=None, model_id=None):
        """
        Retrieves submodel data from SEMA API.

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

        :return: submodel data
        :rtype: list

        :raises Exception: on general exception

        .. Topic:: **-Parameters-**

            Only one of `brand_ids` or `dataset_ids` allowed

        **-Return Format-**
        ::
            ret = [
                {
                    "SubmodelID": <int>,
                    "SubmodelName": <str>
                },
                {...}
            ]

        """

        try:
            data = sema_client.retrieve_submodels()
            for item in data:
                del item['VehicleID']
            return data
        except Exception:
            raise
    # </editor-fold>

    # <editor-fold desc="import properties ...">
    def parse_api_data(self, data):
        """
        Returns object PK and field/value dictionary from API data item.

        :param data: API data item
        :type data: dict

        :return: object PK and field/value dictionary
        :rtype: tuple

        :raises Exception: on general exception

        **-Expected Data Format-**
        ::
            data = {
                "SubmodelID": <int>,
                "SubmodelName": <str>
            }

        **-Return Format-**
        ::
            pk = <int>
            fields = {
                "is_authorized": <bool>,
                "name": <str>
            }

        """

        try:
            pk = data['SubmodelID']
            fields = {
                'is_authorized': True,
                'name': data['SubmodelName']
            }
            return pk, fields
        except Exception:
            raise
    # </editor-fold>

    # <editor-fold desc="unauthorize properties ...">
    def get_pk_list_from_api_data(self, data):
        """
        Returns a list of object PKs from full API data.

        :param data: API data
        :type data: list

        :return: list of PKs
        :rtype: list

        :raises Exception: on general exception

        **-Expected Data Format-**
        ::
            data = [
                {
                    "SubmodelID": <int>
                },
                {..}
            ]

        **-Return Format-**
        ::
            ret = [
                <int>,
                ...
            ]

        """

        try:
            return [item['SubmodelID'] for item in data]
        except Exception:
            raise
    # </editor-fold>


class SemaMakeYearManager(SemaBaseManager):
    """
    This manager class defines SEMA vehicle make year methods.

    """

    def get_queryset(self):
        return SemaMakeYearQuerySet(
            self.model,
            using=self._db
        )

    def with_admin_data(self):
        return self.get_queryset().with_admin_data()

    def get_by_ids(self, year, make_id):
        """
        Returns make year object by year and make id.

        :type year: int
        :type make_id: int
        :rtype: object

        :raises: Exception on get exception

        """

        try:
            return self.get(
                year__year=year,
                make__make_id=make_id
            )
        except Exception:
            raise

    def get_by_names(self, year, make_name):
        """
        Returns make year object by year and make name.

        :type year: int
        :type make_name: str
        :rtype: object

        :raises: Exception on get exception

        """

        try:
            return self.get(
                year__year=year,
                make__name=make_name
            )
        except Exception:
            raise

    def get_or_create_by_names(self, year, make_name):
        try:
            make_year = self.get_by_names(
                year=year,
                make_name=make_name
            )
            created = False
        except self.model.DoesNotExist:
            from sema.models import SemaYear, SemaMake
            year, created = SemaYear.objects.get_or_create(year=year)
            if created:
                print(f'Created unauthorized year {year}')
            make, _ = SemaMake.objects.get_or_create_by_names(
                make_name=make_name
            )
            make_year = self.create(
                year=year,
                make=make,
                is_authorized=False
            )
            created = True
            print(f'Created unauthorized make year {make_year}')
        return make_year, created

    # <editor-fold desc="retrieve properties ...">
    def retrieve_data_from_api(self, years, brand_ids=None,
                               dataset_ids=None, annotated=False):
        """
        Retrieves make year data from SEMA API.

        :param years: year queryset with which to retrieve
        :type years: django.db.models.QuerySet
        :param brand_ids: brand IDs to on which to filter
        :type brand_ids: list
        :param dataset_ids: dataset IDs to on which to filter
        :type dataset_ids: list
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: make year data
        :rtype: list

        :raises Exception: on general exception

        .. Topic:: **-Parameters-**

            Only one of `brand_ids` or `dataset_ids` allowed

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_ids_": <str>, (if defined)
                        "dataset_ids_": <int>, (if defined)
                        "year_": <int>,
                        "makes_": [
                            {
                                "MakeID": <int>,
                                "MakeName": <str>
                            },
                            {...}
                        ]
                    }
                ]
            else:
                ret = [
                    {
                        "MakeID": <int>,
                        "MakeName": <str>
                    },
                    {...}
            ]

        """

        try:
            return years.retrieve_makes_data_from_api(
                brand_ids=brand_ids,
                dataset_ids=dataset_ids,
                annotated=annotated
            )
        except Exception:
            raise

    def retrieve_models_data_from_api(self, brand_ids=None,
                                      dataset_ids=None, annotated=False):
        """
        Retrieves make years models data from SEMA API.

        :param brand_ids: brand IDs on which to filter
        :type brand_ids: list
        :param dataset_ids: dataset IDs on which to filter
        :type dataset_ids: list
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: make years models data
        :rtype: list

        :raises Exception: on general exception

        .. Topic:: **-Parameters-**

            Only one of `brand_ids` or `dataset_ids` allowed

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_ids_": <list>, (if defined)
                        "dataset_ids_": <list>, (if defined)
                        "make_year_id_" <int>,
                        "year_": <int>,
                        "make_id_": <int>,
                        "models_": [
                            {
                                "BaseVehicleID": <int>,
                                "ModelID": <int>,
                                "ModelName": <str>
                            },
                            {...}
                        ]
                    }
                ]
            else:
                ret = [
                    {
                        "BaseVehicleID": <int>,
                        "ModelID": <int>,
                        "ModelName": <str>
                    },
                    {...}
            ]

        """

        try:
            return self.get_queryset().retrieve_models_data_from_api(
                brand_ids=brand_ids,
                dataset_ids=dataset_ids,
                annotated=annotated
            )
        except Exception:
            raise

    def retrieve_submodels_data_from_api(self, brand_ids=None,
                                         dataset_ids=None, model_id=None,
                                         annotated=False):
        """
        Retrieves make years submodels data from SEMA API.

        :param brand_ids: brand IDs on which to filter
        :type brand_ids: list
        :param dataset_ids: dataset IDs on which to filter
        :type dataset_ids: list
        :param model_id: model ID on which to filter
        :type model_id: int
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: make years submodels data
        :rtype: list

        :raises Exception: on general exception

        .. Topic:: **-Parameters-**

            Only one of `brand_ids` or `dataset_ids` allowed

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_ids_": <list>, (if defined)
                        "dataset_ids_": <list>, (if defined)
                        "make_year_id_": <int>,
                        "year_": <int>,
                        "make_id_": <int>,
                        "model_id_": <int>, (if defined)
                        "submodels_": [
                            {
                                "VehicleID": <int>,
                                "SubmodelID": <int>,
                                "SubmodelName": <str>
                            },
                            {...}
                        ]
                    }
                ]
            else:
                ret = [
                    {
                        "VehicleID": <int>,
                        "SubmodelID": <int>,
                        "SubmodelName": <str>
                    },
                    {...}
            ]

        """

        try:
            return self.get_queryset().retrieve_submodels_data_from_api(
                brand_ids=brand_ids,
                dataset_ids=dataset_ids,
                model_id=model_id,
                annotated=annotated
            )
        except Exception:
            raise

    def retrieve_engines_data_from_api(self, brand_ids=None, dataset_ids=None,
                                       model_id=None, annotated=False):
        """
        Retrieves make years engines data from SEMA API.

        :param brand_ids: brand IDs on which to filter
        :type brand_ids: list
        :param dataset_ids: dataset IDs on which to filter
        :type dataset_ids: list
        :param model_id: model ID on which to filter
        :type model_id: int
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: make years engines data
        :rtype: list

        :raises Exception: on general exception

        .. Topic:: **-Parameters-**

            Only one of `brand_ids` or `dataset_ids` allowed

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_ids_": <list>, (if defined)
                        "dataset_ids_": <list>, (if defined)
                        "make_year_id_": <int>,
                        "year_": <int>,
                        "make_id_": <int>,
                        "model_id_": <int>, (if defined)
                        "engines_": [
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
                    },
                    {...}
                ]
            else:
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

        try:
            return self.get_queryset().retrieve_engines_data_from_api(
                brand_ids=brand_ids,
                dataset_ids=dataset_ids,
                model_id=model_id,
                annotated=annotated
            )
        except Exception:
            raise
    # </editor-fold>

    # <editor-fold desc="import properties ...">
    def get_retrieve_data_from_api_params(self, **params):
        """
        Returns params with additional params years as authorized years
        queryset if not already defined and annotated as true.

        :param params: param kwargs to which to add additional params

        :return: param kwargs
        :rtype: dict

        :raises Exception: on general exception

        """

        try:
            if 'years' not in params:
                from sema.models import SemaYear
                years = SemaYear.objects.filter(is_authorized=True)
                params['years'] = years
            params['annotated'] = True
            return params
        except Exception:
            raise

    def flatten_api_data(self, data):
        """
        Flattens nested data and returns relevant key/values.

        :param data: API data
        :type data: list

        :return: flat API data
        :rtype: list

        :raises Exception: on general exception

        **-Expected Data Format-**
        ::
            data = [
                {
                    "year_": <int>
                    "makes_": [
                        {
                            "MakeID": <int>
                        },
                        {...}
                    ]
                }
            ]

        **-Return Format-**
        ::
            data = [
                {
                    "year_": <int>,
                    "MakeID": <int>
                },
                {...}
            ]

        """

        try:
            flattened_data = []
            for year in data:
                for make in year['makes_']:
                    flattened_data.append(
                        {
                            'year_': year['year_'],
                            'MakeID': make['MakeID']
                        }
                    )
            return flattened_data
        except Exception:
            raise

    def parse_api_data(self, data):
        """
        Returns NoneType (because PK is not defined in API data) and
        field/value dictionary from API data item.

        :param data: API data item
        :type data: dict

        :return: object PK and field/value dictionary
        :rtype: tuple

        :raises Exception: on general exception

        **-Expected Data Format-**
        ::
            data = {
                "year_": <int>,
                "MakeID": <int>
            }

        **-Return Format-**
        ::
            pk = None
            fields = {
                "is_authorized": <bool>,
                "year_id": <int>,
                "make_id": <int>
            }

        """

        try:
            fields = {
                'is_authorized': True,
                'year_id': data['year_'],
                'make_id': data['MakeID'],
            }
            return None, fields
        except Exception:
            raise

    def get_object_from_api_data(self, year_id=None, make_id=None, **kwargs):
        """
        Returns object by year and make.

        :param year_id: year ID field value
        :type year_id: int
        :param make_id: make ID field value
        :type make_id: int

        :return: model instance
        :rtype: object

        :raises Exception: missing year_id or make_id, or on general
            exception

        """

        if not (year_id and make_id):
            raise Exception('Year ID and make ID required')

        try:
            return self.get(
                year_id=year_id,
                make_id=make_id
            )
        except Exception:
            raise
    # </editor-fold>

    # <editor-fold desc="unauthorize properties ...">
    def get_pk_list_from_api_data(self, data):
        """
        Returns a list of object PKs from full API data.

        :param data: API data
        :type data: list

        :return: list of PKs
        :rtype: list

        :raises Exception: on general exception

        **-Expected Data Format-**
        ::
            data = [
                {
                    "year_": <int>
                    "MakeID": <int>
                },
                {..}
            ]

        **-Return Format-**
        ::
            ret = [
                <int>,
                ...
            ]

        """

        try:
            pk_list = []
            for item in data:
                try:
                    year_make = self.get(
                        year__year=item['year_'],
                        make__make_id=item['MakeID']
                    )
                    pk_list.append(year_make.pk)
                except self.model.DoesNotExist:
                    pass
            return pk_list
        except Exception:
            raise
    # </editor-fold>


class SemaBaseVehicleManager(SemaBaseManager):
    """
    This manager class defines SEMA base vehicle methods.

    """

    def get_queryset(self):
        return SemaBaseVehicleQuerySet(
            self.model,
            using=self._db
        )

    def with_admin_data(self):
        return self.get_queryset().with_admin_data()

    def get_by_ids(self, year, make_id, model_id):
        """
        Returns base vehicle object by year, make id, and model id.

        :type year: int
        :type make_id: int
        :type model_id: int
        :rtype: object

        :raises: Exception on get exception

        """

        try:
            return self.get(
                make_year__year__year=year,
                make_year__make__make_id=make_id,
                model__model_id=model_id,
            )
        except Exception:
            raise

    def get_by_names(self, year, make_name, model_name):
        """
        Returns base vehicle object by year, make name, and model name.

        :type year: int
        :type make_name: str
        :type model_name: str
        :rtype: object

        :raises: Exception on get exception

        """

        try:
            return self.get(
                make_year__year__year=year,
                make_year__make__name=make_name,
                model__name=model_name
            )
        except Exception:
            raise

    def get_or_create_by_names(self, year, make_name, model_name):
        try:
            base_vehicle = self.get_by_names(
                year=year,
                make_name=make_name,
                model_name=model_name
            )
            created = False
        except self.model.DoesNotExist:
            from sema.models import SemaMakeYear, SemaModel
            make_year, _ = SemaMakeYear.objects.get_or_create_by_names(
                year=year,
                make_name=make_name
            )
            try:
                model, _ = SemaModel.objects.get_or_create_by_names(
                    model_name=model_name
                )
            except MultipleObjectsReturned:  # FIXME
                if make_name == 'Chrysler':
                    model = SemaModel.objects.get(
                        model_id=2489,
                        name=model_name
                    )
                elif make_name == 'GMC':
                    model = SemaModel.objects.get(
                        model_id=21430,
                        name=model_name
                    )
                else:
                    raise
            pk = randint(1000000, 9999999)
            while self.model.objects.filter(pk=pk).exists():
                pk = randint(1000000, 9999999)
            base_vehicle = self.create(
                base_vehicle_id=pk,
                make_year=make_year,
                model=model,
                is_authorized=False
            )
            created = True
            print(f'Created unauthorized base vehicle {base_vehicle}')
        return base_vehicle, created

    # <editor-fold desc="retrieve properties ...">
    def retrieve_data_from_api(self, make_years, brand_ids=None,
                               dataset_ids=None, annotated=False):
        """
        Retrieves base vehicle data from SEMA API.

        :param make_years: make year queryset with which to retrieve
        :type make_years: django.db.models.QuerySet
        :param brand_ids: brand IDs on which to filter
        :type brand_ids: list
        :param dataset_ids: dataset IDs on which to filter
        :type dataset_ids: list
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: base vehicle data
        :rtype: list

        :raises Exception: on general exception

        .. Topic:: **-Parameters-**

            Only one of `brand_ids` or `dataset_ids` allowed

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_ids_": <list>, (if defined)
                        "dataset_ids_": <list>, (if defined)
                        "make_year_id_" <int>,
                        "year_": <int>,
                        "make_id_": <int>,
                        "models_": [
                            {
                                "BaseVehicleID": <int>,
                                "ModelID": <int>,
                                "ModelName": <str>
                            },
                            {...}
                        ]
                    }
                ]
            else:
                ret = [
                    {
                        "BaseVehicleID": <int>,
                        "ModelID": <int>,
                        "ModelName": <str>
                    },
                    {...}
            ]

        """

        try:
            return make_years.retrieve_models_data_from_api(
                brand_ids=brand_ids,
                dataset_ids=dataset_ids,
                annotated=annotated
            )
        except Exception:
            raise

    def retrieve_submodels_data_from_api(self, brand_ids=None,
                                         dataset_ids=None, annotated=False):
        """
        Retrieves base vehicles submodels data from SEMA API.

        :param brand_ids: brand IDs on which to filter
        :type brand_ids: list
        :param dataset_ids: dataset IDs on which to filter
        :type dataset_ids: list
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: base vehicles submodels data
        :rtype: list

        :raises Exception: on general exception

        .. Topic:: **-Parameters-**

            Only one of `brand_ids` or `dataset_ids` allowed

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_ids_": <list>, (if defined)
                        "dataset_ids_": <list>, (if defined)
                        "base_vehicle_id_": <int>,
                        "year_": <int>,
                        "make_id_": <int>,
                        "model_id_": <int>,
                        "submodels_": [
                            {
                                "VehicleID": <int>,
                                "SubmodelID": <int>,
                                "SubmodelName": <str>
                            },
                            {...}
                        ]
                    }
                ]
            else:
                ret = [
                    {
                        "VehicleID": <int>,
                        "SubmodelID": <int>,
                        "SubmodelName": <str>
                    },
                    {...}
            ]

        """

        try:
            return self.get_queryset().retrieve_submodels_data_from_api(
                brand_ids=brand_ids,
                dataset_ids=dataset_ids,
                annotated=annotated
            )
        except Exception:
            raise

    def retrieve_engines_data_from_api(self, brand_ids=None,
                                       dataset_ids=None, annotated=False):
        """
        Retrieves base vehicles engines data from SEMA API.

        :param brand_ids: brand IDs on which to filter
        :type brand_ids: list
        :param dataset_ids: dataset IDs on which to filter
        :type dataset_ids: list
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: base vehicles engines data
        :rtype: list

        :raises Exception: on general exception

        .. Topic:: **-Parameters-**

            Only one of `brand_ids` or `dataset_ids` allowed

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_ids_": <list>, (if defined)
                        "dataset_ids_": <list>, (if defined)
                        "base_vehicle_id_": <int>,
                        "year_": <int>,
                        "make_id_": <int>,
                        "model_id_": <int>,
                        "engines_": [
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
                    }
                ]
            else:
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

        try:
            return self.get_queryset().retrieve_engines_data_from_api(
                brand_ids=brand_ids,
                dataset_ids=dataset_ids,
                annotated=annotated
            )
        except Exception:
            raise

    def retrieve_vehicle_info_data_from_api(self, annotated=False):
        """
        Retrieves base vehicles vehicle info data from SEMA API.

        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: base vehicles vehicle info data
        :rtype: list

        :raises Exception: on general exception

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "base_vehicle_id_": <int>,
                        "vehicles_": [
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
                    },
                    {...}
                ]
            else:
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

        try:
            return self.get_queryset().retrieve_vehicle_info_data_from_api(
                annotated=annotated
            )
        except Exception:
            raise

    def retrieve_categories_data_from_api(self, brand_ids=None,
                                          dataset_ids=None, by_names=False,
                                          annotated=False):
        """
        Retrieves base vehicles categories data from SEMA API.

        :param brand_ids: brand IDs on which to filter
        :type brand_ids: list
        :param dataset_ids: dataset IDs on which to filter
        :type dataset_ids: list
        :param by_names: whether or not to filter by names rather than
            ID
        :type by_names: bool
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: base vehicles categories data
        :rtype: list

        :raises Exception: on general exception

        .. Topic:: **-Parameters-**

            Only one of `brand_ids` or `dataset_ids` allowed

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_ids_": <list>, (if defined)
                        "dataset_ids_": <list>, (if defined)
                        "base_vehicle_id_": <int>,
                        "year_": <int>,
                        "make_id_": <int>,
                        "make_name_": <str>,
                        "model_id_": <int>,
                        "model_name_": <str>,
                        "categories_": [
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
                    }
                ]
            else:
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

        try:
            return self.get_queryset().retrieve_categories_data_from_api(
                brand_ids=brand_ids,
                dataset_ids=dataset_ids,
                by_names=by_names,
                annotated=annotated
            )
        except Exception:
            raise

    def retrieve_products_by_brand_data_from_api(self, brand_ids=None,
                                                 dataset_ids=None,
                                                 part_numbers=None,
                                                 pies_segments=None,
                                                 by_names=False,
                                                 annotated=False):
        """
        Retrieves base vehicles products by brand data from SEMA API.

        :param brand_ids: brand IDs on which to filter
        :type brand_ids: list
        :param dataset_ids: dataset IDs on which to filter
        :type dataset_ids: list
        :param part_numbers: part numbers on which to filter
        :type part_numbers: list
        :param pies_segments: pies segments to include or ['all']
        :type pies_segments: list
        :param by_names: whether or not to filter by names rather than
            ID
        :type by_names: bool
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: base vehicles products data
        :rtype: list

        :raises Exception: on general exception

        .. Topic:: **-Parameters-**

            Only one of `brand_ids` or `dataset_ids` allowed

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_ids_": <list>, (if defined)
                        "dataset_ids_": <list>, (if defined)
                        "base_vehicle_id_": <int>,
                        "year_": <int>,
                        "make_id_": <int>,
                        "make_name_": <str>,
                        "model_id_": <int>,
                        "model_name_": <str>,
                        "part_numbers_": <list>, (if defined)
                        "products_": [
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
                    }
                ]
            else:
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

        try:
            return self.get_queryset().retrieve_products_by_brand_data_from_api(
                brand_ids=brand_ids,
                dataset_ids=dataset_ids,
                part_numbers=part_numbers,
                pies_segments=pies_segments,
                by_names=by_names,
                annotated=annotated
            )
        except Exception:
            raise

    def retrieve_products_by_category_data_from_api(self, category_id,
                                                    brand_ids=None,
                                                    dataset_ids=None,
                                                    part_numbers=None,
                                                    pies_segments=None,
                                                    by_names=False,
                                                    annotated=False):
        """
        Retrieves base vehicles products by category data from SEMA API.

        :param category_id: category ID on which to filter
        :type category_id: int
        :param brand_ids: brand IDs on which to filter
        :type brand_ids: list
        :param dataset_ids: dataset IDs on which to filter
        :type dataset_ids: list
        :param part_numbers: part numbers on which to filter
        :type part_numbers: list
        :param pies_segments: pies segments to include or ['all']
        :type pies_segments: list
        :param by_names: whether or not to filter by names rather than
            ID
        :type by_names: bool
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: base vehicles products by category data
        :rtype: list

        :raises Exception: on general exception

        .. Topic:: **-Parameters-**

            Only one of `brand_ids` or `dataset_ids` allowed

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_ids_": <list>, (if defined)
                        "dataset_ids_": <list>, (if defined)
                        "base_vehicle_id_": <int>,
                        "year_": <int>,
                        "make_id_": <int>,
                        "make_name_": <str>,
                        "model_id_": <int>,
                        "model_name_": <str>,
                        "part_numbers_": <list>, (if defined)
                        "products_": [
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
                    },
                    {...}
                ]
            else:
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

        try:
            return self.get_queryset().retrieve_products_by_category_data_from_api(
                category_id=category_id,
                brand_ids=brand_ids,
                dataset_ids=dataset_ids,
                part_numbers=part_numbers,
                pies_segments=pies_segments,
                by_names=by_names,
                annotated=annotated
            )
        except Exception:
            raise
    # </editor-fold>

    # <editor-fold desc="import properties ...">
    def get_retrieve_data_from_api_params(self, **params):
        """
        Returns params with additional params make_years as authorized
        make years queryset if not already defined and annotated as
        true.

        :param params: param kwargs to which to add additional params

        :return: param kwargs
        :rtype: dict

        :raises Exception: on general exception

        """

        try:
            if 'make_years' not in params:
                from sema.models import SemaMakeYear
                make_years = SemaMakeYear.objects.filter(is_authorized=True)
                params['make_years'] = make_years
            params['annotated'] = True
            return params
        except Exception:
            raise

    def flatten_api_data(self, data):
        """
        Flattens nested data and returns relevant key/values.

        :param data: API data
        :type data: list

        :return: flat API data
        :rtype: list

        :raises Exception: on general exception

        **-Expected Data Format-**
        ::
            data = [
                {
                    "make_year_id_" <int>,
                    "models_": [
                        {
                            "BaseVehicleID": <int>,
                            "ModelID": <int>
                        },
                        {...}
                    ]
                },
                {...}
            ]

        **-Return Format-**
        ::
            data = [
                {
                    "BaseVehicleID": <int>,
                    "make_year_id_": <int>,
                    "ModelID": <int>
                },
                {...}
            ]

        """

        try:
            flattened_data = []
            for make_year in data:
                for model in make_year['models_']:
                    flattened_data.append(
                        {
                            'BaseVehicleID': model['BaseVehicleID'],
                            'make_year_id_': make_year['make_year_id_'],
                            'ModelID': model['ModelID']
                        }
                    )
            return flattened_data
        except Exception:
            raise

    def parse_api_data(self, data):
        """
        Returns object PK and field/value dictionary from API data item.

        :param data: API data item
        :type data: dict

        :return: object PK and field/value dictionary
        :rtype: tuple

        :raises Exception: on general exception

        **-Expected Data Format-**
        ::
            data = {
                "BaseVehicleID": <int>,
                "make_year_id_": <int>,
                "ModelID": <int>
            }

        **-Return Format-**
        ::
            pk = <int>
            fields = {
                "is_authorized": <bool>,
                "make_year_id": <int>,
                "model_id": <int>
            }

        """

        try:
            pk = data['BaseVehicleID']
            fields = {
                'is_authorized': True,
                'make_year_id': data['make_year_id_'],
                'model_id': data['ModelID']
            }
            return pk, fields
        except Exception:
            raise
    # </editor-fold>

    # <editor-fold desc="unauthorize properties ...">
    def get_pk_list_from_api_data(self, data):
        """
        Returns a list of object PKs from full API data.

        :param data: API data
        :type data: list

        :return: list of PKs
        :rtype: list

        :raises Exception: on general exception

        **-Expected Data Format-**
        ::
            data = [
                {
                    "BaseVehicleID": <int>
                },
                {..}
            ]

        **-Return Format-**
        ::
            ret = [
                <int>,
                ...
            ]

        """

        try:
            return [item['BaseVehicleID'] for item in data]
        except Exception:
            raise
    # </editor-fold>


class SemaVehicleManager(SemaBaseManager):
    """
    This manager class defines SEMA vehicle methods.

    """

    def get_queryset(self):
        return SemaVehicleQuerySet(
            self.model,
            using=self._db
        )

    def with_admin_data(self):
        return self.get_queryset().with_admin_data()

    def get_by_ids(self, year, make_id, model_id, submodel_id):
        """
        Returns vehicle object by year, make id, model id, and submodel
        id.

        :type year: int
        :type make_id: int
        :type model_id: int
        :type submodel_id: int
        :rtype: object

        :raises: Exception on get exception

        """

        try:
            return self.get(
                base_vehicle__make_year__year__year=year,
                base_vehicle__make_year__make__make_id=make_id,
                base_vehicle__model__model_id=model_id,
                submodel__submodel_id=submodel_id,
            )
        except Exception:
            raise

    def get_by_names(self, year, make_name, model_name, submodel_name):
        """
        Returns vehicle object by year, make name, model name, and
        submodel name.

        :type year: int
        :type make_name: str
        :type model_name: str
        :type submodel_name: str
        :rtype: object

        :raises: Exception on get exception

        """

        try:
            return self.get(
                base_vehicle__make_year__year__year=year,
                base_vehicle__make_year__make__name=make_name,
                base_vehicle__model__name=model_name,
                submodel__name=submodel_name,
            )
        except Exception:
            raise

    def get_or_create_by_names(self, year, make_name,
                               model_name, submodel_name):
        try:
            vehicle = self.get_by_names(
                year=year,
                make_name=make_name,
                model_name=model_name,
                submodel_name=submodel_name
            )
            created = False
        except self.model.DoesNotExist:
            from sema.models import SemaBaseVehicle, SemaSubmodel
            base_vehicle, _ = SemaBaseVehicle.objects.get_or_create_by_names(
                year=year,
                make_name=make_name,
                model_name=model_name
            )
            submodel, _ = SemaSubmodel.objects.get_or_create_by_names(
                submodel_name=submodel_name
            )
            pk = randint(1000000, 9999999)
            while self.model.objects.filter(pk=pk).exists():
                pk = randint(1000000, 9999999)
            vehicle = self.model.objects.create(
                vehicle_id=pk,
                base_vehicle=base_vehicle,
                submodel=submodel,
                is_authorized=False
            )
            created = True
            print(f'Created unauthorized vehicle {vehicle}')
        return vehicle, created

    # <editor-fold desc="retrieve properties ...">
    def retrieve_data_from_api(self, base_vehicles, brand_ids=None,
                               dataset_ids=None, annotated=False):
        """
        Retrieves vehicle data from SEMA API.

        :param base_vehicles: base vehicle queryset with which to
            retrieve
        :type base_vehicles: django.db.models.QuerySet
        :param brand_ids: brand IDs on which to filter
        :type brand_ids: list
        :param dataset_ids: dataset IDs on which to filter
        :type dataset_ids: list
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: vehicle data
        :rtype: list

        :raises Exception: on general exception

        .. Topic:: **-Parameters-**

            Only one of `brand_ids` or `dataset_ids` allowed

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_ids_": <list>, (if defined)
                        "dataset_ids_": <list>, (if defined)
                        "base_vehicle_id_": <int>,
                        "year_": <int>,
                        "make_id_": <int>,
                        "model_id_": <int>,
                        "submodels_": [
                            {
                                "VehicleID": <int>,
                                "SubmodelID": <int>,
                                "SubmodelName": <str>
                            },
                            {...}
                        ]
                    }
                ]
            else:
                ret = [
                    {
                        "VehicleID": <int>,
                        "SubmodelID": <int>,
                        "SubmodelName": <str>
                    },
                    {...}
            ]

        """

        try:
            return base_vehicles.retrieve_submodels_data_from_api(
                brand_ids=brand_ids,
                dataset_ids=dataset_ids,
                annotated=annotated
            )
        except Exception:
            raise

    def retrieve_vehicle_info_data_from_api(self, annotated=False):
        """
        Retrieves vehicles vehicle info data from SEMA API.

        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: vehicles vehicle info data
        :rtype: list

        :raises Exception: on general exception

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "base_vehicle_id_": <int>,
                        "vehicle_id_": <int>,
                        "vehicles_": [
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
                    },
                    {...}
                ]
            else:
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

        try:
            return self.get_queryset().retrieve_vehicle_info_data_from_api(
                annotated=annotated
            )
        except Exception:
            raise

    def retrieve_categories_data_from_api(self, brand_ids=None,
                                          dataset_ids=None, by_names=False,
                                          annotated=False):
        """
        Retrieves vehicles categories data from SEMA API.

        :param brand_ids: brand IDs on which to filter
        :type brand_ids: list
        :param dataset_ids: dataset IDs on which to filter
        :type dataset_ids: list
        :param by_names: whether or not to filter by names rather than
            ID
        :type by_names: bool
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: vehicles categories data
        :rtype: list

        :raises Exception: on general exception

        .. Topic:: **-Parameters-**

            Only one of `brand_ids` or `dataset_ids` allowed

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_ids_": <list>, (if defined)
                        "dataset_ids_": <list>, (if defined)
                        "base_vehicle_id_": <int>,
                        "vehicle_id_": <int>,
                        "year_": <int>,
                        "make_id_": <int>,
                        "make_name_": <str>,
                        "model_id_": <int>,
                        "model_name_": <str>,
                        "submodel_id_": <int>,
                        "submodel_name_": <str>,
                        "categories_": [
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
                    }
                ]
            else:
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

        try:
            return self.get_queryset().retrieve_categories_data_from_api(
                brand_ids=brand_ids,
                dataset_ids=dataset_ids,
                by_names=by_names,
                annotated=annotated
            )
        except Exception:
            raise

    def retrieve_products_by_brand_data_from_api(self, brand_ids=None,
                                                 dataset_ids=None,
                                                 part_numbers=None,
                                                 pies_segments=None,
                                                 by_names=False,
                                                 annotated=False):
        """
        Retrieves vehicles products by brand data from SEMA API.

        :param brand_ids: brand IDs on which to filter
        :type brand_ids: list
        :param dataset_ids: dataset IDs on which to filter
        :type dataset_ids: list
        :param part_numbers: part numbers on which to filter
        :type part_numbers: list
        :param pies_segments: pies segments to include or ['all']
        :type pies_segments: list
        :param by_names: whether or not to filter by names rather than
            ID
        :type by_names: bool
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: vehicles products data
        :rtype: list

        :raises Exception: on general exception

        .. Topic:: **-Parameters-**

            Only one of `brand_ids` or `dataset_ids` allowed

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_ids_": <list>, (if defined)
                        "dataset_ids_": <list>, (if defined)
                        "base_vehicle_id_": <int>,
                        "vehicle_id_": <int>,
                        "year_": <int>,
                        "make_id_": <int>,
                        "make_name_": <str>,
                        "model_id_": <int>,
                        "model_name_": <str>,
                        "submodel_id_": <int>,
                        "submodel_name_": <str>,
                        "part_numbers_": <list>, (if defined)
                        "products_": [
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
                    }
                ]
            else:
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

        try:
            return self.get_queryset().retrieve_products_by_brand_data_from_api(
                brand_ids=brand_ids,
                dataset_ids=dataset_ids,
                part_numbers=part_numbers,
                pies_segments=pies_segments,
                by_names=by_names,
                annotated=annotated
            )
        except Exception:
            raise

    def retrieve_products_by_category_data_from_api(self, category_id,
                                                    brand_ids=None,
                                                    dataset_ids=None,
                                                    part_numbers=None,
                                                    pies_segments=None,
                                                    by_names=False,
                                                    annotated=False):
        """
        Retrieves vehicles products by category data from SEMA API.

        :param category_id: category ID on which to filter
        :type category_id: int
        :param brand_ids: brand IDs on which to filter
        :type brand_ids: list
        :param dataset_ids: dataset IDs on which to filter
        :type dataset_ids: list
        :param part_numbers: part numbers on which to filter
        :type part_numbers: list
        :param pies_segments: pies segments to include or ['all']
        :type pies_segments: list
        :param by_names: whether or not to filter by names rather than
            ID
        :type by_names: bool
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: vehicles products by category data
        :rtype: list

        :raises Exception: on general exception

        .. Topic:: **-Parameters-**

            Only one of `brand_ids` or `dataset_ids` allowed

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_ids_": <list>, (if defined)
                        "dataset_ids_": <list>, (if defined)
                        "base_vehicle_id_": <int>,
                        "vehicle_id_": <int>,
                        "year_": <int>,
                        "make_id_": <int>,
                        "make_name_": <str>,
                        "model_id_": <int>,
                        "model_name_": <str>,
                        "submodel_id_": <int>,
                        "submodel_name_": <str>,
                        "part_numbers_": <list>, (if defined)
                        "products_": [
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
                    }
                ]
            else:
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

        try:
            return self.get_queryset().retrieve_products_by_category_data_from_api(
                category_id=category_id,
                brand_ids=brand_ids,
                dataset_ids=dataset_ids,
                part_numbers=part_numbers,
                pies_segments=pies_segments,
                by_names=by_names,
                annotated=annotated
            )
        except Exception:
            raise
    # </editor-fold>

    # <editor-fold desc="import properties ...">
    def get_retrieve_data_from_api_params(self, **params):
        """
        Returns params with additional params base_vehicles as
        authorized base vehicles queryset if not already defined and
        annotated as true.

        :param params: param kwargs to which to add additional params

        :return: param kwargs
        :rtype: dict

        :raises Exception: on general exception

        """

        try:
            if 'base_vehicles' not in params:
                from sema.models import SemaBaseVehicle
                base_vehicles = SemaBaseVehicle.objects.filter(
                    is_authorized=True
                )
                params['base_vehicles'] = base_vehicles
            params['annotated'] = True
            return params
        except Exception:
            raise

    def flatten_api_data(self, data):
        """
        Flattens nested data and returns relevant key/values.

        :param data: API data
        :type data: list

        :return: flat API data
        :rtype: list

        :raises Exception: on general exception

        **-Expected Data Format-**
        ::
            data = [
                {
                    "base_vehicle_id_": <int>,
                    "submodels_": [
                        {
                            "VehicleID": <int>,
                            "SubmodelID": <int>
                        },
                        {...}
                    ]
                },
                {...}
            ]

        **-Return Format-**
        ::
            data = [
                {
                    "VehicleID": <int>,
                    "base_vehicle_id_": <int>,
                    "SubmodelID": <int>
                },
                {...}
            ]

        """

        try:
            flattened_data = []
            for base_vehicle in data:
                for submodel in base_vehicle['submodels_']:
                    flattened_data.append(
                        {
                            'VehicleID': submodel['VehicleID'],
                            'base_vehicle_id_': (
                                base_vehicle['base_vehicle_id_']
                            ),
                            'SubmodelID': submodel['SubmodelID']
                        }
                    )
            return flattened_data
        except Exception:
            raise

    def parse_api_data(self, data):
        """
        Returns object PK and field/value dictionary from API data item.

        :param data: API data item
        :type data: dict

        :return: object PK and field/value dictionary
        :rtype: tuple

        :raises Exception: on general exception

        **-Expected Data Format-**
        ::
            data = {
                "VehicleID": <int>,
                "base_vehicle_id_": <int>,
                "SubmodelID": <int>
            }

        **-Return Format-**
        ::
            pk = <int>
            fields = {
                "is_authorized": <bool>,
                "base_vehicle_id": <int>,
                "submodel_id": <int>
            }

        """

        try:
            pk = data['VehicleID']
            fields = {
                'is_authorized': True,
                'base_vehicle_id': data['base_vehicle_id_'],
                'submodel_id': data['SubmodelID']
            }
            return pk, fields
        except Exception:
            raise
    # </editor-fold

    # <editor-fold desc="unauthorize properties ...">
    def get_pk_list_from_api_data(self, data):
        """
        Returns a list of object PKs from full API data.

        :param data: API data
        :type data: list

        :return: list of PKs
        :rtype: list

        :raises Exception: on general exception

        **-Expected Data Format-**
        ::
            data = [
                {
                    "VehicleID": <int>
                },
                {..}
            ]

        **-Return Format-**
        ::
            ret = [
                <int>,
                ...
            ]

        """

        try:
            return [item['VehicleID'] for item in data]
        except Exception:
            raise
    # </editor-fold>


class SemaEngineManager(SemaBaseManager):
    """
    This manager class defines SEMA vehicle engine methods.

    """

    def get_queryset(self):
        return SemaEngineQuerySet(
            self.model,
            using=self._db
        )

    def with_admin_data(self):
        return self.get_queryset().with_admin_data()

    # <editor-fold desc="retrieve properties ...">
    def retrieve_data_from_api(self, brand_ids=None, dataset_ids=None,
                               year=None, make_id=None, model_id=None):
        """
        Retrieves engine data from SEMA API.

        :param brand_ids: brand IDs on which to filter
        :type brand_ids: list
        :param dataset_ids: dataset IDs on which to filter
        :type dataset_ids: list
        :param year: year on which to filter
        :type year: int
        :param make_id: make ID on which to filter
        :type make_id: int
        :param model_id: model ID on which to filter
        :type model_id: int

        :return: vehicle engine data
        :rtype: list

        :raises Exception: on general exception

        .. Topic:: **-Parameters-**

            Only one of `brand_ids` or `dataset_ids` allowed

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

        try:
            return sema_client.retrieve_engines(
                brand_ids=brand_ids,
                dataset_ids=dataset_ids,
                year=year,
                make_id=make_id,
                model_id=model_id
            )
        except Exception:
            raise
    # </editor-fold>

    # <editor-fold desc="import properties ...">
    def parse_api_data(self, data):
        """
        Returns NoneType (because PK is not defined in API data) and
        field/value dictionary from API data item.

        :param data: API data item
        :type data: dict

        :return: object PK and field/value dictionary
        :rtype: tuple

        :raises Exception: on general exception

        **-Expected Data Format-**
        ::
            data = {
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
            }

        **-Return Format-**
        ::
            pk = None
            fields = {
                "is_authorized": <bool>,
                "vehicle_id": <int>,
                "litre": <str>,
                "cc": <str>,
                "cid": <str>,
                "cylinders": <str>,
                "block_type": <str>,
                "engine_bore_in": <str>,
                "engine_bore_metric": <str>,
                "engine_stroke_in": <str>,
                "engine_stroke_metric": <str>,
                "valves_per_engine": "<str>,
                "aspiration": <str>,
                "cylinder_head_type": <str>,
                "fuel_type": <str>,
                "ignition_system_type": <str>,
                "manufacturer": <str>,
                "horse_power": <str>,
                "kilowatt_power": <str>,
                "engine_designation": <str>
            }

        """

        try:
            fields = {
                'is_authorized': True,
                'vehicle_id': data['VehicleID'],
                'litre': data['Liter'],
                'cc': data['CC'],
                'cid': data['CID'],
                'cylinders': data['Cylinders'],
                'block_type': data['BlockType'],
                'engine_bore_in': data['EngBoreIn'],
                'engine_bore_metric': data['EngBoreMetric'],
                'engine_stroke_in': data['EngStrokeIn'],
                'engine_stroke_metric': data['EngStrokeMetric'],
                'valves_per_engine': data['ValvesPerEngine'],
                'aspiration': data['AspirationName'],
                'cylinder_head_type': data['CylinderHeadTypeName'],
                'fuel_type': data['FuelTypeName'],
                'ignition_system_type': data['IgnitionSystemTypeName'],
                'manufacturer': data['MfrName'],
                'horse_power': data['HorsePower'],
                'kilowatt_power': data['KilowattPower'],
                'engine_designation': data['EngineDesignationName']
            }
            return None, fields
        except Exception:
            raise

    def get_object_from_api_data(self, vehicle_id=None, litre=None,
                                 cc=None, cid=None, cylinders=None,
                                 block_type=None, engine_bore_in=None,
                                 engine_bore_metric=None,
                                 engine_stroke_in=None,
                                 engine_stroke_metric=None,
                                 valves_per_engine=None, aspiration=None,
                                 cylinder_head_type=None, fuel_type=None,
                                 ignition_system_type=None, manufacturer=None,
                                 horse_power=None, kilowatt_power=None,
                                 engine_designation=None, **kwargs):
        """
        Returns object by all engine fields.

        :param vehicle_id: vehicle ID field value
        :type vehicle_id: int
        :param litre: litre field value
        :type litre: str
        :param cc: CC field value
        :type cc: str
        :param cid: CID field value
        :type cid: str
        :param cylinders: cylinders field value
        :type cylinders: str
        :param block_type: block type field value
        :type block_type: str
        :param engine_bore_in: engine bore inches field value
        :type engine_bore_in: str
        :param engine_bore_metric: engine bore metric field value
        :type engine_bore_metric: str
        :param engine_stroke_in: engine stroke inches field value
        :type engine_stroke_in: str
        :param engine_stroke_metric: engine stroke metric field value
        :type engine_stroke_metric: str
        :param valves_per_engine: valves per engine field value
        :type valves_per_engine: str
        :param aspiration: aspiration field value
        :type aspiration: str
        :param cylinder_head_type: cylinder head type field value
        :type cylinder_head_type: str
        :param fuel_type: fuel type field value
        :type fuel_type: str
        :param ignition_system_type: ignition system type field value
        :type ignition_system_type: str
        :param manufacturer: manufacturer field value
        :type manufacturer: str
        :param horse_power: horse power field value
        :type horse_power: str
        :param kilowatt_power: kilowatt power field value
        :type kilowatt_power: str
        :param engine_designation: engine designation field value
        :type engine_designation: str


        :return: model instance
        :rtype: object

        :raises Exception: missing year_id or make_id, or on general
            exception

        """
        if not (litre and cc and cid and cylinders and block_type
                and engine_bore_in and engine_bore_metric
                and engine_stroke_in and engine_stroke_metric
                and valves_per_engine and aspiration and cylinder_head_type
                and fuel_type and ignition_system_type and manufacturer
                and horse_power and kilowatt_power and engine_designation):
            raise Exception(
                'litre, CC, CID, cylinders, block type, engine bore inches,'
                'engine bore metric, engine stroke inches, engine stroke '
                'metric, valves per engine, aspiration, cylinder head type, '
                'fuel type, ignition system type, manufacturer, horse power, '
                'kilowatt power, and engine designation required'
            )

        try:
            return self.get(
                vehicle__vehicle_id=vehicle_id,
                litre=litre,
                cc=cc,
                cid=cid,
                cylinders=cylinders,
                block_type=block_type,
                engine_bore_in=engine_bore_in,
                engine_bore_metric=engine_bore_metric,
                engine_stroke_in=engine_stroke_in,
                engine_stroke_metric=engine_stroke_metric,
                valves_per_engine=valves_per_engine,
                aspiration=aspiration,
                cylinder_head_type=cylinder_head_type,
                fuel_type=fuel_type,
                ignition_system_type=ignition_system_type,
                manufacturer=manufacturer,
                horse_power=horse_power,
                kilowatt_power=kilowatt_power,
                engine_designation=engine_designation
            )
        except Exception:
            raise
    # </editor-fold

    # <editor-fold desc="unauthorize properties ...">
    def get_pk_list_from_api_data(self, data):
        """
        Returns a list of object PKs from full API data.

        :param data: API data
        :type data: list

        :return: list of PKs
        :rtype: list

        :raises Exception: on general exception

        **-Expected Data Format-**
        ::
            data = [
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

        **-Return Format-**
        ::
            ret = [
                <int>,
                ...
            ]

        """

        try:
            pk_list = []
            for item in data:
                try:
                    engine = self.get(
                        vehicle__vehicle_id=data['VehicleID'],
                        litre=data['Liter'],
                        cc=data['CC'],
                        cid=data['CID'],
                        cylinders=data['Cylinders'],
                        block_type=data['BlockType'],
                        engine_bore_in=data['EngBoreIn'],
                        engine_bore_metric=data['EngBoreMetric'],
                        engine_stroke_in=data['EngStrokeIn'],
                        engine_stroke_metric=data['EngStrokeMetric'],
                        valves_per_engine=data['ValvesPerEngine'],
                        aspiration=data['AspirationName'],
                        cylinder_head_type=data['CylinderHeadTypeName'],
                        fuel_type=data['FuelTypeName'],
                        ignition_system_type=data['IgnitionSystemTypeName'],
                        manufacturer=data['MfrName'],
                        horse_power=data['HorsePower'],
                        kilowatt_power=data['KilowattPower'],
                        engine_designation=data['EngineDesignationName']
                    )
                    pk_list.append(engine.pk)
                except self.model.DoesNotExist:
                    pass
            return pk_list
        except Exception:
            raise
    # </editor-fold>


class SemaCategoryManager(SemaBaseManager):
    """
    This manager class defines SEMA category methods.

    """

    def get_queryset(self):
        return SemaCategoryQuerySet(
            self.model,
            using=self._db
        )

    def with_admin_data(self):
        return self.get_queryset().with_admin_data()

    # <editor-fold desc="retrieve properties ...">
    def retrieve_data_from_api(self, datasets, base_vehicle_ids=None,
                               vehicle_ids=None, year=None,
                               make_name=None, model_name=None,
                               submodel_name=None, annotated=False):
        """
        Retrieves category data from SEMA API.

        :param datasets: dataset queryset with which to retrieve
        :type datasets: django.db.models.QuerySet
        :param base_vehicle_ids: base vehicle IDs on which to filter
        :type base_vehicle_ids: list
        :param vehicle_ids: vehicle IDs on which to filter
        :type vehicle_ids: list
        :param year: year on which to filter
        :type year: int
        :param make_name: make name on which to filter
        :type make_name: str
        :param model_name: model name on which to filter
        :type model_name: str
        :param submodel_name: submodel name on which to filter
        :type submodel_name: str
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: category data
        :rtype: list

        :raises Exception: on general exception

        .. Topic:: **-Parameters-**

            `year` requires `make_name` and `model_name`

            `make_name` requires `year` and `model_name`

            `model_name` requires `year` and `make_name`

            `submodel_name` requires `year`, `make_name`, and `model_name`

            Only one of `base_vehicle_ids`, `vehicle_ids`, or named
            year/make/model group allowed

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_id_": <str>,
                        "dataset_id_": <int>,
                        "base_vehicle_ids_": <list>, (if defined)
                        "vehicle_ids_": <list>, (if defined)
                        "year_": <int>, (if defined)
                        "make_name_": <str>, (if defined)
                        "model_name_": <str>, (if defined)
                        "submodel_name_": <str>, (if defined)
                        "categories_": [
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
                    }
                ]
            else:
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

        try:
            return datasets.retrieve_categories_data_from_api(
                base_vehicle_ids=base_vehicle_ids,
                vehicle_ids=vehicle_ids,
                year=year,
                make_name=make_name,
                model_name=model_name,
                submodel_name=submodel_name,
                annotated=annotated
            )
        except Exception:
            raise

    def retrieve_products_by_category_data_from_api(self, brand_ids=None,
                                                    dataset_ids=None,
                                                    base_vehicle_ids=None,
                                                    vehicle_ids=None,
                                                    year=None, make_name=None,
                                                    model_name=None,
                                                    submodel_name=None,
                                                    part_numbers=None,
                                                    pies_segments=None,
                                                    annotated=False):
        """
        Retrieves categories products data from SEMA API.

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
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: categories products data
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

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "category_id_": <int>,
                        "brand_ids_": <list>, (if defined)
                        "dataset_ids_": <list>, (if defined)
                        "base_vehicle_ids_": <list>, (if defined)
                        "vehicle_ids_": <list>, (if defined)
                        "year_": <int>, (if defined)
                        "make_name_": <str>, (if defined)
                        "model_name_": <str>, (if defined)
                        "submodel_name_": <str>, (if defined)
                        "part_numbers_": <list>, (if defined)
                        "products_": [
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
                    }
                ]
            else:
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

        try:
            return self.get_queryset().retrieve_products_by_category_data_from_api(
                brand_ids=brand_ids,
                dataset_ids=dataset_ids,
                base_vehicle_ids=base_vehicle_ids,
                vehicle_ids=vehicle_ids,
                year=year,
                make_name=make_name,
                model_name=model_name,
                submodel_name=submodel_name,
                part_numbers=part_numbers,
                pies_segments=pies_segments,
                annotated=annotated
            )
        except Exception:
            raise
    # </editor-fold>

    # <editor-fold desc="import properties ...">
    def get_retrieve_data_from_api_params(self, **params):
        """
        Returns params with additional params datasets as authorized
        datasets queryset if not already defined and annotated as false.

        :param params: param kwargs to which to add additional params

        :return: param kwargs
        :rtype: dict

        :raises Exception: on general exception

        """

        try:
            if 'datasets' not in params:
                from sema.models import SemaDataset
                datasets = SemaDataset.objects.filter(is_authorized=True)
                params['datasets'] = datasets
            params['annotated'] = False
            return params
        except Exception:
            raise

    def flatten_api_data(self, data):
        """
        Returns flattened data from nested data.

        :param data: API data
        :type data: list

        :return: flat API data
        :rtype: list

        :raises Exception: on general exception

        **-Expected Data Format-**
        ::
            data = [
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

        **-Return Format-**
        ::
            data = [
                {
                    "CategoryId": <int>,
                    "Name": <str>,
                    "ParentId": <int>
                },
                {...}
            ]

        """

        try:
            flattened_data = []
            for item in data:
                subcategories = item.pop('Categories', [])
                flattened_data.append(item)
                if subcategories:
                    flattened_data += self.flatten_api_data(subcategories)
            return flattened_data
        except Exception:
            raise

    def parse_api_data(self, data):
        """
        Returns object PK and field/value dictionary from API data item.

        :param data: API data item
        :type data: dict

        :return: object PK and field/value dictionary
        :rtype: tuple

        :raises Exception: on general exception

        **-Expected Data Format-**
        ::
            data = {
                "CategoryId": <int>,
                "Name": <str>,
                "ParentId": <int>
            }

        **-Return Format-**
        ::
            pk = <int>
            if data["ParentId"] == 0:
                fields = {
                    "is_authorized": <bool>,
                    "name": <int>
                }
            else:
                fields = {
                    "is_authorized": <bool>,
                    "name": <int>,
                    "parent_categories": <int>
                }

        """

        try:
            pk = data['CategoryId']
            fields = {
                'is_authorized': True,
                'name': data['Name']
            }
            if data['ParentId']:
                fields['parent_categories'] = data['ParentId']
            return pk, fields
        except Exception:
            raise
    # </editor-fold>

    # <editor-fold desc="unauthorize properties ...">
    def get_pk_list_from_api_data(self, data):
        """
        Returns a list of object PKs from full API data.

        :param data: API data
        :type data: list

        :return: list of PKs
        :rtype: list

        :raises Exception: on general exception

        **-Expected Data Format-**
        ::
            data = [
                {
                    "CategoryId": <int>
                },
                {..}
            ]

        **-Return Format-**
        ::
            ret = [
                <int>,
                ...
            ]

        """

        try:
            return [item['CategoryId'] for item in data]
        except Exception:
            raise
    # </editor-fold>

    # <editor-fold desc="perform properties ...">
    def perform_category_products_update_from_api(self, **filters):
        msgs = []
        try:
            msgs += self.get_queryset().perform_category_products_update_from_api(
                **filters
            )
        except Exception as err:
            msgs.append(self.model.get_class_error_msg(str(err)))

        if not msgs:
            msgs.append(self.model.get_class_up_to_date_msg())
        return msgs
    # </editor-fold>


class SemaProductManager(SemaBaseManager):
    """
    This manager class defines SEMA product methods.

    """

    def get_queryset(self):
        return SemaProductQuerySet(
            self.model,
            using=self._db
        )

    def with_admin_data(self):
        return self.get_queryset().with_admin_data()

    # <editor-fold desc="retrieve properties ...">
    def retrieve_data_from_api(self, datasets, base_vehicle_ids=None,
                               vehicle_ids=None, year=None,
                               make_name=None, model_name=None,
                               submodel_name=None, part_numbers=None,
                               pies_segments=None, annotated=False):
        """
        Retrieves product data from SEMA API.

        :param datasets: dataset queryset with which to retrieve
        :type datasets: django.db.models.QuerySet
        :param base_vehicle_ids: base vehicles IDs on which to filter
        :type base_vehicle_ids: list
        :param vehicle_ids: vehicle IDs on which to filter
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
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: product data
        :rtype: list

        :raises Exception: on general exception

        .. Topic:: **-Parameters-**

            `year` requires `make_name` and `model_name`

            `make_name` requires `year` and `model_name`

            `model_name` requires `year` and `make_name`

            `submodel_name` requires `year`, `make_name`, and `model_name`

            Only one of `base_vehicle_ids`, `vehicle_ids`, or named
            year/make/model group allowed

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_id_": <str>,
                        "dataset_id_": <int>,
                        "base_vehicle_ids_": <list>, (if defined)
                        "vehicle_ids_": <list>, (if defined)
                        "year_": <int>, (if defined)
                        "make_name_": <str>, (if defined)
                        "model_name_": <str>, (if defined)
                        "submodel_name_": <str>, (if defined)
                        "part_numbers_": <list>, (if defined)
                        "products_": [
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
                    }
                ]
            else:
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

        try:
            return datasets.retrieve_products_by_brand_data_from_api(
                base_vehicle_ids=base_vehicle_ids,
                vehicle_ids=vehicle_ids,
                year=year,
                make_name=make_name,
                model_name=model_name,
                submodel_name=submodel_name,
                part_numbers=part_numbers,
                pies_segments=pies_segments,
                annotated=annotated
            )
        except Exception:
            raise

    def retrieve_products_by_brand_data_from_api(self, base_vehicle_ids=None,
                                                 vehicle_ids=None, year=None,
                                                 make_name=None,
                                                 model_name=None,
                                                 submodel_name=None,
                                                 pies_segments=None,
                                                 annotated=False):
        """
        Retrieves products by brand data from SEMA API.

        :param base_vehicle_ids: base vehicle IDs on which to filter
        :type base_vehicle_ids: list
        :param vehicle_ids: vehicle IDs on which to filter
        :type vehicle_ids: list
        :param year: year on which to filter
        :type year: int
        :param make_name: make name on which to filter
        :type make_name: str
        :param model_name: model name on which to filter
        :type model_name: str
        :param submodel_name: submodel name on which to filter
        :type submodel_name: str
        :param pies_segments: pies segments to include or ['all']
        :type pies_segments: list
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: product data
        :rtype: list

        :raises Exception: on general exception

        .. Topic:: **-Parameters-**

            `year` requires `make_name` and `model_name`

            `make_name` requires `year` and `model_name`

            `model_name` requires `year` and `make_name`

            `submodel_name` requires `year`, `make_name`, and `model_name`

            Only one of `base_vehicle_ids`, `vehicle_ids`, or named
            year/make/model group allowed

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_id_": <str>,
                        "dataset_id_": <int>,
                        "base_vehicle_ids_": <list>, (if defined)
                        "vehicle_ids_": <list>, (if defined)
                        "year_": <int>, (if defined)
                        "make_name_": <str>, (if defined)
                        "model_name_": <str>, (if defined)
                        "submodel_name_": <str>, (if defined)
                        "part_numbers_": <list>,
                        "products_": [
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
                    }
                ]
            else:
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

        try:
            return self.get_queryset().retrieve_products_by_brand_data_from_api(
                base_vehicle_ids=base_vehicle_ids,
                vehicle_ids=vehicle_ids,
                year=year,
                make_name=make_name,
                model_name=model_name,
                submodel_name=submodel_name,
                pies_segments=pies_segments,
                annotated=annotated
            )
        except Exception:
            raise

    def retrieve_products_by_category_data_from_api(self, category_id,
                                                    base_vehicle_ids=None,
                                                    vehicle_ids=None,
                                                    year=None, make_name=None,
                                                    model_name=None,
                                                    submodel_name=None,
                                                    pies_segments=None,
                                                    annotated=False):
        """
        Retrieves products by category data from SEMA API.

        :param category_id: category ID on which to filter
        :type category_id: int
        :type base_vehicle_ids: int
        :param base_vehicle_ids: base vehicles IDs on which to filter
        :type base_vehicle_ids: list
        :param vehicle_ids: vehicle IDs on which to filter
        :type vehicle_ids: list
        :param year: year on which to filter
        :type year: int
        :param make_name: make name on which to filter
        :type make_name: str
        :param model_name: model name on which to filter
        :type model_name: str
        :param submodel_name: submodel name on which to filter
        :type submodel_name: str
        :param pies_segments: pies segments to include or ['all']
        :type pies_segments: list
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: products by category data
        :rtype: list

        :raises Exception: on general exception

        .. Topic:: **-Parameters-**

            `year` requires `make_name` and `model_name`

            `make_name` requires `year` and `model_name`

            `model_name` requires `year` and `make_name`

            `submodel_name` requires `year`, `make_name`, and `model_name`

            Only one of `base_vehicle_ids`, `vehicle_ids`, or named
            year/make/model group allowed

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "category_id_": <int>,
                        "brand_ids_": <list>, (if defined)
                        "dataset_ids_": <list>, (if defined)
                        "base_vehicle_ids_": <list>, (if defined)
                        "vehicle_ids_": <list>, (if defined)
                        "year_": <int>, (if defined)
                        "make_name_": <str>, (if defined)
                        "model_name_": <str>, (if defined)
                        "submodel_name_": <str>, (if defined)
                        "product_id_": <int>,
                        "part_number_": <str>,
                        "products_": [
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
                    },
                    {...}
                ]
            else:
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

        try:
            return self.get_queryset().retrieve_products_by_category_data_from_api(
                category_id=category_id,
                base_vehicle_ids=base_vehicle_ids,
                vehicle_ids=vehicle_ids,
                year=year,
                make_name=make_name,
                model_name=model_name,
                submodel_name=submodel_name,
                pies_segments=pies_segments,
                annotated=annotated
            )
        except Exception:
            raise

    def retrieve_product_html_data_from_api(self, annotated=False):
        """
        Retrieves products HTML data from SEMA API object.

        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: products HTML
        :rtype: list

        :raises: Exception on SEMA API object method exception

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "product_id_": <int>,
                        "html_": <str>
                    },
                    {...}
                ]
            else:
                ret = [
                    <str>,
                    ...
                ]
        """

        try:
            return self.get_queryset().retrieve_product_html_data_from_api(
                annotated=annotated
            )
        except Exception:
            raise
    # </editor-fold>

    # <editor-fold desc="import properties ...">
    def get_retrieve_data_from_api_params(self, **params):
        """
        Returns params with additional params datasets as authorized
        datasets queryset if not already defined and annotated as true.

        :param params: param kwargs to which to add additional params

        :return: param kwargs
        :rtype: dict

        :raises Exception: on general exception

        """

        try:
            if 'datasets' not in params:
                from sema.models import SemaDataset
                datasets = SemaDataset.objects.filter(is_authorized=True)
                params['datasets'] = datasets
            params['annotated'] = True
            return params
        except Exception:
            raise

    def flatten_api_data(self, data):
        """
        Flattens nested data and returns relevant key/values.

        :param data: API data
        :type data: list

        :return: flat API data
        :rtype: list

        :raises Exception: on general exception

        **-Expected Data Format-**
        ::
            data = [
                {
                    "dataset_id_": <int>,
                    "products_": [
                        {
                            "ProductId": <int>,
                            "PartNumber": <str>,
                        },
                        {...}
                    ]
                },
                {...}
            ]

        **-Return Format-**
        ::
            data = [
                {
                    "ProductId": <int>,
                    "PartNumber": <str>,
                    "dataset_id_": <int>
                },
                {...}
            ]

        """

        try:
            flattened_data = []
            for dataset in data:
                for product in dataset['products_']:
                    flattened_data.append(
                        {
                            'ProductId': product['ProductId'],
                            'PartNumber': product['PartNumber'],
                            'dataset_id_': dataset['dataset_id_']
                        }
                    )
            return flattened_data
        except Exception:
            raise

    def parse_api_data(self, data):
        """
        Returns object PK and field/value dictionary from API data item.

        :param data: API data item
        :type data: dict

        :return: object PK and field/value dictionary
        :rtype: tuple

        :raises Exception: on general exception

        **-Expected Data Format-**
        ::
            data = {
                "ProductId": <int>,
                "PartNumber": <str>,
                "dataset_id_": <int>
            }

        **-Return Format-**
        ::
            pk = <int>
            fields = {
                "is_authorized": <bool>,
                "part_number": <str>,
                "dataset_id": <int>
            }

        """

        try:
            pk = data['ProductId']
            fields = {
                'is_authorized': True,
                'part_number': data['PartNumber'],
                'dataset_id': data['dataset_id_']
            }
            return pk, fields
        except Exception:
            raise
    # </editor-fold>

    # <editor-fold desc="unauthorize properties ...">
    def get_pk_list_from_api_data(self, data):
        """
        Returns a list of object PKs from full API data.

        :param data: API data
        :type data: list

        :return: list of PKs
        :rtype: list

        :raises Exception: on general exception

        **-Expected Data Format-**
        ::
            data = [
                {
                    "ProductId": <int>
                },
                {..}
            ]

        **-Return Format-**
        ::
            ret = [
                <int>,
                ...
            ]

        """

        try:
            return [item['ProductId'] for item in data]
        except Exception:
            raise
    # </editor-fold>

    # <editor-fold desc="perform properties ...">
    def perform_product_vehicles_update_from_api(self):
        msgs = []
        try:
            msgs += self.get_queryset().perform_product_vehicles_update_from_api()
        except Exception as err:
            msgs.append(self.model.get_class_error_msg(str(err)))

        if not msgs:
            msgs.append(self.model.get_class_up_to_date_msg())
        return msgs

    def perform_pies_attribute_update_from_api(self, pies_attr_model,
                                               new_only=False, **filters):
        """
        Retrieves products PIES attribute data from SEMA API, and
        creates and/or updates products PIES attribute objects.

        :param pies_attr_model: SEMA PIES Attribute model class
        :type pies_attr_model: sema.models.SemaBasePiesAttributeModel
        :param new_only: whether or not to skip updating existing
            objects
        :type new_only: bool
        :param filters: kwargs by which to filter data retrieve

        :return: info, success, and/or error messages
        :rtype: list

        """

        msgs = []
        try:
            msgs += self.get_queryset(
            ).perform_pies_attribute_update_from_api(
                pies_attr_model=pies_attr_model,
                new_only=new_only,
                **filters
            )
        except Exception as err:
            msgs.append(self.model.get_class_error_msg(str(err)))
            return msgs

        if not msgs:
            msgs.append(self.model.get_class_up_to_date_msg())
        return msgs

    def perform_product_html_update_from_api(self):
        """
        Retrieves products HTML data from SEMA API, and updates HTML
        fields.

        :return: update or error messages
        :rtype: list

        """

        msgs = []
        try:
            msgs += self.get_queryset().perform_product_html_update_from_api()
        except Exception as err:
            msgs.append(self.model.get_class_error_msg(str(err)))

        if not msgs:
            msgs.append(self.model.get_class_up_to_date_msg())
        return msgs
    # </editor-fold>


class SemaBasePiesAttributeManager(SemaBaseManager):
    """
    This base manager class defines base attributes for SEMA PIES
    attribute managers.

    """

    DEFAULT_ATTRIBUTE_CODES = ['all']

    def get_queryset(self):
        return SemaBasePiesAttributeQuerySet(
            self.model,
            using=self._db
        )

    # <editor-fold desc="retrieve properties ...">
    def retrieve_data_from_api(self, products, base_vehicle_ids=None,
                               vehicle_ids=None, year=None,
                               make_name=None, model_name=None,
                               submodel_name=None, annotated=False):
        """
        Retrieves product and attribute data from SEMA API.

        :param products: products queryset with which to retrieve
        :type products: django.db.models.QuerySet
        :param base_vehicle_ids: base vehicles IDs on which to filter
        :type base_vehicle_ids: list
        :param vehicle_ids: vehicle IDs on which to filter
        :type vehicle_ids: list
        :param year: year on which to filter
        :type year: int
        :param make_name: make name on which to filter
        :type make_name: str
        :param model_name: model name on which to filter
        :type model_name: str
        :param submodel_name: submodel name on which to filter
        :type submodel_name: str
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: product and attribute data
        :rtype: list

        :raises Exception: on general exception

        .. Topic:: **-Parameters-**

            `year` requires `make_name` and `model_name`

            `make_name` requires `year` and `model_name`

            `model_name` requires `year` and `make_name`

            `submodel_name` requires `year`, `make_name`, and `model_name`

            Only one of `base_vehicle_ids`, `vehicle_ids`, or named
            year/make/model group allowed

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "brand_id_": <str>,
                        "dataset_id_": <int>,
                        "base_vehicle_ids_": <list>, (if defined)
                        "vehicle_ids_": <list>, (if defined)
                        "year_": <int>, (if defined)
                        "make_name_": <str>, (if defined)
                        "model_name_": <str>, (if defined)
                        "submodel_name_": <str>, (if defined)
                        "part_numbers_": <list>, (if defined)
                        "products_": [
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
                    }
                ]
            else:
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

        try:
            return products.retrieve_products_by_brand_data_from_api(
                base_vehicle_ids=base_vehicle_ids,
                vehicle_ids=vehicle_ids,
                year=year,
                make_name=make_name,
                model_name=model_name,
                submodel_name=submodel_name,
                pies_segments=self.DEFAULT_ATTRIBUTE_CODES,
                annotated=annotated
            )
        except Exception:
            raise

    # </editor-fold>

    # <editor-fold desc="import properties ...">
    def get_retrieve_data_from_api_params(self, **params):
        """
        Returns params with additional params products as authorized
        products queryset if not already defined and annotated as false.

        :param params: param kwargs to which to add additional params

        :return: param kwargs
        :rtype: dict

        :raises Exception: on general exception

        """

        try:
            if 'products' not in params:
                from sema.models import SemaProduct
                products = SemaProduct.objects.filter(is_authorized=True)
                params['products'] = products
            params['annotated'] = False
            return params
        except Exception:
            raise

    def flatten_api_data(self, data):
        """
        Flattens nested data and returns relevant key/values.

        :param data: API data
        :type data: list

        :return: flat API data
        :rtype: list

        :raises Exception: on general exception

        **-Expected Data Format-**
        ::
            data = [
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

        **-Return Format-**
        ::
            data = [
                {
                    "ProductId": <int>,
                    "PiesSegment": <str>,
                    "Value": <str> or null
                },
                {...}
            ]

        """

        try:
            flattened_data = []
            for product in data:
                for pies_attribute in product['PiesAttributes']:
                    if pies_attribute['Value']:
                        flattened_data.append(
                            {
                                'ProductId': product['ProductId'],
                                'PiesSegment': pies_attribute['PiesSegment'],
                                'Value': pies_attribute['Value']
                            }
                        )
            return flattened_data
        except Exception:
            raise

    def parse_api_data(self, data):
        """
        Returns NoneType (because PK is not defined in API data) and
        object field/value dictionary from API data item.

        :param data: API data item
        :type data: dict

        :return: object PK and field/value dictionary
        :rtype: tuple

        :raises Exception: on general exception

        **-Expected Data Format-**
        ::
            data = {
                "ProductId": <int>,
                "PiesSegment": <str>,
                "Value": <str> or null
            }

        **-Return Format-**
        ::
            pk = None
            fields = {
                "product_id": <int>,
                "segment": <str>,
                "value": <str>
            }

        """

        try:
            fields = {
                'is_authorized': True,
                'product_id': data['ProductId'],
                'segment': data['PiesSegment'],
                'value': data['Value']
            }
            return None, fields
        except Exception:
            raise

    def get_object_from_api_data(self, pk=None, product_id=None,
                                 segment=None, value=None):
        """
        Returns object by product and segment.

        :param pk: placeholder for overridden PK param
        :param product_id: product ID field value
        :type product_id: int
        :param segment: segment field value
        :type segment: str
        :param value: placeholder for overridden value param
        :type value: str

        :return: model instance
        :rtype: object

        :raises Exception: missing product_id or segment, or on general
            exception

        """

        if not (product_id and segment):
            raise Exception('Product ID and segment required')

        try:
            return self.get(
                product_id=product_id,
                segment=segment
            )
        except Exception:
            raise
    # </editor-fold>

    # <editor-fold desc="unauthorize properties ...">
    def get_pk_list_from_api_data(self, data):
        """
        Returns a list of object PKs from full API data.

        :param data: API data
        :type data: list

        :return: list of PKs
        :rtype: list

        :raises Exception: on general exception

        **-Expected Data Format-**
        ::
            data = [
                {
                    "ProductId": <int>,
                    "PiesSegment": <str>,
                    "Value": <str>
                },
                {..}
            ]

        **-Return Format-**
        ::
            ret = [
                <int>,
                ...
            ]

        """

        try:
            pk_list = []
            for item in data:
                try:
                    pies_attribute = self.get(
                        product_id=item['ProductId'],
                        segment=item['PiesSegment'],
                        value=item['Value']
                    )
                    pk_list.append(pies_attribute.pk)
                except self.model.DoesNotExist:
                    pass
            return pk_list
        except Exception:
            raise
    # </editor-fold>


class SemaDescriptionPiesAttributeManager(SemaBasePiesAttributeManager):
    """
    This manager class defines SEMA description PIES attribute methods.

    """

    DEFAULT_ATTRIBUTE_CODES = ['C10']

    def get_queryset(self):
        return SemaDescriptionPiesAttributeQuerySet(
            self.model,
            using=self._db
        )


class SemaDigitalAssetsPiesAttributeManager(SemaBasePiesAttributeManager):
    """
    This manager class defines SEMA digital assets PIES attribute
    methods.

    """

    DEFAULT_ATTRIBUTE_CODES = ['P05', 'P80']

    def get_queryset(self):
        return SemaDigitalAssetsPiesAttributeQuerySet(
            self.model,
            using=self._db
        )

# <editor-fold desc="perform properties ...">
    def perform_relevancy_update(self):
        msgs = []
        try:
            msgs += self.get_queryset().perform_relevancy_update()
        except Exception as err:
            msgs.append(self.model.get_class_error_msg(str(err)))

        if not msgs:
            msgs.append(self.model.get_class_up_to_date_msg())
        return msgs
    # </editor-fold>
