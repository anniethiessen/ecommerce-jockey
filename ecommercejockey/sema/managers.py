from collections import defaultdict

from django.db.models import (
    Manager,
    QuerySet,
    F,
    Q,
    ManyToManyField
)
from django.db.models.functions import Floor

from .apis import sema_api


class SemaBaseQuerySet(QuerySet):
    def unauthorize(self):
        msgs = []
        for obj in self:
            msgs.append(obj.unauthorize())
        return msgs


class SemaBrandQuerySet(SemaBaseQuerySet):
    def import_datasets_from_api(self):
        msgs = []
        for obj in self:
            msgs += obj.import_datasets_from_api()
        return msgs

    def perform_product_vehicle_update(self, dataset_id=None,
                                       part_numbers=None):
        """
        Retrieves **vehicles by product** data for brand queryset by
        brand queryset method, brand object method and SEMA API object
        method, and retrieves and updates product objects' vehicles by
        product manager method and products object methods, and returns
        a list of messages.

        :type dataset_id: int
        :type part_numbers: list
        :rtype: list

        """

        from .models import SemaProduct

        msgs = []
        try:
            data = self.get_vehicles_by_product_data_from_api(
                dataset_id=dataset_id,
                part_numbers=part_numbers
            )
            msgs += SemaProduct.objects.update_product_vehicles_from_api_data(data)
        except Exception as err:
            msgs.append(self.model.get_class_error_msg(str(err)))

        if not msgs:
            msgs.append(self.model.get_class_up_to_date_msg())
        return msgs

    def get_vehicles_by_product_data_from_api(self, dataset_id=None,
                                              part_numbers=None):
        """
        Retrieves and concatenates **vehicles by product** data for
        brand queryset by brand object method, and SEMA API object
        method.

        :type dataset_id: int
        :type part_numbers: list
        :rtype: list

        :raises: Exception on brand object method exception

        .. Topic:: Return Format

            [
                {
                    "PartNumber": str,
                    "Vehicles": [
                        {
                            "Year": int,
                            "MakeName": str,
                            "ModelName": str,
                            "SubmodelName": str
                        },
                        {...}
                    ],
                    "brand_id_": str
                },
                {...}
            ]

        """

        try:
            data = []
            for brand in self:
                data += brand.get_vehicles_by_product_data_from_api(
                    dataset_id=dataset_id,
                    part_numbers=part_numbers
                )
            return data
        except Exception:
            raise


class SemaDatasetQuerySet(SemaBaseQuerySet):
    def perform_product_vehicle_update(self, part_numbers=None):
        """
        Retrieves **vehicles by product** data for dataset queryset by
        dataset queryset method, dataset object method, brand object
        method and SEMA API object method, and retrieves and updates
        product objects' vehicles by product manager method and products
        object methods, and returns a list of messages.

        :type part_numbers: list
        :rtype: list

        """

        from .models import SemaProduct

        msgs = []
        try:
            data = self.get_vehicles_by_product_data_from_api(
                part_numbers=part_numbers
            )
            msgs += SemaProduct.objects.update_product_vehicles_from_api_data(data)
        except Exception as err:
            msgs.append(self.model.get_class_error_msg(str(err)))

        if not msgs:
            msgs.append(self.model.get_class_up_to_date_msg())
        return msgs

    def get_vehicles_by_product_data_from_api(self, part_numbers=None):
        """
        Retrieves and concatenates **vehicles by product** data for
        dataset queryset by dataset object method, brand object method,
        and SEMA API object method.

        :type part_numbers: list
        :rtype: list

        :raises: Exception on dataset object method exception

        .. Topic:: Return Format

            [
                {
                    "PartNumber": str,
                    "Vehicles": [
                        {
                            "Year": int,
                            "MakeName": str,
                            "ModelName": str,
                            "SubmodelName": str
                        },
                        {...}
                    ],
                    "brand_id_": str,
                    "dataset_id_": int,
                },
                {...}
            ]

        """

        try:
            data = []
            for dataset in self:
                data += dataset.get_vehicles_by_product_data_from_api(
                    part_numbers=part_numbers
                )
            return data
        except Exception:
            raise


class SemaYearQuerySet(SemaBaseQuerySet):
    def with_year_data(self):
        return self.annotate(
            decade=Floor(F('year') / 10) * 10
        )


class SemaMakeQuerySet(SemaBaseQuerySet):
    pass


class SemaModelQuerySet(SemaBaseQuerySet):
    pass


class SemaSubmodelQuerySet(SemaBaseQuerySet):
    pass


class SemaMakeYearQuerySet(SemaBaseQuerySet):
    pass


class SemaBaseVehicleQuerySet(SemaBaseQuerySet):
    pass


class SemaVehicleQuerySet(SemaBaseQuerySet):
    pass

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
                base_vehicle__model__model_ide=model_id,
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


class SemaCategoryQuerySet(SemaBaseQuerySet):
    def perform_product_category_update(self, brand_ids=None, dataset_ids=None,
                                        base_vehicle_ids=None,
                                        vehicle_ids=None, part_numbers=None,
                                        year=None, make_name=None,
                                        model_name=None, submodel_name=None,
                                        pies_segments=None):
        """
        Retrieves **products by category** data for category queryset by
        category queryset method, category object method and SEMA API
        object method and retrieves and updates product objects'
        categories by product manager and product object method, and
        returns a list of messages.

        :type brand_ids: list
        :type dataset_ids: list
        :type base_vehicle_ids: list
        :type vehicle_ids: list
        :type part_numbers: list
        :type year: int
        :type make_name: str
        :type model_name: str
        :type submodel_name: str
        :type pies_segments: list
        :rtype: list

        """

        from .models import SemaProduct

        msgs = []
        try:
            data = self.get_products_by_category_data_from_api(
                brand_ids=brand_ids,
                dataset_ids=dataset_ids,
                base_vehicle_ids=base_vehicle_ids,
                vehicle_ids=vehicle_ids,
                part_numbers=part_numbers,
                year=year,
                make_name=make_name,
                model_name=model_name,
                submodel_name=submodel_name,
                pies_segments=pies_segments
            )
            msgs += SemaProduct.objects.update_product_categories_from_api_data(
                data
            )
        except Exception as err:
            msgs.append(self.model.get_class_error_msg(str(err)))
            return msgs

        if not msgs:
            msgs.append(self.model.get_class_up_to_date_msg())
        return msgs

    def get_products_by_category_data_from_api(self, brand_ids=None,
                                               dataset_ids=None,
                                               base_vehicle_ids=None,
                                               vehicle_ids=None,
                                               part_numbers=None,
                                               year=None,
                                               make_name=None,
                                               model_name=None,
                                               submodel_name=None,
                                               pies_segments=None):
        """
        Retrieves and concatenates **products by category** data for
        category queryset by category object method, and SEMA API object
        method.

        :type brand_ids: list
        :type dataset_ids: list
        :type base_vehicle_ids: list
        :type vehicle_ids: list
        :type part_numbers: list
        :type year: int
        :type make_name: str
        :type model_name: str
        :type submodel_name: str
        :type pies_segments: list
        :rtype: list

        :raises: Exception on category object method exception

        .. warnings also:: Filtering by year, make, model, or submodel
        requires all four

        .. Topic:: Return Format

            [
                {
                    "ProductId": int,
                    "PartNumber": str,
                    "PiesAttributes": [],
                    "category_id_" int
                },
                {...}
            ]

        """

        try:
            data = []
            for category in self:
                data += category.get_products_by_category_data_from_api(
                    brand_ids=brand_ids,
                    dataset_ids=dataset_ids,
                    base_vehicle_ids=base_vehicle_ids,
                    vehicle_ids=vehicle_ids,
                    part_numbers=part_numbers,
                    year=year,
                    make_name=make_name,
                    model_name=model_name,
                    submodel_name=submodel_name,
                    pies_segments=pies_segments
                )
            return data
        except Exception:
            raise


class SemaProductQuerySet(SemaBaseQuerySet):
    def perform_product_html_update(self):
        msgs = []

        for obj in self:
            try:
                msgs.append(obj.perform_product_html_update())
            except Exception as err:
                msgs.append(obj.get_instance_error_msg(str(err)))

        return msgs

    def perform_product_vehicle_update(self):
        """
        Retrieves **vehicles by product** data for product queryset by
        product queryset method, dataset queryset method, dataset object
        method, brand object method and SEMA API object method, and
        retrieves and updates product objects' vehicles by product
        manager method and products object method, and returns a list
        of messages.

        :rtype: list

        """

        msgs = []
        try:
            data = self.get_vehicles_by_product_data_from_api()
            msgs += self.model.objects.update_product_vehicles_from_api_data(data)
        except Exception as err:
            msgs.append(self.model.get_class_error_msg(str(err)))

        if not msgs:
            msgs.append(self.model.get_class_up_to_date_msg())
        return msgs

    def get_vehicles_by_product_data_from_api(self):
        """
        Retrieves and concatenates **vehicles by product** data for
        product queryset by dataset object method, brand object method,
        and SEMA API object method.

        :rtype: list

        :raises: Exception on dataset object method exception

        .. Topic:: Return Format

            [
                {
                    "PartNumber": str,
                    "Vehicles": [
                        {
                            "Year": int,
                            "MakeName": str,
                            "ModelName": str,
                            "SubmodelName": str
                        },
                        {...}
                    ],
                    "brand_id_": str,
                    "dataset_id_": int,
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
                data += dataset.get_vehicles_by_product_data_from_api(
                    part_numbers=part_numbers
                )
            return data
        except Exception:
            raise


class SemaBaseManager(Manager):
    def import_and_unauthorize_from_api(self):
        msgs = []

        try:
            data = self.get_api_data()
            msgs += self.create_or_update_from_api_data(data, new_only=False)
            msgs += self.unauthorize_from_api_data(data)
        except Exception as err:
            msgs.append(self.model.get_class_error_msg(str(err)))
            return msgs

        if not msgs:
            msgs.append(self.model.get_class_up_to_date_msg())
        return msgs

    def import_from_api(self, new_only=False, **filters):
        msgs = []

        try:
            errors = self.get_api_filter_errors(**filters)
            if errors:
                msgs.append(self.model.get_class_error_msg(errors))
                return msgs
        except Exception as err:
            msgs.append(self.model.get_class_error_msg(str(err)))
            return msgs

        try:
            data = self.get_api_data(**filters)
            msgs += self.create_or_update_from_api_data(data, new_only=new_only)
        except Exception as err:
            msgs.append(self.model.get_class_error_msg(str(err)))
            return msgs

        if not msgs:
            msgs.append(self.model.get_class_up_to_date_msg())
        return msgs

    def unauthorize_from_api(self):
        msgs = []

        try:
            data = self.get_api_data()
            msgs += self.unauthorize_from_api_data(data)
        except Exception as err:
            msgs.append(self.model.get_class_error_msg(str(err)))
            return msgs

        return msgs

    def get_api_filter_errors(self, **filters):
        return []

    def get_api_data(self, **filters):
        raise Exception('Get API data must be defined')

    def parse_api_data(self, data):
        raise Exception('Parse API data must be defined')

    def create_or_update_from_api_data(self, data, new_only=False):
        msgs = []
        for item in data:
            try:
                pk, update_fields = self.parse_api_data(item)
            except Exception as err:
                msgs.append(self.model.get_class_error_msg(f"{item}: {err}"))
                continue

            try:
                obj = self.get_object_from_api_data(pk, **update_fields)
                if not new_only:
                    msgs.append(obj.update_from_api_data(**update_fields))
            except self.model.DoesNotExist:
                msgs.append(self.create_from_api_data(pk, **update_fields))
            except Exception as err:
                msgs.append(self.model.get_class_error_msg(f"{item}: {err}"))
        return msgs

    def get_object_from_api_data(self, pk, **update_fields):
        try:
            return self.get(pk=pk)
        except Exception:
            raise

    def create_from_api_data(self, pk, **update_fields):
        try:
            m2m_fields = {}
            create_fields = {}
            for attr, value in update_fields.items():
                if isinstance(
                        self.model._meta.get_field(attr), ManyToManyField):
                    m2m_fields[attr] = value
                else:
                    create_fields[attr] = value
            obj = self.create(
                pk=pk,
                is_authorized=True,
                **create_fields
            )
            for attr, value in m2m_fields.items():
                getattr(obj, attr).add(value)
                obj.save()
            msg = obj.get_create_success_msg()
        except Exception as err:
            msg = self.model.get_class_error_msg(f"{pk}, {update_fields}, {err}")
        return msg

    def unauthorize_from_api_data(self, data):
        msgs = []

        try:
            authorized_pks = self.get_pk_list_from_api_data(data)
            unauthorized = self.model.objects.filter(~Q(pk__in=authorized_pks))
            msgs += unauthorized.unauthorize()
        except Exception as err:
            msgs.append(self.model.get_class_error_msg(str(err)))
            return msgs

        return msgs

    def get_pk_list_from_api_data(self, data):
        raise Exception('Get PK list must be defined')

    def flatten_api_data(self, data):
        flattened_data = []

        try:
            for item in data:
                subcategories = item.pop('Categories', [])
                flattened_data.append(item)
                if subcategories:
                    flattened_data += self.flatten_api_data(subcategories)
            return flattened_data
        except Exception:
            raise

    def remove_duplicates_from_api_data(self, data):
        try:
            return [dict(t) for t in {tuple(i.items()) for i in data}]
        except Exception:
            raise

    def get_queryset(self):
        return SemaBaseQuerySet(
            self.model,
            using=self._db
        )


class SemaBrandManager(SemaBaseManager):
    def get_api_data(self):
        try:
            data = sema_api.retrieve_brand_datasets()
            for item in data:
                del item['DatasetId']
                del item['DatasetName']
            return data
        except Exception:
            raise

    def parse_api_data(self, data):
        pk = data['AAIABrandId']
        update_fields = {
            'name': data['BrandName']
        }
        return pk, update_fields

    def get_pk_list_from_api_data(self, data):
        try:
            return [item['AAIABrandId'] for item in data]
        except Exception:
            raise

    def get_queryset(self):
        return SemaBrandQuerySet(
            self.model,
            using=self._db
        )

    def import_datasets_from_api(self):
        return self.get_queryset().import_datasets_from_api()

    def perform_product_vehicle_update(self, dataset_id=None,
                                       part_numbers=None):
        """
        Retrieves brand queryset and **vehicles by product** data for
        brand queryset by brand queryset method, brand object method,
        and SEMA API object method and retrieves and updates product
        objects' vehicles by product manager and products object methods
        and returns a list of messages.

        :type dataset_id: int
        :type part_numbers: list
        :rtype: list

        """

        msgs = []
        try:
            msgs += self.get_queryset().perform_product_vehicle_update(
                dataset_id=dataset_id,
                part_numbers=part_numbers
            )
        except Exception as err:
            msgs.append(self.model.get_class_error_msg(str(err)))

        if not msgs:
            msgs.append(self.model.get_class_up_to_date_msg())
        return msgs

    def get_vehicles_by_product_data_from_api(self, dataset_id=None,
                                              part_numbers=None):
        """
        Retrieves brand queryset and returns **vehicles by product**
        data for queryset by brand queryset method, brand object method,
        and SEMA API object method.

        :type dataset_id: int
        :type part_numbers: list
        :rtype: list

        :raises: Exception on brand queryset method exception

        .. Topic:: Return Format

            [
                {
                    "PartNumber": str,
                    "Vehicles": [
                        {
                            "Year": int,
                            "MakeName": str,
                            "ModelName": str,
                            "SubmodelName": str
                        },
                        {...}
                    ],
                    "brand_id_": str
                },
                {...}
            ]

        """

        try:
            return self.get_queryset().get_vehicles_by_product_data_from_api(
                dataset_id=dataset_id,
                part_numbers=part_numbers
            )
        except Exception:
            raise


class SemaDatasetManager(SemaBaseManager):
    def get_api_data(self, brand_ids=None):
        try:
            data = sema_api.retrieve_brand_datasets()
            if brand_ids:
                data = [
                    item for item in data
                    if item['AAIABrandId'] in brand_ids
                ]
            return data
        except Exception:
            raise

    def parse_api_data(self, data):
        from .models import SemaBrand

        pk = data['DatasetId']
        update_fields = {
            'name': data['DatasetName'],
            'brand': SemaBrand.objects.get(brand_id=data['AAIABrandId'])
        }
        return pk, update_fields

    def get_pk_list_from_api_data(self, data):
        try:
            return [item['DatasetId'] for item in data]
        except Exception:
            raise

    def get_queryset(self):
        return SemaDatasetQuerySet(
            self.model,
            using=self._db
        )

    def perform_product_vehicle_update(self, part_numbers=None):
        """
        Retrieves dataset queryset and **vehicles by product** data for
        dataset queryset by dataset queryset method, dataset object
        method, brand object method, and SEMA API object method and
        retrieves and updates product objects' vehicles by product
        manager and products object methods and returns a list of
        messages.

        :type part_numbers: list
        :rtype: list

        """

        msgs = []
        try:
            msgs += self.get_queryset().perform_product_vehicle_update(
                part_numbers=part_numbers
            )
        except Exception as err:
            msgs.append(self.model.get_class_error_msg(str(err)))

        if not msgs:
            msgs.append(self.model.get_class_up_to_date_msg())
        return msgs

    def get_vehicles_by_product_data_from_api(self, part_numbers=None):
        """
        Retrieves dataset queryset and returns **vehicles by product**
        data for queryset by dataset queryset method, dataset object
        method, brand object method, and SEMA API object method.

        :type part_numbers: list
        :rtype: list

        :raises: Exception on dataset queryset method exception

        .. Topic:: Return Format

            [
                {
                    "PartNumber": str,
                    "Vehicles": [
                        {
                            "Year": int,
                            "MakeName": str,
                            "ModelName": str,
                            "SubmodelName": str
                        },
                        {...}
                    ],
                    "brand_id_": str,
                    "dataset_id_: int
                },
                {...}
            ]

        """

        try:
            return self.get_queryset().get_vehicles_by_product_data_from_api(
                part_numbers=part_numbers
            )
        except Exception:
            raise


class SemaYearManager(SemaBaseManager):
    def get_api_data(self, brand_ids=None, dataset_ids=None):
        try:
            return sema_api.retrieve_years(
                brand_ids=brand_ids,
                dataset_ids=dataset_ids
            )
        except Exception:
            raise

    def parse_api_data(self, data):
        pk = data
        update_fields = {}
        return pk, update_fields

    def get_pk_list_from_api_data(self, data):
        return data

    def get_queryset(self):
        return SemaYearQuerySet(
            self.model,
            using=self._db
        )

    def with_year_data(self):
        return self.get_queryset().with_year_data()


class SemaMakeManager(SemaBaseManager):
    def get_api_data(self, brand_ids=None, dataset_ids=None, year=None):
        try:
            return sema_api.retrieve_makes(
                brand_ids=brand_ids,
                dataset_ids=dataset_ids,
                year=year
            )
        except Exception:
            raise

    def parse_api_data(self, data):
        try:
            pk = data['MakeID']
            update_fields = {
                'name': data['MakeName']
            }
            return pk, update_fields
        except Exception:
            raise

    def get_pk_list_from_api_data(self, data):
        try:
            return [item['MakeID'] for item in data]
        except Exception:
            raise

    def get_queryset(self):
        return SemaMakeQuerySet(
            self.model,
            using=self._db
        )


class SemaModelManager(SemaBaseManager):
    def get_api_data(self, brand_ids=None, dataset_ids=None,
                     year=None, make_id=None):
        try:
            data = sema_api.retrieve_models(
                brand_ids=brand_ids,
                dataset_ids=dataset_ids,
                year=year,
                make_id=make_id
            )
            for item in data:
                del item['BaseVehicleID']
            return [dict(t) for t in {tuple(item.items()) for item in data}]
        except Exception:
            raise

    def parse_api_data(self, data):
        try:
            pk = data['ModelID']
            update_fields = {
                'name': data['ModelName']
            }
            return pk, update_fields
        except Exception:
            raise

    def get_pk_list_from_api_data(self, data):
        try:
            return [item['ModelID'] for item in data]
        except Exception:
            raise

    def get_queryset(self):
        return SemaModelQuerySet(
            self.model,
            using=self._db
        )


class SemaSubmodelManager(SemaBaseManager):
    def get_api_data(self, brand_ids=None, dataset_ids=None,
                     year=None, make_id=None, model_id=None):
        try:
            data = sema_api.retrieve_submodels(
                brand_ids=brand_ids,
                dataset_ids=dataset_ids,
                year=year,
                make_id=make_id,
                model_id=model_id
            )
            for item in data:
                del item['VehicleID']
            return [dict(t) for t in {tuple(item.items()) for item in data}]
        except Exception:
            raise

    def parse_api_data(self, data):
        try:
            pk = data['SubmodelID']
            update_fields = {
                'name': data['SubmodelName']
            }
            return pk, update_fields
        except Exception:
            raise

    def get_pk_list_from_api_data(self, data):
        try:
            return [item['SubmodelID'] for item in data]
        except Exception:
            raise

    def get_queryset(self):
        return SemaSubmodelQuerySet(
            self.model,
            using=self._db
        )


class SemaMakeYearManager(SemaBaseManager):
    def get_api_data(self, brand_ids=None, dataset_ids=None, year=None):
        from .models import SemaYear
        years = SemaYear.objects.filter(is_authorized=True)
        if year:
            years = years.filter(year=year)
        if not years:
            raise Exception('No authorized years')

        all_data = []
        try:
            for year in years:
                data = sema_api.retrieve_makes(
                    brand_ids=brand_ids,
                    dataset_ids=dataset_ids,
                    year=year.year
                )
                for item in data:
                    item['year_'] = year.year
                all_data += data
            return self.remove_duplicates_from_api_data(all_data)
        except Exception:
            raise

    def parse_api_data(self, data):
        from .models import SemaYear, SemaMake

        try:
            pk = None
            update_fields = {
                'year': SemaYear.objects.get(year=data['year_']),
                'make': SemaMake.objects.get(make_id=data['MakeID']),
            }
            return pk, update_fields
        except Exception:
            raise

    def get_object_from_api_data(self, pk, **update_fields):
        try:
            return self.get(
                year=update_fields['year'],
                make=update_fields['make']
            )
        except Exception:
            raise

    def get_pk_list_from_api_data(self, data):
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

    def get_queryset(self):
        return SemaMakeYearQuerySet(
            self.model,
            using=self._db
        )


class SemaBaseVehicleManager(SemaBaseManager):
    def get_api_data(self, brand_ids=None, dataset_ids=None,
                     year=None, make_id=None):
        from .models import SemaMakeYear
        make_years = SemaMakeYear.objects.filter(is_authorized=True)
        if year:
            make_years = make_years.filter(year__year=year)
        if make_id:
            make_years = make_years.filter(make__make_id=make_id)
        if not make_years:
            raise Exception('No authorized make years')

        all_data = []
        try:
            for make_year in make_years:
                data = sema_api.retrieve_models(
                    brand_ids=brand_ids,
                    dataset_ids=dataset_ids,
                    year=make_year.year.year,
                    make_id=make_year.make.make_id
                )
                for item in data:
                    item['year_'] = make_year.year.year
                    item['make_id_'] = make_year.make.make_id
                all_data += data
            return self.remove_duplicates_from_api_data(all_data)
        except Exception:
            raise

    def parse_api_data(self, data):
        from .models import SemaMakeYear, SemaModel
        try:
            pk = data['BaseVehicleID']
            update_fields = {
                'make_year': SemaMakeYear.objects.get(
                    year__year=data['year_'],
                    make__make_id=data['make_id_']
                ),
                'model': SemaModel.objects.get(model_id=data['ModelID'])
            }
            return pk, update_fields
        except Exception:
            raise

    def get_pk_list_from_api_data(self, data):
        try:
            return [item['BaseVehicleID'] for item in data]
        except Exception:
            raise

    def get_queryset(self):
        return SemaBaseVehicleQuerySet(
            self.model,
            using=self._db
        )


class SemaVehicleManager(SemaBaseManager):
    def get_api_data(self, brand_ids=None, dataset_ids=None,
                     year=None, make_id=None, model_id=None):
        from .models import SemaBaseVehicle

        base_vehicles = SemaBaseVehicle.objects.filter(is_authorized=True)
        if year:
            base_vehicles = base_vehicles.filter(make_year__year__year=year)
        if make_id:
            base_vehicles = base_vehicles.filter(
                make_year__make__make_id=make_id
            )
        if model_id:
            base_vehicles = base_vehicles.filter(model__model_id=model_id)
        if not base_vehicles:
            raise Exception('No authorized base vehicles')

        all_data = []
        try:
            for base_vehicle in base_vehicles:
                data = sema_api.retrieve_submodels(
                    brand_ids=brand_ids,
                    dataset_ids=dataset_ids,
                    year=base_vehicle.make_year.year.year,
                    make_id=base_vehicle.make_year.make.make_id,
                    model_id=base_vehicle.model.model_id
                )
                for item in data:
                    item['year_'] = base_vehicle.make_year.year.year
                    item['make_id_'] = base_vehicle.make_year.make.make_id
                    item['model_id_'] = base_vehicle.model.model_id
                all_data += data
            return self.remove_duplicates_from_api_data(all_data)
        except Exception:
            raise

    def parse_api_data(self, data):
        from .models import SemaBaseVehicle, SemaSubmodel
        try:
            pk = data['VehicleID']
            update_fields = {
                'base_vehicle': SemaBaseVehicle.objects.get(
                    make_year__year__year=data['year_'],
                    make_year__make__make_id=data['make_id_'],
                    model__model_id=data['model_id_']
                ),
                'submodel': SemaSubmodel.objects.get(
                    submodel_id=data['SubmodelID']
                )
            }
            return pk, update_fields
        except Exception:
            raise

    def get_pk_list_from_api_data(self, data):
        try:
            return [item['VehicleID'] for item in data]
        except Exception:
            raise

    def get_queryset(self):
        return SemaVehicleQuerySet(
            self.model,
            using=self._db
        )

    def get_by_ids(self, year, make_id, model_id, submodel_id):
        """
        Returns vehicle queryset and returns queryset object by year,
        make id, model id, and submodel id.

        :type year: int
        :type make_id: int
        :type model_id: int
        :type submodel_id: int
        :rtype: object

        :raises: Exception on queryset method exception

        """

        try:
            return self.get_queryset().get_by_ids(
                year=year,
                make_id=make_id,
                model_id=model_id,
                submodel_id=submodel_id
            )
        except Exception:
            raise

    def get_by_names(self, year, make_name, model_name, submodel_name):
        """
        Retrieves vehicle queryset and returns vehicle object by year,
        make name, model name, and submodel name by vehicle queryset
        method.

        :type year: int
        :type make_name: str
        :type model_name: str
        :type submodel_name: str
        :rtype: object

        :raises: Exception on queryset method exception

        """

        try:
            return self.get_queryset().get_by_names(
                year=year,
                make_name=make_name,
                model_name=model_name,
                submodel_name=submodel_name
            )
        except Exception:
            raise


class SemaCategoryManager(SemaBaseManager):
    def get_api_data(self, brand_ids=None, dataset_ids=None,
                     year=None, make_name=None,
                     model_name=None, submodel_name=None,
                     base_vehicle_ids=None, vehicle_ids=None):
        from .models import SemaBrand, SemaDataset

        brands = SemaBrand.objects.filter(is_authorized=True)
        datasets = SemaDataset.objects.filter(is_authorized=True)

        if brand_ids:
            brands = brands.filter(brand_id__in=brand_ids)
        if dataset_ids:
            datasets = datasets.filter(dataset_id__in=dataset_ids)
        if not (brands or datasets):
            raise Exception('No authorized brands or datasets')

        try:
            data = sema_api.retrieve_categories(
                brand_ids=list(brands.values_list('brand_id', flat=True)),
                dataset_ids=list(datasets.values_list('dataset_id', flat=True)),
                year=year,
                make_name=make_name,
                model_name=model_name,
                submodel_name=submodel_name,
                base_vehicle_ids=base_vehicle_ids,
                vehicle_ids=vehicle_ids
            )
            data = self.flatten_api_data(data)
            return self.remove_duplicates_from_api_data(data)
        except Exception:
            raise

    def parse_api_data(self, data):
        try:
            pk = data['CategoryId']
            update_fields = {
                'name': data['Name']
            }
            if data.get('ParentId'):
                update_fields['parent_categories'] = (
                    self.get(category_id=data['ParentId'])
                )
            return pk, update_fields
        except Exception:
            raise

    def get_pk_list_from_api_data(self, data):
        try:
            return [item['CategoryId'] for item in data]
        except Exception:
            raise

    def get_queryset(self):
        return SemaCategoryQuerySet(
            self.model,
            using=self._db
        )

    def perform_product_category_update(self, brand_ids=None, dataset_ids=None,
                                        base_vehicle_ids=None,
                                        vehicle_ids=None, part_numbers=None,
                                        year=None, make_name=None,
                                        model_name=None, submodel_name=None,
                                        pies_segments=None):
        """
        Retrieves category queryset and **products by category** data
        for queryset by category queryset method, category object method
        and SEMA API object method and retrieves and updates product
        objects' categories by product manager and product object method,
        and returns a list of messages.

        :type brand_ids: list
        :type dataset_ids: list
        :type base_vehicle_ids: list
        :type vehicle_ids: list
        :type part_numbers: list
        :type year: int
        :type make_name: str
        :type model_name: str
        :type submodel_name: str
        :type pies_segments: list
        :rtype: list

        """

        msgs = []
        try:
            msgs += self.get_queryset().perform_product_category_update(
                brand_ids=brand_ids,
                dataset_ids=dataset_ids,
                base_vehicle_ids=base_vehicle_ids,
                vehicle_ids=vehicle_ids,
                part_numbers=part_numbers,
                year=year,
                make_name=make_name,
                model_name=model_name,
                submodel_name=submodel_name,
                pies_segments=pies_segments
            )
        except Exception as err:
            msgs.append(self.model.get_class_error_msg(str(err)))
            return msgs

        if not msgs:
            msgs.append(self.model.get_class_up_to_date_msg())
        return msgs

    def get_products_by_category_data_from_api(self, brand_ids=None,
                                               dataset_ids=None,
                                               base_vehicle_ids=None,
                                               vehicle_ids=None,
                                               part_numbers=None,
                                               year=None, make_name=None,
                                               model_name=None,
                                               submodel_name=None,
                                               pies_segments=None):
        """
        Retrieves category queryset and returns **products by category**
        data for queryset by category queryset method, category object
        method, and SEMA API object method.

        :type brand_ids: list
        :type dataset_ids: list
        :type base_vehicle_ids: list
        :type vehicle_ids: list
        :type part_numbers: list
        :type year: int
        :type make_name: str
        :type model_name: str
        :type submodel_name: str
        :type pies_segments: list
        :rtype: list

        :raises: Exception on category queryset method exception

        .. warnings also:: Filtering by year, make, model, or submodel
        requires all four

        .. Topic:: Return Format

            [
                {
                    "ProductId": int,
                    "PartNumber": str,
                    "PiesAttributes": [],
                    "category_id_" int
                },
                {...}
            ]

        """

        try:
            return self.get_queryset().get_products_by_category_data_from_api(
                brand_ids=brand_ids,
                dataset_ids=dataset_ids,
                base_vehicle_ids=base_vehicle_ids,
                vehicle_ids=vehicle_ids,
                part_numbers=part_numbers,
                year=year,
                make_name=make_name,
                model_name=model_name,
                submodel_name=submodel_name,
                pies_segments=pies_segments
            )
        except Exception:
            raise


class SemaProductManager(SemaBaseManager):
    def get_api_data(self, brand_ids=None, dataset_ids=None,
                     year=None, make_name=None,
                     model_name=None, submodel_name=None,
                     base_vehicle_ids=None, vehicle_ids=None,
                     part_numbers=None, pies_segments=('C10_DES', 'C10_EXT')):
        from .models import SemaDataset

        datasets = SemaDataset.objects.filter(is_authorized=True)
        if brand_ids:
            datasets = datasets.filter(brand__brand_id__in=brand_ids)
        if dataset_ids:
            datasets = datasets.filter(dataset_id__in=dataset_ids)
        if not datasets:
            raise Exception('No authorized datasets')

        if pies_segments:
            pies_segments = list(pies_segments)

        all_data = []
        try:
            for dataset in datasets:
                data = sema_api.retrieve_products_by_brand(
                    brand_ids=[dataset.brand.brand_id],
                    dataset_ids=[dataset.dataset_id],
                    year=year,
                    make_name=make_name,
                    model_name=model_name,
                    submodel_name=submodel_name,
                    base_vehicle_ids=base_vehicle_ids,
                    vehicle_ids=vehicle_ids,
                    part_numbers=part_numbers,
                    pies_segments=pies_segments
                )
                for item in data:
                    item['dataset_id_'] = dataset.dataset_id
                all_data += data
            return all_data
        except Exception:
            raise

    def parse_api_data(self, data):
        from .models import SemaDataset
        try:
            pk = data['ProductId']
            update_fields = {
                'part_number': data['PartNumber'],
                'dataset': SemaDataset.objects.get(
                    dataset_id=data['dataset_id_']
                )
            }
            pies_attributes = data.pop('PiesAttributes', [])
            if pies_attributes:
                for attribute in pies_attributes:
                    if attribute['PiesSegment'] == 'C10_DES_EN':
                        update_fields['pies_c10_des'] = attribute['Value']
                    elif attribute['PiesSegment'] == 'C10_EXT_EN':
                        update_fields['pies_c10_ext'] = attribute['Value']
            return pk, update_fields
        except Exception:
            raise

    def get_pk_list_from_api_data(self, data):
        try:
            return [item['ProductId'] for item in data]
        except Exception:
            raise

    def get_queryset(self):
        return SemaProductQuerySet(
            self.model,
            using=self._db
        )

    def perform_product_html_update(self):
        return self.get_queryset().perform_product_html_update()

    def perform_product_vehicle_update(self):
        """
        Retrieves product queryset and **vehicles by product** data for
        product queryset by product queryset method, dataset queryset
        method, dataset object method, brand object method, and SEMA API
        object method and retrieves and updates product objects'
        vehicles by product manager and products object methods and
        returns a list of messages.

        :rtype: list

        """

        msgs = []
        try:
            msgs += self.get_queryset().perform_product_vehicle_update()
        except Exception as err:
            msgs.append(self.model.get_class_error_msg(str(err)))

        if not msgs:
            msgs.append(self.model.get_class_up_to_date_msg())
        return msgs

    def perform_product_category_update(self, brand_ids=None, dataset_ids=None,
                                        base_vehicle_ids=None,
                                        vehicle_ids=None, part_numbers=None,
                                        year=None, make_name=None,
                                        model_name=None, submodel_name=None,
                                        pies_segments=None):
        """
        Retrieves **products by category** data for available categories
        by category queryset method, category object method and SEMA API
        object method and retrieves and updates product objects'
        categories by product manager and product object method, and
        returns a list of messages.

        :type brand_ids: list
        :type dataset_ids: list
        :type base_vehicle_ids: list
        :type vehicle_ids: list
        :type part_numbers: list
        :type year: int
        :type make_name: str
        :type model_name: str
        :type submodel_name: str
        :type pies_segments: list
        :rtype: list

        """
        from .models import SemaCategory

        msgs = []
        try:
            categories = SemaCategory.objects.filter(is_authorized=True)
            data = categories.get_products_by_category_data_from_api(
                brand_ids=brand_ids,
                dataset_ids=dataset_ids,
                base_vehicle_ids=base_vehicle_ids,
                vehicle_ids=vehicle_ids,
                part_numbers=part_numbers,
                year=year,
                make_name=make_name,
                model_name=model_name,
                submodel_name=submodel_name,
                pies_segments=pies_segments
            )
            msgs += self.update_product_categories_from_api_data(
                data
            )
        except Exception as err:
            msgs.append(self.model.get_class_error_msg(str(err)))
            return msgs

        if not msgs:
            msgs.append(self.model.get_class_up_to_date_msg())
        return msgs

    def get_vehicles_by_product_data_from_api(self):
        """
        Retrieves product queryset and returns **vehicles by product**
        data for queryset by product queryset method, dataset object
        method, brand object method, and SEMA API object method.

        :rtype: list

        :raises: Exception on dataset queryset method exception

        .. Topic:: Return Format

            [
                {
                    "PartNumber": str,
                    "Vehicles": [
                        {
                            "Year": int,
                            "MakeName": str,
                            "ModelName": str,
                            "SubmodelName": str
                        },
                        {...}
                    ],
                    "brand_id_": str,
                    "dataset_id_: int
                },
                {...}
            ]

        """

        try:
            return self.get_queryset().get_vehicles_by_product_data_from_api()
        except Exception:
            raise

    def update_product_vehicles_from_api_data(self, data):
        """
        Retrieves product object by data part number, updates
        product vehicles by product object method, and returns a list
        of messages.

        :rtype: list

        .. warnings also:: Does not remove vehicles not in data

        .. Topic:: Expected Data Format

            [
                {
                    "PartNumber": str,
                    "Vehicles": [
                        {
                            "Year": int,
                            "MakeName": str,
                            "ModelName": str,
                            "SubmodelName": str
                        },
                        {...}
                    ],
                    "brand_id_": str
                },
                {...}
            ]

        """

        msgs = []
        try:
            for item in data:
                try:
                    product = self.get(
                        part_number=item['PartNumber'],
                        dataset__brand__brand_id=item['brand_id_']
                    )
                    msgs += product.update_product_vehicles_from_api_data(
                        item['Vehicles']
                    )
                except Exception as err:
                    msgs.append(self.model.get_class_error_msg(f'{item, err}'))
                    continue
        except Exception as err:
            msgs.append(self.model.get_class_error_msg(str(err)))
        return msgs

    def update_product_categories_from_api_data(self, data):
        """
        Retrieves product object by data product id, updates
        product vehicles by product object method, and returns a list
        of messages.

        :rtype: list

        .. warnings also:: Does not remove categories not in data

        .. Topic:: Expected Data Format

            [
                {
                    "ProductId": int,
                    "PartNumber": str,
                    "PiesAttributes": [],
                    "category_id_" int
                },
                {...}
            ]

        """

        msgs = []
        products_categories = defaultdict(list)
        for item in data:
            try:
                products_categories[item['ProductId']].append(
                    item['category_id_']
                )
            except Exception as err:
                msgs.append(self.model.get_class_error_msg(str(err)))
                return msgs

        for product_id, categories in products_categories.items():
            try:
                product = self.get(product_id=product_id)
                msgs += product.update_product_categories_from_api_data(
                    categories
                )
            except Exception as err:
                msgs.append(self.model.get_class_error_msg(
                    f"{product_id}, {err}")
                )
                continue
        return msgs
