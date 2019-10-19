from django.db.models import Manager, QuerySet, F, Q
from django.db.models.functions import Floor

from .apis import PremierApi, SemaApi
from .utils import chunkify_list


premier_api = PremierApi()
sema_api = SemaApi()


class PremierProductQuerySet(QuerySet):
    def has_missing_inventory(self):
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

    def has_all_inventory(self):
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

    def has_missing_pricing(self):
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

    def has_all_pricing(self):
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

    def update_inventory_from_api(self):
        msgs = []

        invalid = self.filter(premier_part_number__isnull=True)
        for obj in invalid:
            msgs.append(
                obj.get_instance_error_msg("Premier Part Number required")
            )

        queryset = self.filter(premier_part_number__isnull=False)
        part_numbers = [obj.premier_part_number for obj in queryset]

        chunks = chunkify_list(part_numbers, chunk_size=50)
        for chunk in chunks:
            try:
                response = self.model.objects.get_api_inventory_data(chunk)
                for items in response:
                    obj = queryset.get(premier_part_number=items['itemNumber'])
                    data = items['inventory']
                    update_fields = obj.parse_api_inventory_data(data)
                    msgs.append(
                        obj.update_inventory_from_api_data(**update_fields)
                    )
            except Exception as err:
                msgs.append(f'Chunk Error: {chunk}, {err}')
                continue
        return msgs

    def update_pricing_from_api(self):
        msgs = []

        invalid = self.filter(premier_part_number__isnull=True)
        for obj in invalid:
            msgs.append(
                obj.get_instance_error_msg("Premier Part Number required")
            )

        queryset = self.filter(premier_part_number__isnull=False)
        part_numbers = [obj.premier_part_number for obj in queryset]

        chunks = chunkify_list(part_numbers, chunk_size=50)
        for chunk in chunks:
            try:
                response = self.model.objects.get_api_inventory_data(chunk)
                for items in response:
                    obj = queryset.get(premier_part_number=items['itemNumber'])
                    data = items['pricing']
                    update_fields = obj.parse_api_pricing_data(data)
                    msgs.append(
                        obj.update_pricing_from_api_data(**update_fields)
                    )
            except Exception as err:
                msgs.append(f'Chunk Error: {chunk}, {err}')
                continue
        return msgs


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


class SemaDatasetQuerySet(SemaBaseQuerySet):
    pass


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


class SemaCategoryQuerySet(SemaBaseQuerySet):
    pass


class SemaProductQuerySet(SemaBaseQuerySet):
    def update_html_from_api(self):
        msgs = []

        for obj in self:
            try:
                msgs.append(obj.update_html_from_api())
            except Exception as err:
                msgs.append(obj.get_instance_error_msg(str(err)))

        return msgs


class PremierProductManager(Manager):
    @staticmethod
    def get_api_inventory_data(part_numbers):
        try:
            return premier_api.retrieve_product_inventory(part_numbers)
        except Exception:
            raise

    @staticmethod
    def get_api_pricing_data(part_numbers):
        try:
            return premier_api.retrieve_product_pricing(part_numbers)
        except Exception:
            raise

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

    def get_queryset(self):
        return PremierProductQuerySet(
            self.model,
            using=self._db
        )

    def has_all_inventory(self):
        return self.get_queryset().has_all_inventory()

    def has_missing_inventory(self):
        return self.get_queryset().has_missing_inventory()

    def has_all_pricing(self):
        return self.get_queryset().has_all_pricing()

    def has_missing_pricing(self):
        return self.get_queryset().has_missing_pricing()

    def update_inventory_from_api(self):
        return self.get_queryset().update_inventory_from_api()

    def update_pricing_from_api(self):
        return self.get_queryset().update_pricing_from_api()


class SemaBaseManager(Manager):
    def import_and_unauthorize_from_api(self):
        msgs = []

        try:
            data = self.get_api_data()
            msgs += self.create_or_update_from_api_data(data)
            msgs += self.unauthorize_from_api_data(data)
        except Exception as err:
            msgs.append(self.model.get_class_error_msg(str(err)))
            return msgs

        if not msgs:
            msgs.append(self.model.get_class_up_to_date_msg())
        return msgs

    def import_from_api(self, **filters):
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
        except Exception as err:
            msgs.append(self.model.get_class_error_msg(str(err)))
            return msgs

        try:
            msgs += self.create_or_update_from_api_data(data)
        except Exception as err:
            msgs.append(self.model.get_class_error_msg(str(err)))

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

    def create_or_update_from_api_data(self, data):
        msgs = []
        for item in data:
            try:
                pk, update_fields = self.parse_api_data(item)
            except Exception as err:
                msgs.append(self.model.get_class_error_msg(f"{item}: {err}"))
                continue

            try:
                obj = self.get_object_from_api_data(pk, **update_fields)
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
            obj = self.create(
                pk=pk,
                is_authorized=True,
                **update_fields
            )
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
        from product.models import SemaBrand

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
        from product.models import SemaYear
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
        from product.models import SemaYear, SemaMake

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
        from product.models import SemaMakeYear
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
        from product.models import SemaMakeYear, SemaModel
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
        from product.models import SemaBaseVehicle

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
        from product.models import SemaBaseVehicle, SemaSubmodel
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


class SemaCategoryManager(SemaBaseManager):
    def get_api_data(self, brand_ids=None, dataset_ids=None,
                     year=None, make_name=None,
                     model_name=None, submodel_name=None,
                     base_vehicle_ids=None, vehicle_ids=None):
        from product.models import SemaBrand, SemaDataset

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
                update_fields['parent_category'] = (
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


class SemaProductManager(SemaBaseManager):
    def get_api_data(self, brand_ids=None, dataset_ids=None,
                     year=None, make_name=None,
                     model_name=None, submodel_name=None,
                     base_vehicle_ids=None, vehicle_ids=None,
                     part_numbers=None, pies_segments=None):
        from product.models import SemaDataset

        datasets = SemaDataset.objects.filter(is_authorized=True)
        if brand_ids:
            datasets = datasets.filter(brand__brand_id__in=brand_ids)
        if dataset_ids:
            datasets = datasets.filter(dataset_id__in=dataset_ids)
        if not datasets:
            raise Exception('No authorized datasets')

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
        from product.models import SemaDataset

        try:
            pk = data['ProductId']
            update_fields = {
                'part_number': data['PartNumber'],
                'dataset': SemaDataset.objects.get(
                    dataset_id=data['dataset_id_']
                )
            }
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

    def update_html_from_api(self):
        return self.get_queryset().update_html_from_api()
