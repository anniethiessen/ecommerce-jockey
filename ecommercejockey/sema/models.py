"""
This module defines all models for the SEMA app.

"""


from bs4 import BeautifulSoup
from slugify import slugify

from django.db.models import (
    Model,
    BooleanField,
    CharField,
    ForeignKey,
    ManyToManyField,
    PositiveIntegerField,
    PositiveSmallIntegerField,
    TextField,
    URLField,
    CASCADE
)

from core.models import (
    MessagesMixin,
    NotesBaseModel,
    RelevancyBaseModel
)
from .clients import sema_client
from .managers import (
    SemaBaseManager,
    SemaBasePiesAttributeManager,
    SemaBaseVehicleManager,
    SemaBrandManager,
    SemaCategoryManager,
    SemaDatasetManager,
    SemaDescriptionPiesAttributeManager,
    SemaDigitalAssetsPiesAttributeManager,
    SemaEngineManager,
    SemaMakeManager,
    SemaMakeYearManager,
    SemaModelManager,
    SemaProductManager,
    SemaSubmodelManager,
    SemaYearManager,
    SemaVehicleManager
)


class SemaBaseModel(RelevancyBaseModel):
    """
    This abstract model class defines base attributes for SEMA models.

    """

    is_authorized = BooleanField(
        default=False,
        help_text='brand has given access to dataset'
    )

    # <editor-fold desc="relevancy properties ...">
    @property
    def relevancy_warnings(self):
        """
        Returns a concatenation of warnings based on relevancy.

        :return: warnings based on relevancy
        :rtype: str

        """

        msgs = []
        if self.is_relevant:
            if not self.is_authorized:
                warning = "not authorized"
                msgs.append(warning)
        return ', '.join(msgs)
    relevancy_warnings.fget.short_description = 'Warnings'
    # </editor-fold>

    # <editor-fold desc="update properties ...">
    @property
    def state(self):
        """
        Returns a dictionary of fields and values relevant to updates.

        :return: current values of fields relevant to updates
        :rtype: dict

        """

        return {
            'Authorized': self.is_authorized
        }

    def update_from_api_data(self, **update_fields):
        """
        Marks object as authorized and updates any necessary fields.

        :param update_fields: field/value kwargs to be updated.
        :type update_fields: dict

        :return: info, success or error message
        :rtype: str

        """

        try:
            prev = self.state
            for attr, value in update_fields.items():
                if isinstance(
                        self._meta.model._meta.get_field(attr),
                        ManyToManyField):
                    getattr(self, attr).add(value)
                    self.save()
                elif not getattr(self, attr) == value:
                    setattr(self, attr, value)
                    self.save()
            self.refresh_from_db()
            new = self.state
            msg = self.get_update_success_msg(previous_data=prev, new_data=new)
        except Exception as err:
            msg = self.get_instance_error_msg(f"{update_fields}, {err}")
        return msg
    # </editor-fold>

    # <editor-fold desc="unauthorize properties ...">
    def unauthorize(self):
        """
        Marks object as unauthorized.

        :return: info, success, or error message
        :rtype: str

        """

        try:
            if self.is_authorized:
                previous = self.state
                self.is_authorized = False
                self.save()
                self.refresh_from_db()
                new = self.state
                msg = self.get_update_success_msg(
                    previous_data=previous,
                    new_data=new
                )
            else:
                msg = self.get_instance_up_to_date_msg()
        except Exception as err:
            msg = self.get_instance_error_msg(str(err))
        return msg
    # </editor-fold>

    objects = SemaBaseManager()

    class Meta:
        abstract = True


class SemaYear(SemaBaseModel):
    """
    This model class defines SEMA vehicle years.

    """

    year = PositiveSmallIntegerField(
        primary_key=True,
        unique=True
    )

    # <editor-fold desc="relevancy properties ...">
    @property
    def may_be_relevant(self):
        """
        Returns whether or not object may be relevant based on
        attributes and related attributes.

        .. Topic:: **-May Be Relevant Conditions-**

            1. has relevant vehicles

        :return: whether or not object may be relevant
        :rtype: bool

        """

        return bool(self.vehicle_relevant_count)

    @property
    def relevancy_errors(self):
        """
        Returns a concatenation of errors based on relevancy.

        :return: errors based on relevancy
        :rtype: str

        """

        msgs = []
        if self.is_relevant:
            if not self.vehicle_relevant_count:
                error = "no relevant vehicles"
                msgs.append(error)
        return ', '.join(msgs)
    relevancy_errors.fget.short_description = 'Errors'
    # </editor-fold>

    # <editor-fold desc="count properties ...">
    @property
    def make_year_count(self):
        """
        Returns make year count.

        :return: make year count
        :rtype: int

        """

        return self.make_years.distinct().count()

    @property
    def make_year_relevant_count(self):
        """
        Returns relevant make year count.

        :return: relevant make year count
        :rtype: int

        """

        return self.make_years.filter(is_relevant=True).distinct().count()
    make_year_relevant_count.fget.short_description = (
        'Relevant Make Year Count'
    )

    @property
    def vehicle_relevant_count(self):
        """
        Returns relevant vehicle count.

        :return: relevant vehicle count
        :rtype: int

        """

        relevant_vehicle_count = 0
        for make_year in self.make_years.all():
            for base_vehicle in make_year.base_vehicles.all():
                relevant_vehicle_count += base_vehicle.vehicle_relevant_count
        return relevant_vehicle_count
    vehicle_relevant_count.fget.short_description = 'Relevant Vehicle Count'
    # </editor-fold>

    # <editor-fold desc="retrieve properties ...">
    def retrieve_makes_data_from_api(self, brand_ids=None,
                                     dataset_ids=None, annotated=False):
        """
        Retrieves year makes data from SEMA API.

        :param brand_ids: brand IDs on which to filter
        :type brand_ids: list
        :param dataset_ids: dataset IDs on which to filter
        :type dataset_ids: list
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: year makes data
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
            data = sema_client.retrieve_makes(
                brand_ids=brand_ids,
                dataset_ids=dataset_ids,
                year=self.year
            )
            if annotated:
                data = {
                    'year_': self.year,
                    'makes_': data
                }
                if brand_ids:
                    data['brand_ids_'] = brand_ids
                if dataset_ids:
                    data['dataset_ids_'] = dataset_ids
                data = [data]
            return data
        except Exception:
            raise

    def retrieve_models_data_from_api(self, brand_ids=None, dataset_ids=None,
                                      make_id=None, annotated=False):
        """
        Retrieves year models data from SEMA API.

        :param brand_ids: brand IDs on which to filter
        :type brand_ids: list
        :param dataset_ids: dataset IDs on which to filter
        :type dataset_ids: list
        :param make_id: make ID on which to filter
        :type make_id: int
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: year models data
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
            data = sema_client.retrieve_models(
                brand_ids=brand_ids,
                year=self.year,
                dataset_ids=dataset_ids,
                make_id=make_id
            )
            if annotated:
                data = {
                    'year_': self.year,
                    'models_': data
                }
                if brand_ids:
                    data['brand_ids_'] = brand_ids
                if dataset_ids:
                    data['dataset_ids_'] = dataset_ids
                if make_id:
                    data['make_id_'] = make_id
                data = [data]
            return data
        except Exception:
            raise

    def retrieve_submodels_data_from_api(self, brand_ids=None,
                                         dataset_ids=None,
                                         make_id=None, model_id=None,
                                         annotated=False):
        """
        Retrieves year submodels data from SEMA API.

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

        :return: year submodels data
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
            data = sema_client.retrieve_submodels(
                brand_ids=brand_ids,
                dataset_ids=dataset_ids,
                year=self.year,
                make_id=make_id,
                model_id=model_id
            )
            if annotated:
                data = {
                    'year_': self.year,
                    'submodels_': data
                }
                if brand_ids:
                    data['brand_ids_'] = brand_ids
                if dataset_ids:
                    data['dataset_ids_'] = dataset_ids
                if make_id:
                    data['make_id_'] = make_id
                if model_id:
                    data['model_id_'] = model_id
                data = [data]
            return data
        except Exception:
            raise

    def retrieve_engines_data_from_api(self, brand_ids=None, dataset_ids=None,
                                       make_id=None, model_id=None,
                                       annotated=False):
        """
        Retrieves year engines data from SEMA API.

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

        :return: year engines data
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
            data = sema_client.retrieve_engines(
                brand_ids=brand_ids,
                dataset_ids=dataset_ids,
                year=self.year,
                make_id=make_id,
                model_id=model_id
            )
            if annotated:
                data = {
                    'year_': self.year,
                    'engines_': data
                }
                if brand_ids:
                    data['brand_ids_'] = brand_ids
                if dataset_ids:
                    data['dataset_ids_'] = dataset_ids
                if make_id:
                    data['make_id_'] = make_id
                if model_id:
                    data['model_id_'] = model_id
                data = [data]
            return data
        except Exception:
            raise
    # </editor-fold>

    objects = SemaYearManager()

    class Meta:
        ordering = ['year']
        verbose_name = 'SEMA year'

    def __str__(self):
        return str(self.year)


class SemaMake(SemaBaseModel):
    """
    This model class defines SEMA vehicle makes.

    """

    make_id = PositiveIntegerField(
        primary_key=True,
        unique=True
    )
    name = CharField(
        max_length=50,
    )

    # <editor-fold desc="count properties ...">
    @property
    def make_year_count(self):
        """
        Returns make year count.

        :return: make year count
        :rtype: int

        """

        return self.make_years.distinct().count()

    @property
    def make_year_relevant_count(self):
        """
        Returns relevant make year count.

        :return: relevant make year count
        :rtype: int

        """

        return self.make_years.filter(is_relevant=True).distinct().count()
    make_year_relevant_count.fget.short_description = (
        'Relevant Make Year Count'
    )
    # </editor-fold>

    # <editor-fold desc="retrieve properties ...">
    def retrieve_models_data_from_api(self, brand_ids=None, dataset_ids=None,
                                      year=None, annotated=False):
        """
        Retrieves make models data from SEMA API.

        :param brand_ids: brand IDs on which to filter
        :type brand_ids: list
        :param dataset_ids: dataset IDs on which to filter
        :type dataset_ids: list
        :param year: year on which to filter
        :type year: int
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: make models data
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
            data = sema_client.retrieve_models(
                brand_ids=brand_ids,
                dataset_ids=dataset_ids,
                year=year,
                make_id=self.make_id
            )
            if annotated:
                data = {
                    'make_id_': self.make_id,
                    'models_': data
                }
                if brand_ids:
                    data['brand_ids_'] = brand_ids
                if dataset_ids:
                    data['dataset_ids_'] = dataset_ids
                if year:
                    data['year_'] = year
                data = [data]
            return data
        except Exception:
            raise

    def retrieve_submodels_data_from_api(self, brand_ids=None,
                                         dataset_ids=None,
                                         year=None, model_id=None,
                                         annotated=False):
        """
        Retrieves make submodels data from SEMA API.

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

        :return: make submodels data
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
            data = sema_client.retrieve_submodels(
                brand_ids=brand_ids,
                dataset_ids=dataset_ids,
                year=year,
                make_id=self.make_id,
                model_id=model_id
            )
            if annotated:
                data = {
                    'make_id_': self.make_id,
                    'submodels_': data
                }
                if brand_ids:
                    data['brand_ids_'] = brand_ids
                if dataset_ids:
                    data['dataset_ids_'] = dataset_ids
                if year:
                    data['year_'] = year
                if model_id:
                    data['model_id_'] = model_id
                data = [data]
            return data
        except Exception:
            raise

    def retrieve_engines_data_from_api(self, brand_ids=None, dataset_ids=None,
                                       year=None, model_id=None,
                                       annotated=False):
        """
        Retrieves make engines data from SEMA API.

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

        :return: make engines data
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
            data = sema_client.retrieve_engines(
                brand_ids=brand_ids,
                dataset_ids=dataset_ids,
                year=year,
                make_id=self.make_id,
                model_id=model_id
            )
            if annotated:
                data = {
                    'make_id_': self.make_id,
                    'engines_': data
                }
                if brand_ids:
                    data['brand_ids_'] = brand_ids
                if dataset_ids:
                    data['dataset_ids_'] = dataset_ids
                if year:
                    data['year_'] = year
                if model_id:
                    data['model_id_'] = model_id
                data = [data]
            return data
        except Exception:
            raise
    # </editor-fold>

    # <editor-fold desc="update properties ...">
    @property
    def state(self):
        """
        Returns a dictionary of fields and values relevant to updates.

        :return: current values of fields relevant to updates
        :rtype: dict

        """

        state = dict(super().state)
        state.update(
            {
                'Name': self.name
            }
        )
        return state
    # </editor-fold>

    objects = SemaMakeManager()

    class Meta:
        ordering = ['name']
        verbose_name = 'SEMA make'

    def __str__(self):
        return str(self.name)


class SemaModel(SemaBaseModel):
    """
    This model class defines SEMA vehicle models.

    """

    model_id = PositiveIntegerField(
        primary_key=True,
        unique=True
    )
    name = CharField(
        max_length=50,
    )

    # <editor-fold desc="relevancy properties ...">
    @property
    def may_be_relevant(self):
        """
        Returns whether or not object may be relevant based on
        attributes and related attributes.

        .. Topic:: **-May Be Relevant Conditions-**

            1. has relevant vehicles

        :return: whether or not object may be relevant
        :rtype: bool

        """

        return bool(self.vehicle_relevant_count)

    @property
    def relevancy_errors(self):
        """
        Returns a concatenation of errors based on relevancy.

        :return: errors based on relevancy
        :rtype: str

        """

        msgs = []
        if self.is_relevant:
            if not self.vehicle_relevant_count:
                error = "no relevant vehicles"
                msgs.append(error)
        return ', '.join(msgs)
    relevancy_errors.fget.short_description = 'Errors'
    # </editor-fold>

    # <editor-fold desc="count properties ...">
    @property
    def base_vehicle_count(self):
        """
        Returns base vehicle count.

        :return: base vehicle count
        :rtype: int

        """

        return self.base_vehicles.distinct().count()

    @property
    def base_vehicle_relevant_count(self):
        """
        Returns relevant base vehicle count.

        :return: relevant base vehicle count
        :rtype: int

        """

        return self.base_vehicles.filter(is_relevant=True).distinct().count()
    base_vehicle_relevant_count.fget.short_description = (
        'Relevant Base Vehicle Count'
    )

    @property
    def vehicle_relevant_count(self):
        """
        Returns relevant vehicle count.

        :return: relevant vehicle count
        :rtype: int

        """

        relevant_vehicle_count = 0
        for base_vehicle in self.base_vehicles.all():
            relevant_vehicle_count += base_vehicle.vehicle_relevant_count
        return relevant_vehicle_count
    vehicle_relevant_count.fget.short_description = 'Relevant Vehicle Count'
    # </editor-fold>

    # <editor-fold desc="retrieve properties ...">
    def retrieve_submodels_data_from_api(self, brand_ids=None,
                                         dataset_ids=None, year=None,
                                         make_id=None, annotated=False):
        """
        Retrieves model submodels data from SEMA API.

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

        :return: model submodels data
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
            data = sema_client.retrieve_submodels(
                brand_ids=brand_ids,
                dataset_ids=dataset_ids,
                year=year,
                make_id=make_id,
                model_id=self.model_id
            )
            if annotated:
                data = {
                    'model_id_': self.model_id,
                    'submodels_': data
                }
                if brand_ids:
                    data['brand_ids_'] = brand_ids
                if dataset_ids:
                    data['dataset_ids_'] = dataset_ids
                if year:
                    data['year_'] = year
                if make_id:
                    data['make_id_'] = make_id
                data = [data]
            return data
        except Exception:
            raise

    def retrieve_engines_data_from_api(self, brand_ids=None, dataset_ids=None,
                                       year=None, make_id=None,
                                       annotated=False):
        """
        Retrieves model engines data from SEMA API.

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

        :return: model engines data
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
            data = sema_client.retrieve_engines(
                brand_ids=brand_ids,
                dataset_ids=dataset_ids,
                year=year,
                make_id=make_id,
                model_id=self.model_id
            )
            if annotated:
                data = {
                    'model_id_': self.model_id,
                    'engines_': data
                }
                if brand_ids:
                    data['brand_ids_'] = brand_ids
                if dataset_ids:
                    data['dataset_ids_'] = dataset_ids
                if year:
                    data['year_'] = year
                if make_id:
                    data['make_id_'] = make_id
                data = [data]
            return data
        except Exception:
            raise
    # </editor-fold>

    # <editor-fold desc="update properties ...">
    @property
    def state(self):
        """
        Returns a dictionary of fields and values relevant to updates.

        :return: current values of fields relevant to updates
        :rtype: dict

        """

        state = dict(super().state)
        state.update(
            {
                'Name': self.name
            }
        )
        return state
    # </editor-fold>

    objects = SemaModelManager()

    class Meta:
        ordering = ['name']
        verbose_name = 'SEMA model'

    def __str__(self):
        return str(self.name)


class SemaSubmodel(SemaBaseModel):
    """
    This model class defines SEMA vehicle submodels.

    """

    submodel_id = PositiveIntegerField(
        primary_key=True,
        unique=True
    )
    name = CharField(
        max_length=50,
    )

    # <editor-fold desc="relevancy properties ...">
    @property
    def may_be_relevant(self):
        """
        Returns whether or not object may be relevant based on
        attributes and related attributes.

        .. Topic:: **-May Be Relevant Conditions-**

            1. has relevant vehicles

        :return: whether or not object may be relevant
        :rtype: bool

        """

        return bool(self.vehicle_relevant_count)

    @property
    def relevancy_errors(self):
        """
        Returns a concatenation of errors based on relevancy.

        :return: errors based on relevancy
        :rtype: str

        """

        msgs = []
        if self.is_relevant:
            if not self.vehicle_relevant_count:
                error = "no relevant vehicles"
                msgs.append(error)
        return ', '.join(msgs)
    relevancy_errors.fget.short_description = 'Errors'
    # </editor-fold>

    # <editor-fold desc="count properties ...">
    @property
    def vehicle_count(self):
        """
        Returns vehicle count.

        :return: vehicle count
        :rtype: int

        """

        return self.vehicles.distinct().count()

    @property
    def vehicle_relevant_count(self):
        """
        Returns relevant vehicle count.

        :return: relevant vehicle count
        :rtype: int

        """

        return self.vehicles.filter(is_relevant=True).distinct().count()
    vehicle_relevant_count.fget.short_description = 'Relevant Vehicle Count'
    # </editor-fold>

    # <editor-fold desc="update properties ...">
    @property
    def state(self):
        """
        Returns a dictionary of fields and values relevant to updates.

        :return: current values of fields relevant to updates
        :rtype: dict

        """

        state = dict(super().state)
        state.update(
            {
                'Name': self.name
            }
        )
        return state
    # </editor-fold>

    objects = SemaSubmodelManager()

    class Meta:
        ordering = ['name']
        verbose_name = 'SEMA submodel'

    def __str__(self):
        return str(self.name)


class SemaMakeYear(SemaBaseModel):
    """
    This model class defines SEMA vehicle make and year relationships.

    """

    year = ForeignKey(
        SemaYear,
        on_delete=CASCADE,
        related_name='make_years'
    )
    make = ForeignKey(
        SemaMake,
        on_delete=CASCADE,
        related_name='make_years'
    )

    # <editor-fold desc="relevancy properties ...">
    @property
    def may_be_relevant(self):
        """
        Returns whether or not object may be relevant based on
        attributes and related attributes.

        .. Topic:: **-May Be Relevant Conditions-**

            1. has relevant vehicles

        :return: whether or not object may be relevant
        :rtype: bool

        """

        return bool(self.vehicle_relevant_count)

    @property
    def relevancy_errors(self):
        """
        Returns a concatenation of errors based on relevancy.

        :return: errors based on relevancy
        :rtype: str

        """

        msgs = []
        if self.is_relevant:
            if not self.vehicle_relevant_count:
                error = "no relevant vehicles"
                msgs.append(error)
        return ', '.join(msgs)
    relevancy_errors.fget.short_description = 'Errors'
    # </editor-fold>

    # <editor-fold desc="count properties ...">
    @property
    def base_vehicle_count(self):
        """
        Returns base vehicle count.

        :return: base vehicle count
        :rtype: int

        """

        return self.base_vehicles.distinct().count()

    @property
    def base_vehicle_relevant_count(self):
        """
        Returns relevant base vehicle count.

        :return: relevant base vehicle count
        :rtype: int

        """

        return self.base_vehicles.filter(is_relevant=True).distinct().count()
    base_vehicle_relevant_count.fget.short_description = (
        'Relevant Base Vehicle Count'
    )

    @property
    def vehicle_relevant_count(self):
        """
        Returns relevant vehicle count.

        :return: relevant vehicle count
        :rtype: int

        """

        relevant_vehicle_count = 0
        for base_vehicle in self.base_vehicles.all():
            relevant_vehicle_count += base_vehicle.vehicle_relevant_count
        return relevant_vehicle_count
    vehicle_relevant_count.fget.short_description = 'Relevant Vehicle Count'
    # </editor-fold>

    # <editor-fold desc="retrieve properties ...">
    def retrieve_models_data_from_api(self, brand_ids=None,
                                      dataset_ids=None, annotated=False):
        """
        Retrieves make year models data from SEMA API.

        :param brand_ids: brand IDs on which to filter
        :type brand_ids: list
        :param dataset_ids: dataset IDs on which to filter
        :type dataset_ids: list
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: make year models data
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
            data = sema_client.retrieve_models(
                brand_ids=brand_ids,
                dataset_ids=dataset_ids,
                year=self.year.year,
                make_id=self.make.make_id
            )
            if annotated:
                data = {
                    'make_year_id_': self.pk,
                    'year_': self.year.year,
                    'make_id_': self.make.make_id,
                    'models_': data
                }
                if brand_ids:
                    data['brand_ids_'] = brand_ids
                if dataset_ids:
                    data['dataset_ids_'] = dataset_ids
                data = [data]
            return data
        except Exception:
            raise

    def retrieve_submodels_data_from_api(self, brand_ids=None,
                                         dataset_ids=None, model_id=None,
                                         annotated=False):
        """
        Retrieves make year submodels data from SEMA API.

        :param brand_ids: brand IDs on which to filter
        :type brand_ids: list
        :param dataset_ids: dataset IDs on which to filter
        :type dataset_ids: list
        :param model_id: model ID on which to filter
        :type model_id: int
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: make year submodels data
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
            data = sema_client.retrieve_submodels(
                brand_ids=brand_ids,
                dataset_ids=dataset_ids,
                year=self.year.year,
                make_id=self.make.make_id,
                model_id=model_id
            )
            if annotated:
                data = {
                    'make_year_id_': self.pk,
                    'year_': self.year.year,
                    'make_id_': self.make.make_id,
                    'submodels_': data
                }
                if brand_ids:
                    data['brand_ids_'] = brand_ids
                if dataset_ids:
                    data['dataset_ids_'] = dataset_ids
                if model_id:
                    data['model_id_'] = model_id
                data = [data]
            return data
        except Exception:
            raise

    def retrieve_engines_data_from_api(self, brand_ids=None, dataset_ids=None,
                                       model_id=None, annotated=False):
        """
        Retrieves make year engines data from SEMA API.

        :param brand_ids: brand IDs on which to filter
        :type brand_ids: list
        :param dataset_ids: dataset IDs on which to filter
        :type dataset_ids: list
        :param model_id: model ID on which to filter
        :type model_id: int
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: make year engines data
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
            data = sema_client.retrieve_engines(
                brand_ids=brand_ids,
                dataset_ids=dataset_ids,
                year=self.year.year,
                make_id=self.make.make_id,
                model_id=model_id
            )
            if annotated:
                data = {
                    'make_year_id_': self.pk,
                    'year_': self.year.year,
                    'make_id_': self.make.make_id,
                    'engines_': data
                }
                if brand_ids:
                    data['brand_ids_'] = brand_ids
                if dataset_ids:
                    data['dataset_ids_'] = dataset_ids
                if model_id:
                    data['model_id_'] = model_id
                data = [data]
            return data
        except Exception:
            raise
    # </editor-fold>

    # <editor-fold desc="update properties ...">
    @property
    def state(self):
        """
        Returns a dictionary of fields and values relevant to updates.

        :return: current values of fields relevant to updates
        :rtype: dict

        """

        state = dict(super().state)
        state.update(
            {
                'Year': str(self.year),
                'Make': str(self.make)
            }
        )
        return state
    # </editor-fold>

    objects = SemaMakeYearManager()

    class Meta:
        ordering = ['make', 'year']
        unique_together = ['make', 'year']
        verbose_name = 'SEMA make year'

    def __str__(self):
        return f'{self.year} :: {self.make}'


class SemaBaseVehicle(SemaBaseModel):
    """
    This model class defines SEMA base vehicles.

    """

    base_vehicle_id = PositiveIntegerField(
        primary_key=True,
        unique=True
    )
    make_year = ForeignKey(
        SemaMakeYear,
        on_delete=CASCADE,
        related_name='base_vehicles'
    )
    model = ForeignKey(
        SemaModel,
        on_delete=CASCADE,
        related_name='base_vehicles'
    )

    # <editor-fold desc="relevancy properties ...">
    @property
    def may_be_relevant(self):
        """
        Returns whether or not object may be relevant based on
        attributes and related attributes.

        .. Topic:: **-May Be Relevant Conditions-**

            1. has relevant vehicles

        :return: whether or not object may be relevant
        :rtype: bool

        """

        return bool(self.vehicle_relevant_count)

    @property
    def relevancy_errors(self):
        """
        Returns a concatenation of errors based on relevancy.

        :return: errors based on relevancy
        :rtype: str

        """

        msgs = []
        if self.is_relevant:
            if not self.vehicle_relevant_count:
                error = "no relevant vehicles"
                msgs.append(error)
        return ', '.join(msgs)
    relevancy_errors.fget.short_description = 'Errors'
    # </editor-fold>

    # <editor-fold desc="count properties ...">
    @property
    def vehicle_count(self):
        """
        Returns vehicle count.

        :return: vehicle count
        :rtype: int

        """

        return self.vehicles.distinct().count()

    @property
    def vehicle_relevant_count(self):
        """
        Returns relevant vehicle count.

        :return: relevant vehicle count
        :rtype: int

        """

        return self.vehicles.filter(is_relevant=True).distinct().count()
    vehicle_relevant_count.fget.short_description = 'Relevant Vehicle Count'
    # </editor-fold>

    # <editor-fold desc="retrieve properties ...">
    def retrieve_submodels_data_from_api(self, brand_ids=None,
                                         dataset_ids=None, annotated=False):
        """
        Retrieves base vehicle submodels data from SEMA API.

        :param brand_ids: brand IDs on which to filter
        :type brand_ids: list
        :param dataset_ids: dataset IDs on which to filter
        :type dataset_ids: list
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: base vehicle submodels data
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
            data = sema_client.retrieve_submodels(
                brand_ids=brand_ids,
                dataset_ids=dataset_ids,
                year=self.make_year.year.year,
                make_id=self.make_year.make.make_id,
                model_id=self.model.model_id
            )
            if annotated:
                data = {
                    'base_vehicle_id_': self.base_vehicle_id,
                    'year_': self.make_year.year.year,
                    'make_id_': self.make_year.make.make_id,
                    'model_id_': self.model.model_id,
                    'submodels_': data
                }
                if brand_ids:
                    data['brand_ids_'] = brand_ids
                if dataset_ids:
                    data['dataset_ids_'] = dataset_ids
                data = [data]
            return data
        except Exception:
            raise

    def retrieve_engines_data_from_api(self, brand_ids=None, dataset_ids=None,
                                       annotated=False):
        """
        Retrieves base vehicle engines data from SEMA API.

        :param brand_ids: brand IDs on which to filter
        :type brand_ids: list
        :param dataset_ids: dataset IDs on which to filter
        :type dataset_ids: list
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: base vehicle engines data
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
            data = sema_client.retrieve_engines(
                brand_ids=brand_ids,
                dataset_ids=dataset_ids,
                year=self.make_year.year.year,
                make_id=self.make_year.make.make_id,
                model_id=self.model.model_id
            )
            if annotated:
                data = {
                    'base_vehicle_id_': self.base_vehicle_id,
                    'year_': self.make_year.year.year,
                    'make_id_': self.make_year.make.make_id,
                    'model_id_': self.model.model_id,
                    'engines_': data
                }
                if brand_ids:
                    data['brand_ids_'] = brand_ids
                if dataset_ids:
                    data['dataset_ids_'] = dataset_ids
                data = [data]
            return data
        except Exception:
            raise

    def retrieve_vehicle_info_data_from_api(self, annotated=False):
        """
        Retrieves base vehicle vehicle info data from SEMA API.

        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: base vehicle vehicle info data
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
                    }
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
            data = sema_client.retrieve_vehicle_info(
                base_vehicle_id=self.base_vehicle_id
            )
            if annotated:
                data = {
                    'base_vehicle_id_': self.base_vehicle_id,
                    'vehicles_': data
                }
                data = [data]
            return data
        except Exception:
            raise

    def retrieve_categories_data_from_api(self, brand_ids=None,
                                          dataset_ids=None, by_names=False,
                                          annotated=False):
        """
        Retrieves base vehicle categories data from SEMA API.

        :param brand_ids: brand IDs on which to filter
        :type brand_ids: list
        :param dataset_ids: dataset IDs on which to filter
        :type dataset_ids: list
        :param by_names: whether or not to filter by names rather than
            ID
        :type by_names: bool
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: base vehicle categories data
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
            if by_names:
                data = sema_client.retrieve_categories(
                    brand_ids=brand_ids,
                    dataset_ids=dataset_ids,
                    year=self.make_year.year.year,
                    make_name=self.make_year.make.name,
                    model_name=self.model.name
                )
            else:
                data = sema_client.retrieve_categories(
                    brand_ids=brand_ids,
                    dataset_ids=dataset_ids,
                    base_vehicle_ids=[self.base_vehicle_id]
                )
            if annotated:
                data = {
                    'base_vehicle_id_': self.base_vehicle_id,
                    'year_': self.make_year.year.year,
                    'make_id_': self.make_year.make.make_id,
                    'make_name_': self.make_year.make.name,
                    'model_id_': self.model.model_id,
                    'model_name_': self.model.name,
                    'categories_': data
                }
                if brand_ids:
                    data['brand_ids_'] = brand_ids
                if dataset_ids:
                    data['dataset_ids_'] = dataset_ids
                data = [data]
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
        Retrieves base vehicle products by brand data from SEMA API.

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

        :return: base vehicle products data
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
            if by_names:
                data = sema_client.retrieve_products_by_brand(
                    brand_ids=brand_ids,
                    dataset_ids=dataset_ids,
                    year=self.make_year.year.year,
                    make_name=self.make_year.make.name,
                    model_name=self.model.name,
                    part_numbers=part_numbers,
                    pies_segments=pies_segments
                )
            else:
                data = sema_client.retrieve_products_by_brand(
                    brand_ids=brand_ids,
                    dataset_ids=dataset_ids,
                    base_vehicle_ids=[self.base_vehicle_id],
                    part_numbers=part_numbers,
                    pies_segments=pies_segments
                )
            if annotated:
                data = {
                    'base_vehicle_id_': self.base_vehicle_id,
                    'year_': self.make_year.year.year,
                    'make_id_': self.make_year.make.make_id,
                    'make_name_': self.make_year.make.name,
                    'model_id_': self.model.model_id,
                    'model_name_': self.model.name,
                    'products_': data
                }
                if brand_ids:
                    data['brand_ids_'] = brand_ids
                if dataset_ids:
                    data['dataset_ids_'] = dataset_ids
                if part_numbers:
                    data['part_numbers_'] = part_numbers
                data = [data]
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
        Retrieves base vehicle products by category data from SEMA API.

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

        :return: base vehicle products by category data
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
            if by_names:
                data = sema_client.retrieve_products_by_category(
                    category_id=category_id,
                    brand_ids=brand_ids,
                    dataset_ids=dataset_ids,
                    year=self.make_year.year.year,
                    make_name=self.make_year.make.name,
                    model_name=self.model.name,
                    part_numbers=part_numbers,
                    pies_segments=pies_segments
                )
            else:
                data = sema_client.retrieve_products_by_category(
                    category_id=category_id,
                    brand_ids=brand_ids,
                    dataset_ids=dataset_ids,
                    base_vehicle_ids=[self.base_vehicle_id],
                    part_numbers=part_numbers,
                    pies_segments=pies_segments
                )
            if annotated:
                data = {
                    'base_vehicle_id_': self.base_vehicle_id,
                    'year_': self.make_year.year.year,
                    'make_id_': self.make_year.make.make_id,
                    'make_name_': self.make_year.make.name,
                    'model_id_': self.model.model_id,
                    'model_name_': self.model.name,
                    'products_': data
                }
                if brand_ids:
                    data['brand_ids_'] = brand_ids
                if dataset_ids:
                    data['dataset_ids_'] = dataset_ids
                if part_numbers:
                    data['part_numbers_'] = part_numbers
                data = [data]
            return data
        except Exception:
            raise
    # </editor-fold>

    # <editor-fold desc="update properties ...">
    @property
    def state(self):
        """
        Returns a dictionary of fields and values relevant to updates.

        :return: current values of fields relevant to updates
        :rtype: dict

        """

        state = dict(super().state)
        state.update(
            {
                'Make Year': str(self.make_year),
                'Model': str(self.model)
            }
        )
        return state
    # </editor-fold>

    objects = SemaBaseVehicleManager()

    class Meta:
        ordering = ['make_year', 'model']
        unique_together = ['make_year', 'model']
        verbose_name = 'SEMA base vehicle'

    def __str__(self):
        return f'{self.make_year} :: {self.model}'


class SemaVehicle(SemaBaseModel):
    """
    This model class defines SEMA vehicles.

    """

    vehicle_id = PositiveIntegerField(
        primary_key=True,
        unique=True
    )
    base_vehicle = ForeignKey(
        SemaBaseVehicle,
        on_delete=CASCADE,
        related_name='vehicles'
    )
    submodel = ForeignKey(
        SemaSubmodel,
        on_delete=CASCADE,
        related_name='vehicles'
    )

    # <editor-fold desc="relevancy properties ...">
    @property
    def may_be_relevant(self):
        """
        Returns whether or not object may be relevant based on
        attributes and related attributes.

        .. Topic:: **-May Be Relevant Conditions-**

            1. base vehicle is relevant, and
            2. submodel is relevant

        :return: whether or not object may be relevant
        :rtype: bool

        """

        return bool(self.engine_relevant_count)

    @property
    def relevancy_errors(self):
        """
        Returns a concatenation of errors based on relevancy.

        :return: errors based on relevancy
        :rtype: str

        """

        msgs = []
        if self.is_relevant:
            if not self.engine_relevant_count:
                error = "no relevant engines"
                msgs.append(error)
        return ', '.join(msgs)
    relevancy_errors.fget.short_description = 'Errors'
    # </editor-fold>

    # <editor-fold desc="count properties ...">
    @property
    def dataset_count(self):
        """
        Returns dataset count.

        :return: dataset count
        :rtype: int

        """

        return self.datasets.distinct().count()

    @property
    def dataset_relevant_count(self):
        """
        Returns relevant dataset count.

        :return: relevant dataset count
        :rtype: int

        """

        return self.datasets.filter(is_relevant=True).distinct().count()
    dataset_relevant_count.fget.short_description = 'Relevant Dataset Count'

    @property
    def engine_count(self):
        """
        Returns engine count.

        :return: engine count
        :rtype: int

        """

        return self.engines.distinct().count()

    @property
    def engine_relevant_count(self):
        """
        Returns relevant engine count.

        :return: relevant engine count
        :rtype: int

        """

        return self.engines.filter(is_relevant=True).distinct().count()
    engine_relevant_count.fget.short_description = 'Relevant Engine Count'

    @property
    def product_count(self):
        """
        Returns product count.

        :return: product count
        :rtype: int

        """

        return self.products.distinct().count()

    @property
    def product_relevant_count(self):
        """
        Returns relevant product count.

        :return: relevant product count
        :rtype: int

        """

        return self.products.filter(is_relevant=True).distinct().count()
    product_relevant_count.fget.short_description = 'Relevant Product Count'
    # </editor-fold>

    # <editor-fold desc="retrieve properties ...">
    def retrieve_vehicle_info_data_from_api(self, annotated=False):
        """
        Retrieves vehicle vehicle info data from SEMA API.

        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: vehicle vehicle info data
        :rtype: list

        :raises Exception: on general exception

        **-Return Format-**
        ::
            if annotated:
                ret = [
                    {
                        "base_vehicle_id_": <int>,
                        "vehicle_id": <int>,
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
                    }
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
            data = sema_client.retrieve_vehicle_info(
                vehicle_id=self.vehicle_id
            )
            if annotated:
                data = {
                    'base_vehicle_id_': self.base_vehicle.base_vehicle_id,
                    'vehicle_id': self.vehicle_id,
                    'vehicles_': data
                }
                data = [data]
            return data
        except Exception:
            raise

    def retrieve_categories_data_from_api(self, brand_ids=None,
                                          dataset_ids=None, by_names=False,
                                          annotated=False):
        """
        Retrieves vehicle categories data from SEMA API.

        :param brand_ids: brand IDs on which to filter
        :type brand_ids: list
        :param dataset_ids: dataset IDs on which to filter
        :type dataset_ids: list
        :param by_names: whether or not to filter by names rather than
            ID
        :type by_names: bool
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: vehicle categories data
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
            if by_names:
                data = sema_client.retrieve_categories(
                    brand_ids=brand_ids,
                    dataset_ids=dataset_ids,
                    year=self.base_vehicle.make_year.year.year,
                    make_name=self.base_vehicle.make_year.make.name,
                    model_name=self.base_vehicle.model.name,
                    submodel_name=self.submodel.name
                )
            else:
                data = sema_client.retrieve_categories(
                    brand_ids=brand_ids,
                    dataset_ids=dataset_ids,
                    vehicle_ids=[self.vehicle_id]
                )
            if annotated:
                data = {
                    'base_vehicle_id_': self.base_vehicle.base_vehicle_id,
                    'vehicle_id_': self.vehicle_id,
                    'year_': self.base_vehicle.make_year.year.year,
                    'make_id_': self.base_vehicle.make_year.make.make_id,
                    'make_name_': self.base_vehicle.make_year.make.name,
                    'model_id_': self.base_vehicle.model.model_id,
                    'model_name_': self.base_vehicle.model.name,
                    'submodel_id_': self.submodel.submodel_id,
                    'submodel_name_': self.submodel.name,
                    'categories_': data
                }
                if brand_ids:
                    data['brand_ids_'] = brand_ids
                if dataset_ids:
                    data['dataset_ids_'] = dataset_ids
                data = [data]
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
        Retrieves vehicle products by brand data from SEMA API.

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

        :return: vehicle products data
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
            if by_names:
                data = sema_client.retrieve_products_by_brand(
                    brand_ids=brand_ids,
                    dataset_ids=dataset_ids,
                    year=self.base_vehicle.make_year.year.year,
                    make_name=self.base_vehicle.make_year.make.name,
                    model_name=self.base_vehicle.model.name,
                    submodel_name=self.submodel.name,
                    part_numbers=part_numbers,
                    pies_segments=pies_segments
                )
            else:
                data = sema_client.retrieve_products_by_brand(
                    brand_ids=brand_ids,
                    dataset_ids=dataset_ids,
                    vehicle_ids=[self.vehicle_id],
                    part_numbers=part_numbers,
                    pies_segments=pies_segments
                )
            if annotated:
                data = {
                    'base_vehicle_id_': self.base_vehicle.base_vehicle_id,
                    'vehicle_id_': self.vehicle_id,
                    'year_': self.base_vehicle.make_year.year.year,
                    'make_id_': self.base_vehicle.make_year.make.make_id,
                    'make_name_': self.base_vehicle.make_year.make.name,
                    'model_id_': self.base_vehicle.model.model_id,
                    'model_name_': self.base_vehicle.model.name,
                    'submodel_id_': self.submodel.submodel_id,
                    'submodel_name_': self.submodel.name,
                    'products_': data
                }
                if brand_ids:
                    data['brand_ids_'] = brand_ids
                if dataset_ids:
                    data['dataset_ids_'] = dataset_ids
                if part_numbers:
                    data['part_numbers_'] = part_numbers
                data = [data]
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
        Retrieves vehicle products by category data from SEMA API.

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

        :return: vehicle products by category data
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
            if by_names:
                data = sema_client.retrieve_products_by_category(
                    category_id=category_id,
                    brand_ids=brand_ids,
                    dataset_ids=dataset_ids,
                    year=self.base_vehicle.make_year.year.year,
                    make_name=self.base_vehicle.make_year.make.name,
                    model_name=self.base_vehicle.model.name,
                    submodel_name=self.submodel.name,
                    part_numbers=part_numbers,
                    pies_segments=pies_segments
                )
            else:
                data = sema_client.retrieve_products_by_category(
                    category_id=category_id,
                    brand_ids=brand_ids,
                    dataset_ids=dataset_ids,
                    vehicle_ids=[self.vehicle_id],
                    part_numbers=part_numbers,
                    pies_segments=pies_segments
                )
            if annotated:
                data = {
                    'base_vehicle_id_': self.base_vehicle_id,
                    'year_': self.base_vehicle.make_year.year.year,
                    'make_id_': self.base_vehicle.make_year.make.make_id,
                    'make_name_': self.base_vehicle.make_year.make.name,
                    'model_id_': self.base_vehicle.model.model_id,
                    'model_name_': self.base_vehicle.model.name,
                    'submodel_id_': self.submodel.submodel_id,
                    'submodel_name_': self.submodel.name,
                    'products_': data
                }
                if brand_ids:
                    data['brand_ids_'] = brand_ids
                if dataset_ids:
                    data['dataset_ids_'] = dataset_ids
                if part_numbers:
                    data['part_numbers_'] = part_numbers
                data = [data]
            return data
        except Exception:
            raise
    # </editor-fold>

    # <editor-fold desc="update properties ...">
    @property
    def state(self):
        """
        Returns a dictionary of fields and values relevant to updates.

        :return: current values of fields relevant to updates
        :rtype: dict

        """

        state = dict(super().state)
        state.update(
            {
                'Base Vehicle': str(self.base_vehicle),
                'Submodel': str(self.submodel)
            }
        )
        return state
    # </editor-fold>

    objects = SemaVehicleManager()

    class Meta:
        ordering = ['base_vehicle', 'submodel']
        unique_together = ['base_vehicle', 'submodel']
        verbose_name = 'SEMA vehicle'

    def __str__(self):
        return f'{self.base_vehicle} :: {self.submodel}'


class SemaEngine(SemaBaseModel):
    """
    This model class defines SEMA vehicle engines.

    """

    vehicle = ForeignKey(
        SemaVehicle,
        on_delete=CASCADE,
        related_name='engines'
    )
    litre = CharField(
        max_length=10
    )
    cc = CharField(
        max_length=10
    )
    cid = CharField(
        max_length=10
    )
    cylinders = CharField(
        max_length=10
    )
    block_type = CharField(
        max_length=10
    )
    engine_bore_in = CharField(
        max_length=10
    )
    engine_bore_metric = CharField(
        max_length=10
    )
    engine_stroke_in = CharField(
        max_length=10
    )
    engine_stroke_metric = CharField(
        max_length=10
    )
    valves_per_engine = CharField(
        max_length=10
    )
    aspiration = CharField(
        max_length=50
    )
    cylinder_head_type = CharField(
        max_length=10
    )
    fuel_type = CharField(
        max_length=20
    )
    ignition_system_type = CharField(
        max_length=50
    )
    manufacturer = CharField(
        max_length=50
    )
    horse_power = CharField(
        max_length=10
    )
    kilowatt_power = CharField(
        max_length=10
    )
    engine_designation = CharField(
        max_length=10
    )

    # <editor-fold desc="relevancy properties ...">
    @property
    def may_be_relevant(self):
        """
        Returns whether or not object may be relevant based on
        attributes and related attributes.

        .. Topic:: **-May Be Relevant Conditions-**

            1. vehicle make is relevant, and
            2. fuel type is diesel

        :return: whether or not object may be relevant
        :rtype: bool

        """

        return bool(
            self.vehicle.base_vehicle.make_year.make.is_relevant
            and self.fuel_type == 'DIESEL'
        )

    @property
    def relevancy_errors(self):
        """
        Returns a concatenation of errors based on relevancy.

        :return: errors based on relevancy
        :rtype: str

        """

        msgs = []
        if self.is_relevant:
            if not self.vehicle.base_vehicle.make_year.make.is_relevant:
                error = "make not relevant"
                msgs.append(error)
            if not self.fuel_type == 'DIESEL':
                error = "not diesel"
                msgs.append(error)
        return ', '.join(msgs)
    relevancy_errors.fget.short_description = 'Errors'
    # </editor-fold>

    # <editor-fold desc="update properties ...">
    @property
    def state(self):
        """
        Returns a dictionary of fields and values relevant to updates.

        :return: current values of fields relevant to updates
        :rtype: dict

        """

        state = dict(super().state)
        state.update(
            {
                'Vehicle': str(self.vehicle),
                'Litre': self.litre,
                'CC': self.cc,
                'CID': self.cid,
                'Cylinders': self.cylinders,
                'Block': self.block_type,
                'Bore In': self.engine_bore_in,
                'Bore Met': self.engine_bore_metric,
                'Stroke In': self.engine_stroke_in,
                'Stroke Met': self.engine_stroke_metric,
                'Valves': self.valves_per_engine,
                'Aspiration': self.aspiration,
                'Cylinder Head': self.cylinder_head_type,
                'Fuel': self.fuel_type,
                'Ignition System': self.ignition_system_type,
                'Manufacturer': self.manufacturer,
                'Horse Power': self.horse_power,
                'Kilowatt Power': self.kilowatt_power,
                'Engine Designation': self.engine_designation
            }
        )
        return state
    # </editor-fold>

    objects = SemaEngineManager()

    class Meta:
        verbose_name = 'SEMA engine'

    def __str__(self):
        return f'{self.vehicle} :: {self.litre} :: {self.fuel_type}'


class SemaCategory(SemaBaseModel):
    """
    This model class defines SEMA categories.

    """

    category_id = PositiveIntegerField(
        primary_key=True,
        unique=True
    )
    name = CharField(
        max_length=100,
    )
    parent_categories = ManyToManyField(
        'self',
        blank=True,
        related_name='child_categories',
        symmetrical=False
    )

    @property
    def tag_name(self):
        name = self.name
        return f'category:{slugify(name)}-{self.level}'

    @property
    def level(self):
        if self.parent_category_count:
            if self.child_category_count:
                return '2'
            else:
                return '3'
        else:
            if self.child_category_count:
                return '1'
            else:
                return ''

    # <editor-fold desc="relevancy properties ...">
    @property
    def may_be_relevant(self):
        """
        Returns whether or not object may be relevant based on
        attributes and related attributes.

        .. Topic:: **-May Be Relevant Conditions-**

            1. always relevant

        :return: whether or not object may be relevant
        :rtype: bool

        """

        return True

    @property
    def relevancy_errors(self):
        """
        Returns a concatenation of errors based on relevancy.

        :return: errors based on relevancy
        :rtype: str

        """

        msgs = []
        if self.is_relevant:
            if not self.level:
                error = "invalid level"
                msgs.append(error)
        return ', '.join(msgs)
    relevancy_errors.fget.short_description = 'Errors'
    # </editor-fold>

    # <editor-fold desc="count properties ...">
    @property
    def dataset_count(self):
        """
        Returns dataset count.

        :return: dataset count
        :rtype: int

        """

        return self.datasets.distinct().count()

    @property
    def dataset_relevant_count(self):
        """
        Returns relevant dataset count.

        :return: relevant dataset count
        :rtype: int

        """

        return self.datasets.filter(is_relevant=True).distinct().count()
    dataset_relevant_count.fget.short_description = 'Relevant Dataset Count'

    @property
    def product_count(self):
        """
        Returns product count.

        :return: product count
        :rtype: int

        """

        return self.products.distinct().count()

    @property
    def product_relevant_count(self):
        """
        Returns relevant product count.

        :return: relevant product count
        :rtype: int

        """

        return self.products.filter(is_relevant=True).distinct().count()
    product_relevant_count.fget.short_description = 'Relevant Product Count'

    @property
    def parent_category_count(self):
        """
        Returns parent category count.

        :return: parent category count
        :rtype: int

        """

        return self.parent_categories.distinct().count()
    parent_category_count.fget.short_description = 'Parent Count'

    @property
    def parent_category_relevant_count(self):
        """
        Returns relevant parent category count.

        :return: relevant parent category count
        :rtype: int

        """

        return self.parent_categories.filter(
            is_relevant=True
        ).distinct().count()
    parent_category_count.fget.short_description = 'Relevant Parent Count'

    @property
    def child_category_count(self):
        """
        Returns child category count.

        :return: child category count
        :rtype: int

        """

        return self.child_categories.distinct().count()
    child_category_count.fget.short_description = 'Child Count'

    @property
    def child_category_relevant_count(self):
        """
        Returns relevant child category count.

        :return: relevant child category count
        :rtype: int

        """

        return self.child_categories.distinct().filter(
            is_relevant=True
        ).count()
    child_category_relevant_count.fget.short_description = (
        'Relevant Child Count'
    )
    # </editor-fold>

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
        Retrieves category products data from SEMA API.

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

        :return: category products data
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
            data = sema_client.retrieve_products_by_category(
                category_id=self.category_id,
                brand_ids=brand_ids,
                dataset_ids=dataset_ids,
                base_vehicle_ids=base_vehicle_ids,
                vehicle_ids=vehicle_ids,
                year=year,
                make_name=make_name,
                model_name=model_name,
                submodel_name=submodel_name,
                part_numbers=part_numbers,
                pies_segments=pies_segments
            )
            if annotated:
                data = {
                    'category_id_': self.category_id,
                    'products_': data
                }
                if brand_ids:
                    data['brand_ids_'] = brand_ids
                if dataset_ids:
                    data['dataset_ids_'] = dataset_ids
                if base_vehicle_ids:
                    data['base_vehicles_ids_'] = base_vehicle_ids
                if vehicle_ids:
                    data['vehicles_ids_'] = vehicle_ids
                if year:
                    data['year_'] = year
                if make_name:
                    data['make_name_'] = make_name
                if model_name:
                    data['model_name_'] = model_name
                if submodel_name:
                    data['submodel_name_'] = submodel_name
                if part_numbers:
                    data['part_numbers_'] = part_numbers
                data = [data]
            return data
        except Exception:
            raise
    # </editor-fold>

    # <editor-fold desc="update properties ...">
    @property
    def state(self):
        """
        Returns a dictionary of fields and values relevant to updates.

        :return: current values of fields relevant to updates
        :rtype: dict

        """

        state = dict(super().state)
        state.update(
            {
                'Name': self.name,
                'Parent': str(self.parent_categories.all())
            }
        )
        return state
    # </editor-fold>

    # <editor-fold desc="perform properties ...">
    def perform_category_products_update_from_api(self, **filters):
        msgs = []
        try:
            if 'brand_ids' in filters or 'dataset_ids' in filters:
                data = self.retrieve_products_by_category_data_from_api(
                    annotated=True,
                    **filters
                )
            else:
                datasets = self.datasets.filter(is_authorized=True)
                data = datasets.retrieve_products_by_category_data_from_api(
                    category_id=self.category_id,
                    annotated=True,
                    **filters
                )
        except Exception as err:
            msgs.append(self.get_instance_error_msg(str(err)))
            return msgs

        for item in data:
            if item['category_id_'] == self.category_id:
                for product_item in item['products_']:
                    try:
                        if (product_item['ProductId']
                                in self.products.values_list(
                                    'product_id', flat=True)):
                            msgs.append(
                                self.get_instance_up_to_date_msg(
                                    message=(
                                        f"{product_item['PartNumber']} "
                                        "already added"
                                    )
                                )
                            )
                        else:
                            self.products.add(product_item['ProductId'])
                            self.save()
                            msgs.append(
                                self.get_update_success_msg(
                                    message=(
                                        f"{product_item['PartNumber']} added"
                                    )
                                )
                            )
                    except Exception as err:
                        msgs.append(self.get_instance_error_msg(str(err)))
                        continue
            else:
                msgs.append(
                    self.get_instance_error_msg(
                        error="Incorrect category returned"
                    )
                )
                continue

        if not msgs:
            msgs.append(self.get_instance_up_to_date_msg())
        return msgs
    # </editor-fold>

    objects = SemaCategoryManager()

    class Meta:
        ordering = ['name']
        verbose_name = 'SEMA category'
        verbose_name_plural = 'SEMA categories'

    def __str__(self):
        return f'{self.level}: {self.name}'


class SemaBrand(SemaBaseModel):
    """
    This model class defines SEMA brands.

    """

    brand_id = CharField(
        primary_key=True,
        max_length=10,
        unique=True
    )
    name = CharField(
        max_length=50,
    )
    primary_image_url = URLField(
        blank=True
    )

    @property
    def tag_name(self):
        return f'brand:{slugify(self.name)}'

    # <editor-fold desc="relevancy properties ...">
    @property
    def may_be_relevant(self):
        """
        Returns whether or not object may be relevant based on
        attributes and related attributes.

        .. Topic:: **-May Be Relevant Conditions-**

            1. has relevant datasets

        :return: whether or not object may be relevant
        :rtype: bool

        """

        return bool(self.dataset_relevant_count)

    @property
    def relevancy_errors(self):
        """
        Returns a concatenation of errors based on relevancy.

        :return: errors based on relevancy
        :rtype: str

        """

        msgs = []
        if self.is_relevant:
            if not self.dataset_relevant_count:
                error = "no relevant datasets"
                msgs.append(error)
            if not self.primary_image_url or self.primary_image_url == '':
                error = "missing image"
                msgs.append(error)
        return ', '.join(msgs)
    relevancy_errors.fget.short_description = 'Errors'
    # </editor-fold>

    # <editor-fold desc="count properties ...">
    @property
    def dataset_count(self):
        """
        Returns dataset count.

        :return: dataset count
        :rtype: int

        """

        return self.datasets.distinct().count()

    @property
    def dataset_relevant_count(self):
        """
        Returns relevant dataset count.

        :return: relevant dataset count
        :rtype: int

        """

        return self.datasets.filter(is_relevant=True).distinct().count()
    dataset_relevant_count.fget.short_description = 'Relevant Dataset Count'
    # </editor-fold>

    # <editor-fold desc="retrieve properties ...">
    def retrieve_years_data_from_api(self, annotated=False):
        """
        Retrieves brand years data from SEMA API.

        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: brand years data
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
            data = sema_client.retrieve_years(
                brand_ids=[self.brand_id]
            )
            if annotated:
                data = {
                    'brand_id_': self.brand_id,
                    'years_': data
                }
                data = [data]
            return data
        except Exception:
            raise

    def retrieve_makes_data_from_api(self, year=None, annotated=False):
        """
        Retrieves brand makes data from SEMA API.

        :param year: year on which to filter
        :type year: int
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: brand makes data
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
            data = sema_client.retrieve_makes(
                brand_ids=[self.brand_id],
                year=year
            )
            if annotated:
                data = {
                    'brand_id_': self.brand_id,
                    'makes_': data
                }
                if year:
                    data['year_'] = year
                data = [data]
            return data
        except Exception:
            raise

    def retrieve_models_data_from_api(self, year=None,
                                      make_id=None, annotated=False):
        """
        Retrieves brand models data from SEMA API.

        :param year: year on which to filter
        :type year: int
        :param make_id: make ID on which to filter
        :type make_id: int
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: brand models data
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
            data = sema_client.retrieve_models(
                brand_ids=[self.brand_id],
                year=year,
                make_id=make_id
            )
            if annotated:
                data = {
                    'brand_id_': self.brand_id,
                    'models_': data
                }
                if year:
                    data['year_'] = year
                if make_id:
                    data['make_id_'] = make_id
                data = [data]
            return data
        except Exception:
            raise

    def retrieve_submodels_data_from_api(self, year=None, make_id=None,
                                         model_id=None, annotated=False):
        """
        Retrieves brand submodels data from SEMA API.

        :param year: year on which to filter
        :type year: int
        :param make_id: make ID on which to filter
        :type make_id: int
        :param model_id: model ID on which to filter
        :type model_id: int
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: brand submodels data
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
            data = sema_client.retrieve_submodels(
                brand_ids=[self.brand_id],
                year=year,
                make_id=make_id,
                model_id=model_id
            )
            if annotated:
                data = {
                    'brand_id_': self.brand_id,
                    'submodels_': data
                }
                if year:
                    data['year_'] = year
                if make_id:
                    data['make_id_'] = make_id
                if model_id:
                    data['model_id_'] = model_id
                data = [data]
            return data
        except Exception:
            raise

    def retrieve_engines_data_from_api(self, year=None, make_id=None,
                                       model_id=None, annotated=False):
        """
        Retrieves brand engines data from SEMA API.

        :param year: year on which to filter
        :type year: int
        :param make_id: make ID on which to filter
        :type make_id: int
        :param model_id: model ID on which to filter
        :type model_id: int
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: brand engines data
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
            data = sema_client.retrieve_engines(
                brand_ids=[self.brand_id],
                year=year,
                make_id=make_id,
                model_id=model_id
            )
            if annotated:
                data = {
                    'brand_id_': self.brand_id,
                    'engines_': data
                }
                if year:
                    data['year_'] = year
                if make_id:
                    data['make_id_'] = make_id
                if model_id:
                    data['model_id_'] = model_id
                data = [data]
            return data
        except Exception:
            raise

    def retrieve_categories_data_from_api(self, base_vehicle_ids=None,
                                          vehicle_ids=None, year=None,
                                          make_name=None, model_name=None,
                                          submodel_name=None,
                                          annotated=False):
        """
        Retrieves brand categories data from SEMA API.

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

        :return: brand categories data
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
            data = sema_client.retrieve_categories(
                brand_ids=[self.brand_id],
                base_vehicle_ids=base_vehicle_ids,
                vehicle_ids=vehicle_ids,
                year=year,
                make_name=make_name,
                model_name=model_name,
                submodel_name=submodel_name
            )
            if annotated:
                data = {
                    'brand_id_': self.brand_id,
                    'categories_': data
                }
                if base_vehicle_ids:
                    data['base_vehicles_ids_'] = base_vehicle_ids
                if vehicle_ids:
                    data['vehicles_ids_'] = vehicle_ids
                if year:
                    data['year_'] = year
                if make_name:
                    data['make_name_'] = make_name
                if model_name:
                    data['model_name_'] = model_name
                if submodel_name:
                    data['submodel_name_'] = submodel_name
                data = [data]
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
        Retrieves brand products data from SEMA API.

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

        :return: brand products data
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
            data = sema_client.retrieve_products_by_brand(
                brand_ids=[self.brand_id],
                base_vehicle_ids=base_vehicle_ids,
                vehicle_ids=vehicle_ids,
                year=year,
                make_name=make_name,
                model_name=model_name,
                submodel_name=submodel_name,
                pies_segments=pies_segments,
                part_numbers=part_numbers
            )
            if annotated:
                data = {
                    'brand_id_': self.brand_id,
                    'products_': data
                }
                if base_vehicle_ids:
                    data['base_vehicles_ids_'] = base_vehicle_ids
                if vehicle_ids:
                    data['vehicles_ids_'] = vehicle_ids
                if year:
                    data['year_'] = year
                if make_name:
                    data['make_name_'] = make_name
                if model_name:
                    data['model_name_'] = model_name
                if submodel_name:
                    data['submodel_name_'] = submodel_name
                if part_numbers:
                    data['part_numbers_'] = part_numbers
                data = [data]
            return data
        except Exception:
            raise

    def retrieve_products_by_category_data_from_api(self, category_id,
                                                    base_vehicle_ids=None,
                                                    vehicle_ids=None, year=None,
                                                    make_name=None,
                                                    model_name=None,
                                                    submodel_name=None,
                                                    part_numbers=None,
                                                    pies_segments=None,
                                                    annotated=False):
        """
        Retrieves brand products by category data from SEMA API.

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

        :return: brand products by category data
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
            data = sema_client.retrieve_products_by_category(
                category_id=category_id,
                brand_ids=[self.brand_id],
                base_vehicle_ids=base_vehicle_ids,
                vehicle_ids=vehicle_ids,
                year=year,
                make_name=make_name,
                model_name=model_name,
                submodel_name=submodel_name,
                part_numbers=part_numbers,
                pies_segments=pies_segments
            )
            if annotated:
                data = {
                    'brand_id_': self.brand_id,
                    'category_id_': category_id,
                    'products_': data
                }
                if base_vehicle_ids:
                    data['base_vehicles_ids_'] = base_vehicle_ids
                if vehicle_ids:
                    data['vehicles_ids_'] = vehicle_ids
                if year:
                    data['year_'] = year
                if make_name:
                    data['make_name_'] = make_name
                if model_name:
                    data['model_name_'] = model_name
                if submodel_name:
                    data['submodel_name_'] = submodel_name
                if part_numbers:
                    data['part_numbers_'] = part_numbers
                data = [data]
            return data
        except Exception:
            raise

    def retrieve_vehicles_by_product_data_from_api(self, part_numbers=None,
                                                   annotated=False):
        """
        Retrieves brand vehicles by product data from SEMA API.

        :param part_numbers: part numbers on which to filter
        :type part_numbers: list
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: brand vehicles by product data
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
            data = sema_client.retrieve_vehicles_by_product(
                brand_id=self.brand_id,
                part_numbers=part_numbers
            )
            if annotated:
                data = {
                    'brand_id_': self.brand_id,
                    'products_': data
                }
                if part_numbers:
                    data['part_numbers_'] = part_numbers
                data = [data]
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
                    }
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
            data = sema_client.retrieve_vehicles_by_brand(
                brand_ids=[self.brand_id]
            )
            if annotated:
                data = {
                    'brand_id_': self.brand_id,
                    'vehicles_': data
                }
                data = [data]
            return data
        except Exception:
            raise
    # </editor-fold>

    # <editor-fold desc="update properties ...">
    @property
    def state(self):
        """
        Returns a dictionary of fields and values relevant to updates.

        :return: current values of fields relevant to updates
        :rtype: dict

        """

        state = dict(super().state)
        state.update(
            {
                'Name': self.name
            }
        )
        return state
    # </editor-fold>

    objects = SemaBrandManager()

    class Meta:
        ordering = ['name']
        verbose_name = 'SEMA brand'

    def __str__(self):
        return str(self.name)


class SemaDataset(SemaBaseModel):
    """
    This model class defines SEMA datasets.

    """

    dataset_id = PositiveIntegerField(
        primary_key=True,
        unique=True
    )
    name = CharField(
        max_length=50,
    )
    brand = ForeignKey(
        SemaBrand,
        on_delete=CASCADE,
        related_name='datasets'
    )
    categories = ManyToManyField(
        SemaCategory,
        blank=True,
        related_name='datasets'
    )
    vehicles = ManyToManyField(
        SemaVehicle,
        blank=True,
        related_name='datasets'
    )

    # <editor-fold desc="count properties ...">
    @property
    def category_count(self):
        """
        Returns category count.

        :return: category count
        :rtype: int

        """

        return self.categories.distinct().count()

    @property
    def category_relevant_count(self):
        """
        Returns relevant category count.

        :return: relevant category count
        :rtype: int

        """

        return self.categories.filter(is_relevant=True).distinct().count()
    category_relevant_count.fget.short_description = 'Relevant Category Count'

    @property
    def vehicle_count(self):
        """
        Returns vehicle count.

        :return: vehicle count
        :rtype: int

        """

        return self.vehicles.distinct().count()

    @property
    def vehicle_relevant_count(self):
        """
        Returns relevant vehicle count.

        :return: relevant vehicle count
        :rtype: int

        """

        return self.vehicles.filter(is_relevant=True).distinct().count()
    vehicle_relevant_count.fget.short_description = 'Relevant Vehicle Count'

    @property
    def product_count(self):
        """
        Returns product count.

        :return: product count
        :rtype: int

        """

        return self.products.distinct().count()

    @property
    def product_relevant_count(self):
        """
        Returns relevant product count.

        :return: relevant product count
        :rtype: int

        """
        return self.products.filter(is_relevant=True).distinct().count()
    product_relevant_count.fget.short_description = 'Relevant Product Count'
    # </editor-fold>

    # <editor-fold desc="retrieve properties ...">
    def retrieve_years_data_from_api(self, annotated=False):
        """
        Retrieves dataset years data from SEMA API.

        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: dataset years data
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
            data = sema_client.retrieve_years(
                dataset_ids=[self.dataset_id]
            )
            if annotated:
                data = {
                    'brand_id_': self.brand.brand_id,
                    'dataset_id_': self.dataset_id,
                    'years_': data
                }
                data = [data]
            return data
        except Exception:
            raise

    def retrieve_makes_data_from_api(self, year=None, annotated=False):
        """
        Retrieves dataset makes data from SEMA API.

        :param year: year on which to filter
        :type year: int
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: dataset makes data
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
            data = sema_client.retrieve_makes(
                dataset_ids=[self.dataset_id],
                year=year
            )
            if annotated:
                data = {
                    'brand_id_': self.brand.brand_id,
                    'dataset_id_': self.dataset_id,
                    'makes_': data
                }
                if year:
                    data['year_'] = year
                data = [data]
            return data
        except Exception:
            raise

    def retrieve_models_data_from_api(self, year=None,
                                      make_id=None, annotated=False):
        """
        Retrieves dataset models data from SEMA API.

        :param year: year on which to filter
        :type year: int
        :param make_id: make ID on which to filter
        :type make_id: int
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: dataset models data
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
            data = sema_client.retrieve_models(
                dataset_ids=[self.dataset_id],
                year=year,
                make_id=make_id
            )
            if annotated:
                data = {
                    'brand_id_': self.brand.brand_id,
                    'dataset_id_': self.dataset_id,
                    'models_': data
                }
                if year:
                    data['year_'] = year
                if make_id:
                    data['make_id_'] = make_id
                data = [data]
            return data
        except Exception:
            raise

    def retrieve_submodels_data_from_api(self, year=None, make_id=None,
                                         model_id=None, annotated=False):
        """
        Retrieves dataset submodels data from SEMA API.

        :param year: year on which to filter
        :type year: int
        :param make_id: make ID on which to filter
        :type make_id: int
        :param model_id: model ID on which to filter
        :type model_id: int
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: dataset submodels data
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
            data = sema_client.retrieve_submodels(
                dataset_ids=[self.dataset_id],
                year=year,
                make_id=make_id,
                model_id=model_id
            )
            if annotated:
                data = {
                    'brand_id_': self.brand.brand_id,
                    'dataset_id_': self.dataset_id,
                    'submodels_': data
                }
                if year:
                    data['year_'] = year
                if make_id:
                    data['make_id_'] = make_id
                if model_id:
                    data['model_id_'] = model_id
                data = [data]
            return data
        except Exception:
            raise

    def retrieve_engines_data_from_api(self, year=None, make_id=None,
                                       model_id=None, annotated=False):
        """
        Retrieves dataset engines data from SEMA API.

        :param year: year on which to filter
        :type year: int
        :param make_id: make ID on which to filter
        :type make_id: int
        :param model_id: model ID on which to filter
        :type model_id: int
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: dataset engines data
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
            data = sema_client.retrieve_engines(
                dataset_ids=[self.dataset_id],
                year=year,
                make_id=make_id,
                model_id=model_id
            )
            if annotated:
                data = {
                    'brand_id_': self.brand.brand_id,
                    'dataset_id_': self.dataset_id,
                    'engines_': data
                }
                if year:
                    data['year_'] = year
                if make_id:
                    data['make_id_'] = make_id
                if model_id:
                    data['model_id_'] = model_id
                data = [data]
            return data
        except Exception:
            raise

    def retrieve_categories_data_from_api(self, base_vehicle_ids=None,
                                          vehicle_ids=None, year=None,
                                          make_name=None, model_name=None,
                                          submodel_name=None, annotated=False):
        """
        Retrieves dataset categories data from SEMA API.

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

        :return: dataset categories data
        :rtype: list

        :raises Exception: on general exception

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
            data = sema_client.retrieve_categories(
                dataset_ids=[self.dataset_id],
                base_vehicle_ids=base_vehicle_ids,
                vehicle_ids=vehicle_ids,
                year=year,
                make_name=make_name,
                model_name=model_name,
                submodel_name=submodel_name
            )
            if annotated:
                data = {
                    'brand_id_': self.brand.brand_id,
                    'dataset_id_': self.dataset_id,
                    'categories_': data
                }
                if base_vehicle_ids:
                    data['base_vehicles_ids_'] = base_vehicle_ids
                if vehicle_ids:
                    data['vehicles_ids_'] = vehicle_ids
                if year:
                    data['year_'] = year
                if make_name:
                    data['make_name_'] = make_name
                if model_name:
                    data['model_name_'] = model_name
                if submodel_name:
                    data['submodel_name_'] = submodel_name
                data = [data]
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
        Retrieves dataset products data from SEMA API.

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

        :return: dataset products data
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
            data = sema_client.retrieve_products_by_brand(
                dataset_ids=[self.dataset_id],
                base_vehicle_ids=base_vehicle_ids,
                vehicle_ids=vehicle_ids,
                year=year,
                make_name=make_name,
                model_name=model_name,
                submodel_name=submodel_name,
                part_numbers=part_numbers,
                pies_segments=pies_segments
            )
            if annotated:
                data = {
                    'brand_id_': self.brand.brand_id,
                    'dataset_id_': self.dataset_id,
                    'products_': data
                }
                if base_vehicle_ids:
                    data['base_vehicles_ids_'] = base_vehicle_ids
                if vehicle_ids:
                    data['vehicles_ids_'] = vehicle_ids
                if year:
                    data['year_'] = year
                if make_name:
                    data['make_name_'] = make_name
                if model_name:
                    data['model_name_'] = model_name
                if submodel_name:
                    data['submodel_name_'] = submodel_name
                if part_numbers:
                    data['part_numbers_'] = part_numbers
                data = [data]
            return data
        except Exception:
            raise

    def retrieve_products_by_category_data_from_api(self, category_id,
                                                    base_vehicle_ids=None,
                                                    vehicle_ids=None,
                                                    year=None,
                                                    make_name=None,
                                                    model_name=None,
                                                    submodel_name=None,
                                                    part_numbers=None,
                                                    pies_segments=None,
                                                    annotated=False):
        """
        Retrieves dataset products by category data from SEMA API.

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

        :return: dataset products by category data
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
            data = sema_client.retrieve_products_by_category(
                category_id=category_id,
                dataset_ids=[self.dataset_id],
                base_vehicle_ids=base_vehicle_ids,
                vehicle_ids=vehicle_ids,
                year=year,
                make_name=make_name,
                model_name=model_name,
                submodel_name=submodel_name,
                pies_segments=pies_segments,
                part_numbers=part_numbers
            )
            if annotated:
                data = {
                    'brand_id_': self.brand.brand_id,
                    'dataset_id_': self.dataset_id,
                    'category_id_': category_id,
                    'products_': data
                }
                if base_vehicle_ids:
                    data['base_vehicles_ids_'] = base_vehicle_ids
                if vehicle_ids:
                    data['vehicles_ids_'] = vehicle_ids
                if year:
                    data['year_'] = year
                if make_name:
                    data['make_name_'] = make_name
                if model_name:
                    data['model_name_'] = model_name
                if submodel_name:
                    data['submodel_name_'] = submodel_name
                if part_numbers:
                    data['part_numbers_'] = part_numbers
                data = [data]
            return data
        except Exception:
            raise

    def retrieve_vehicles_by_product_data_from_api(self, part_numbers=None,
                                                   annotated=False):
        """
        Retrieves dataset vehicles by product data from SEMA API.

        :param part_numbers: part numbers on which to filter
        :type part_numbers: list
        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: dataset vehicles by product data
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
            data = sema_client.retrieve_vehicles_by_product(
                dataset_id=self.dataset_id,
                part_numbers=part_numbers
            )
            if annotated:
                data = {
                    'brand_id_': self.brand.brand_id,
                    'dataset_id_': self.dataset_id,
                    'products_': data
                }
                if part_numbers:
                    data['part_numbers_'] = part_numbers
                data = [data]
            return data
        except Exception:
            raise

    def retrieve_vehicles_by_brand_data_from_api(self, annotated=False):
        """
        Retrieves dataset vehicles by brand data from SEMA API.

        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: dataset vehicles by brand data
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
                    }
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
            data = sema_client.retrieve_vehicles_by_brand(
                dataset_ids=[self.dataset_id]
            )
            if annotated:
                data = {
                    'brand_id_': self.brand.brand_id,
                    'dataset_id': self.dataset_id,
                    'vehicles_': data
                }
                data = [data]
            return data
        except Exception:
            raise
    # </editor-fold>

    # <editor-fold desc="update properties ...">
    @property
    def state(self):
        """
        Returns a dictionary of fields and values relevant to updates.

        :return: current values of fields relevant to updates
        :rtype: dict

        """

        state = dict(super().state)
        state.update(
            {
                'Name': self.name,
                'Brand': str(self.brand)
            }
        )
        return state
    # </editor-fold>

    # <editor-fold desc="perform properties ...">
    def perform_dataset_categories_update_from_api(self, **filters):
        msgs = []
        try:
            data = SemaCategory.objects.get_api_data(
                datasets=self._meta.model.objects.filter(pk=self.pk),
                **filters
            )
        except Exception as err:
            msgs.append(self.get_instance_error_msg(str(err)))
            return msgs

        for category in data:
            try:
                if category['CategoryId'] in self.categories.values_list(
                        'category_id', flat=True):
                    msgs.append(
                        self.get_instance_up_to_date_msg(
                            message=f"{category['Name']} already added"
                        )
                    )
                else:
                    self.categories.add(category['CategoryId'])
                    self.save()
                    msgs.append(
                        self.get_update_success_msg(
                            message=f"{category['Name']} added"
                        )
                    )
            except Exception as err:
                msgs.append(self.get_instance_error_msg(str(err)))
                continue

        if not msgs:
            msgs.append(self.get_instance_up_to_date_msg())
        return msgs

    def perform_dataset_vehicles_update_from_api(self):
        msgs = []
        try:
            data = self.retrieve_vehicles_by_brand_data_from_api(
                annotated=False
            )
        except Exception as err:
            msgs.append(self.get_instance_error_msg(str(err)))
            return msgs

        for item in data:
            try:
                vehicle, _ = SemaVehicle.objects.get_or_create_by_names(
                    year=item['Year'],
                    make_name=item['MakeName'],
                    model_name=item['ModelName'],
                    submodel_name=item['SubmodelName']
                )
                if vehicle in self.vehicles.all():
                    msgs.append(
                        self.get_instance_up_to_date_msg(
                            message=f"{vehicle} already added"
                        )
                    )
                else:
                    self.vehicles.add(vehicle)
                    self.save()
                    msgs.append(
                        self.get_update_success_msg(
                            message=f"{vehicle} added"
                        )
                    )
            except Exception as err:
                msgs.append(self.get_instance_error_msg(str(err)))
                continue

        if not msgs:
            msgs.append(self.get_instance_up_to_date_msg())
        return msgs
    # </editor-fold>

    objects = SemaDatasetManager()

    class Meta:
        ordering = ['name']
        verbose_name = 'SEMA dataset'

    def __str__(self):
        return f'{self.brand} :: {self.name}'


class SemaProduct(SemaBaseModel):
    """
    This model class defines SEMA products.

    """

    product_id = PositiveIntegerField(
        primary_key=True,
        unique=True
    )
    part_number = CharField(
        max_length=30
    )
    dataset = ForeignKey(
        SemaDataset,
        on_delete=CASCADE,
        related_name='products',
    )
    html = TextField(
        blank=True,
        verbose_name='HTML'
    )
    categories = ManyToManyField(
        SemaCategory,
        blank=True,
        related_name='products'
    )
    vehicles = ManyToManyField(
        SemaVehicle,
        blank=True,
        related_name='products'
    )

    @property
    def clean_html(self):
        all_image_classes = [
            'main-product-img',
            'brand-logo'
        ]

        def remove_head(html_):
            prefix = '<html>\n' if '<html>' in html_ else ''
            if '<head>' in html_:
                html_ = f"{prefix}{html_.split('</head>', 1)[1]}"
            return html_

        def shrink_images(html_, image_classes_=None):
            if not image_classes_:
                image_classes_ = all_image_classes
            image_width = '100px'
            for image_class in image_classes_:
                if f'class="{image_class}"' in html_:
                    i = html_.index(f'class="{image_class}"')
                    html_ = f'{html_[:i]}width="{image_width}" {html_[i:]}'
            return html_

        def remove_images(html_, image_classes_=None):
            if not image_classes_:
                image_classes_ = all_image_classes
            soup = BeautifulSoup(html_)
            for image_class in image_classes_:
                for tag in soup.find_all('img', {'class': image_class}):
                    tag.decompose()
            html_ = str(soup)
            return html_

        if not self.html:
            return '<html></html>'
        return remove_head(remove_images(self.html))

    # <editor-fold desc="relevancy properties ...">
    @property
    def may_be_relevant(self):
        """
        Returns whether or not object may be relevant based on
        attributes and related attributes.

        .. Topic:: **-May Be Relevant Conditions-**

            1. dataset is relevant, and
            2. has relevant vehicles (inherits dataset vehicles if none)

        :return: whether or not object may be relevant
        :rtype: bool

        """

        if self.vehicle_count:
            relevant_vehicle_count = self.vehicle_relevant_count
        else:
            relevant_vehicle_count = self.dataset.vehicle_relevant_count
        return self.dataset.is_relevant and relevant_vehicle_count > 0

    @property
    def relevancy_errors(self):
        """
        Returns a concatenation of errors based on relevancy.

        :return: errors based on relevancy
        :rtype: str

        """

        msgs = []
        if self.is_relevant:
            if not self.dataset.is_relevant:
                error = "dataset not relevant"
                msgs.append(error)
            if not self.vehicle_count:
                if not self.dataset.vehicle_relevant_count:
                    error = "no relevant vehicles"
                    msgs.append(error)
            else:
                if not self.vehicle_relevant_count:
                    error = "no relevant vehicles"
                    msgs.append(error)
            if not self.html or self.html == '':
                error = "no html"
                msgs.append(error)
            if not self.category_relevant_count == 3:
                error = f"{self.category_relevant_count} categories"
                msgs.append(error)
            if not self.description_pies_attribute_count:
                error = "missing description PIES"
                msgs.append(error)
            if not self.digital_assets_pies_attribute_count:
                error = "missing digital assets PIES"
                msgs.append(error)
        return ', '.join(msgs)
    relevancy_errors.fget.short_description = 'Errors'
    # </editor-fold>

    # <editor-fold desc="count properties ...">
    @property
    def description_pies_attribute_count(self):
        """
        Returns description PIES attribute count.

        :return: description PIES attribute count
        :rtype: int

        """

        return self.description_pies_attributes.distinct().count()
    description_pies_attribute_count.fget.short_description = (
        'Description Count'
    )

    @property
    def digital_assets_pies_attribute_count(self):
        """
        Returns digital assets PIES attribute count.

        :return: digital assets PIES attribute count
        :rtype: int

        """

        return self.digital_assets_pies_attributes.distinct().count()
    digital_assets_pies_attribute_count.fget.short_description = (
        'Digital Asset Count'
    )

    @property
    def category_count(self):
        """
        Returns category count.

        :return: category count
        :rtype: int

        """

        return self.categories.distinct().count()

    @property
    def category_relevant_count(self):
        """
        Returns relevant category count.

        :return: relevant category count
        :rtype: int

        """

        return self.categories.filter(is_relevant=True).distinct().count()
    category_relevant_count.fget.short_description = 'Relevant Category Count'

    @property
    def vehicle_count(self):
        """
        Returns vehicle count.

        :return: vehicle count
        :rtype: int

        """

        return self.vehicles.distinct().count()

    @property
    def vehicle_relevant_count(self):
        """
        Returns relevant vehicle count.

        :return: relevant vehicle count
        :rtype: int

        """

        return self.vehicles.filter(is_relevant=True).distinct().count()
    vehicle_relevant_count.fget.short_description = 'Relevant Vehicle Count'
    # </editor-fold>

    # <editor-fold desc="retrieve properties ...">
    def retrieve_products_by_brand_data_from_api(self, base_vehicle_ids=None,
                                                 vehicle_ids=None, year=None,
                                                 make_name=None,
                                                 model_name=None,
                                                 submodel_name=None,
                                                 pies_segments=None,
                                                 annotated=False):
        """
        Retrieves product by brand data from SEMA API.

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
            return self.dataset.retrieve_products_by_brand_data_from_api(
                base_vehicle_ids=base_vehicle_ids,
                vehicle_ids=vehicle_ids,
                year=year,
                make_name=make_name,
                model_name=model_name,
                submodel_name=submodel_name,
                part_numbers=[self.part_number],
                pies_segments=pies_segments,
                annotated=annotated
            )
        except Exception:
            raise

    def retrieve_products_by_category_data_from_api(self, category_id,
                                                    base_vehicle_ids=None,
                                                    vehicle_ids=None,
                                                    year=None,
                                                    make_name=None,
                                                    model_name=None,
                                                    submodel_name=None,
                                                    pies_segments=None,
                                                    annotated=False):
        """
        Retrieves product by category data from SEMA API.

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

        :return: product by category data
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
            return self.dataset.retrieve_products_by_category_data_from_api(
                category_id=category_id,
                base_vehicle_ids=base_vehicle_ids,
                vehicle_ids=vehicle_ids,
                year=year,
                make_name=make_name,
                model_name=model_name,
                submodel_name=submodel_name,
                part_numbers=[self.part_number],
                pies_segments=pies_segments,
                annotated=annotated
            )
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
                        "brand_id_": <str>,
                        "dataset_id_": <int>,
                        "part_numbers_" <list>,
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
            return self.dataset.retrieve_vehicles_by_product_data_from_api(
                part_numbers=[self.part_number],
                annotated=annotated
            )
        except Exception:
            raise

    def retrieve_product_html_data_from_api(self, annotated=False):
        """
        Retrieves product HTML data from SEMA API object.

        :param annotated: whether or not to include filter annotation
        :type annotated: bool

        :return: product HTML
        :rtype: str or dict

        :raises: Exception on SEMA API object method exception

        **-Return Format-**
        ::
            if annotated:
                ret = {
                    "product_id_": <int>,
                    "html_": <str>
                }
            else:
                ret = <str>

        """

        try:
            data = sema_client.retrieve_product_html(
                product_id=self.product_id
            )
            if annotated:
                data = {
                    'product_id_': self.product_id,
                    'html_': data
                }
            return data
        except Exception:
            raise
    # </editor-fold>

    # <editor-fold desc="update properties ...">
    @property
    def state(self):
        """
        Returns a dictionary of fields and values relevant to updates.

        :return: current values of fields relevant to updates
        :rtype: dict

        """

        state = dict(super().state)
        state.update(
            {
                'Part': self.part_number,
                'Dataset': str(self.dataset)
            }
        )
        return state
    # </editor-fold>

    # <editor-fold desc="perform properties ...">
    def perform_product_vehicles_update_from_api(self):
        msgs = []
        try:
            data = self.retrieve_vehicles_by_product_data_from_api(
                annotated=False
            )
        except Exception as err:
            msgs.append(self.get_instance_error_msg(str(err)))
            return msgs

        for item in data:
            if self.part_number == item['PartNumber']:
                for vehicle_item in item['Vehicles']:
                    try:
                        vehicle, _ = SemaVehicle.objects.get_or_create_by_names(
                            year=vehicle_item['Year'],
                            make_name=vehicle_item['MakeName'],
                            model_name=vehicle_item['ModelName'],
                            submodel_name=vehicle_item['SubmodelName']
                        )
                        if vehicle in self.vehicles.all():
                            msgs.append(
                                self.get_instance_up_to_date_msg(
                                    message=f"{vehicle} already added"
                                )
                            )
                        else:
                            self.vehicles.add(vehicle)
                            self.save()
                            msgs.append(
                                self.get_update_success_msg(
                                    message=f"{vehicle} added"
                                )
                            )
                    except Exception as err:
                        msgs.append(self.get_instance_error_msg(str(err)))
                        continue
            else:
                msgs.append(
                    self.get_instance_error_msg(
                        error="Incorrect product returned"
                    )
                )
                continue

        if not msgs:
            msgs.append(self.get_instance_up_to_date_msg())
        return msgs

    def perform_pies_attribute_update_from_api(self, pies_attr_model,
                                               new_only=False, **filters):
        """
        Retrieves product PIES attribute data from SEMA API, and creates
        and/or updates PIES attribute objects.

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
                products=self._meta.model.objects.filter(pk=self.pk),
                new_only=new_only,
                **filters
            )
        except Exception as err:
            msgs.append(self.get_instance_error_msg(str(err)))

        if not msgs:
            msgs.append(self.get_instance_up_to_date_msg())
        return msgs

    def perform_product_html_update_from_api(self):
        """
        Retrieves product HTML data from SEMA API, and updates HTML
        field.

        :return: update or error message
        :rtype: str

        """

        try:
            html = self.retrieve_product_html_data_from_api(annotated=False)
            self.html = html
            self.save()
            self.refresh_from_db()
            return self.get_update_success_msg()
        except Exception as err:
            return self.get_instance_error_msg(str(err))
    # </editor-fold>

    objects = SemaProductManager()

    class Meta:
        ordering = ['dataset', 'part_number']
        unique_together = ['dataset', 'part_number']
        verbose_name = 'SEMA product'

    def __str__(self):
        return f'{self.product_id} :: {self.dataset}'


class SemaBasePiesAttributeModel(Model, MessagesMixin):
    """
    This abstract model class defines base attributes for SEMA PIES
    attribute models.

    """

    product = ForeignKey(
        SemaProduct,
        on_delete=CASCADE,
        related_name='pies_attributes'
    )
    segment = CharField(
        max_length=100
    )
    value = CharField(
        max_length=500
    )

    # <editor-fold desc="update properties ...">
    @property
    def state(self):
        """
        Returns a dictionary of fields and values relevant to updates.

        :return: current values of fields relevant to updates
        :rtype: dict

        """

        return {
            'Value': self.value
        }

    def update_from_api_data(self, **update_fields):
        """
        Marks object as authorized and updates any necessary fields.

        :param update_fields: field/value kwargs to be updated.
        :type update_fields: dict

        :return: info, success or error message
        :rtype: str

        """

        try:
            prev = self.state
            for attr, value in update_fields.items():
                if isinstance(
                        self._meta.model._meta.get_field(attr),
                        ManyToManyField):
                    getattr(self, attr).add(value)
                    self.save()
                elif not getattr(self, attr) == value:
                    setattr(self, attr, value)
                    self.save()
            self.refresh_from_db()
            new = self.state
            msg = self.get_update_success_msg(previous_data=prev, new_data=new)
        except Exception as err:
            msg = self.get_instance_error_msg(f"{update_fields}, {err}")
        return msg
    # </editor-fold>

    objects = SemaBasePiesAttributeManager()

    class Meta:
        unique_together = ['product', 'segment']
        abstract = True

    def __str__(self):
        return f"{self.product} :: {self.segment}"


class SemaDescriptionPiesAttribute(SemaBasePiesAttributeModel):
    """
    This model class defines SEMA product PIES description attributes.

    """

    product = ForeignKey(
        SemaProduct,
        on_delete=CASCADE,
        related_name='description_pies_attributes'
    )
    value = CharField(
        max_length=500
    )

    objects = SemaDescriptionPiesAttributeManager()

    class Meta:
        verbose_name = 'SEMA description PIES'
        verbose_name_plural = 'SEMA description PIES'


class SemaDigitalAssetsPiesAttribute(SemaBasePiesAttributeModel):
    """
    This model class defines SEMA product PIES digital asset attributes.

    """

    product = ForeignKey(
        SemaProduct,
        on_delete=CASCADE,
        related_name='digital_assets_pies_attributes'
    )
    value = URLField(
        max_length=500
    )

    objects = SemaDigitalAssetsPiesAttributeManager()

    class Meta:
        verbose_name = 'SEMA digital assets PIES'
        verbose_name_plural = 'SEMA digital assets PIES'
