import json

import requests

from django.conf import settings


class MessagesMixin(object):
    @classmethod
    def get_class_up_to_date_msg(cls):
        return (
            "Info: "
            f"{cls._meta.verbose_name.title()}, "
            "everything up-to-date"
        )

    def get_instance_up_to_date_msg(self):
        return (
            "Info: "
            f"{self._meta.model._meta.verbose_name.title()} {self}, "
            "already up-to-date"
        )

    @classmethod
    def get_class_error_msg(cls, error):
        return f"Error: {cls._meta.verbose_name.title()}, {error}"

    def get_instance_error_msg(self, error):
        return (
            "Error: "
            f"{self._meta.model._meta.verbose_name.title()} {self}, {error}"
        )

    def get_create_success_msg(self):
        return (
            "Success: "
            f"{self._meta.model._meta.verbose_name.title()} {self} created"
        )

    def get_update_success_msg(self, previous_data=None, new_data=None):
        msg = (
            "Success: "
            f"{self._meta.model._meta.verbose_name.title()} {self} updated"
        )
        if previous_data and new_data:
            changes = ""
            for key, value in new_data.items():
                if not value == previous_data[key]:
                    changes += f", {key}: {previous_data[key]} -> {value}"

            if changes:
                msg += changes
            else:
                msg = self.get_instance_up_to_date_msg()
        return msg


class ProductMixin(MessagesMixin):
    @classmethod
    def link_products(cls):
        from product.models import PremierProduct, SemaProduct, Manufacturer

        msgs = []
        premier_products = PremierProduct.objects.filter(product__isnull=True)
        sema_products = SemaProduct.objects.filter(product__isnull=True)

        # for premier_product in premier_products:
        #     try:
        #         manufacturer = Manufacturer.objects.get(
        #             premier_manufacturer=premier_product.manufacturer)
        #         sema_product = sema_products.get(
        #             dataset__brand__name=manufacturer.sema_brand,
        #             part_number=premier_product.vendor_part_number,
        #         )
        #         product = cls.objects.get_or_create(
        #             premier_product=premier_product,
        #             sema_product=sema_product
        #         )
        #         msgs.append(product.get_create_success_msg())
        #     except Manufacturer.DoesNotExist:
        #         msgs.append(premier_product.get_instance_error_msg(
        #             "Premier manufacturer does not exist"))
        #     except SemaProduct.DoesNotExist:
        #         msgs.append(premier_product.get_instance_error_msg(
        #             "SEMA product does not exist"))
        #     except Exception as err:
        #         msgs.append(premier_product.get_instance_error_msg(str(err)))

        for sema_product in sema_products:
            try:
                manufacturer = Manufacturer.objects.get(
                    sema_brand=sema_product.dataset.brand.name)
                matching_products = premier_products.filter(
                    manufacturer=manufacturer.premier_manufacturer,
                    vendor_part_number=sema_product.part_number
                )
                for premier_product in matching_products:
                    product = cls.objects.create(
                        premier_product=premier_product,
                        sema_product=sema_product
                    )
                    msgs.append(product.get_create_success_msg())
            except Manufacturer.DoesNotExist:
                msgs.append(sema_product.get_instance_error_msg(
                    "SEMA brand does not exist"))
            except PremierProduct.DoesNotExist:
                msgs.append(sema_product.get_instance_error_msg(
                    "Premier product does not exist"))
            except Exception as err:
                msgs.append(sema_product.get_instance_error_msg(str(err)))

        return msgs


class ManufacturerMixin(MessagesMixin):
    @classmethod
    def check_unlinked_manufacturers(cls):
        from product.models import PremierProduct, SemaBrand

        msgs = []
        premier_manufacturers = list(PremierProduct.objects.values_list(
            'manufacturer', flat=True).distinct())
        sema_brands = SemaBrand.objects.all()

        for premier_manufacturer in premier_manufacturers:
            try:
                cls.objects.get(premier_manufacturer=premier_manufacturer)
            except cls.DoesNotExist:
                msgs.append(cls.get_class_error_msg(
                    f"Premier Manufacturer {premier_manufacturer} "
                    "Missing linked brand")
                )
            except Exception as err:
                msgs.append(cls.get_class_error_msg(str(err)))

        for sema_brand in sema_brands:
            try:
                cls.objects.get(sema_brand=sema_brand.name)
            except cls.DoesNotExist:
                msgs.append(sema_brand.get_instance_error_msg(
                    "Missing linked brand")
                )
            except Exception as err:
                msgs.append(cls.get_class_error_msg(str(err)))
        return msgs


# <editor-fold desc="Premier">
class PremierApiCoreMixin(MessagesMixin):
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
            response.raise_for_status()
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
            response.raise_for_status()
            if response.status_code == requests.codes.ok:
                return json.loads(response.text)
            else:
                raise Exception('Bad request')
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
            response.raise_for_status()
            if response.status_code == requests.codes.ok:
                return json.loads(response.text)
            else:
                raise Exception('Bad request')
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
            return self.get_instance_error_msg("Premier Part Number required")

        try:
            if not token:
                token = self.retrieve_premier_api_token()
            response = self.retrieve_premier_api_inventory(
                [self.premier_part_number], token)
            data = response[0]['inventory']
            return self.update_inventory_from_data(data)
        except Exception as err:
            return self.get_instance_error_msg(str(err))

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
            return self.get_instance_error_msg(str(err))

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
            return self.get_instance_error_msg("Premier Part Number required")

        try:
            if not token:
                token = self.retrieve_premier_api_token()
            response = self.retrieve_premier_api_pricing(
                [self.premier_part_number], token)
            data = response[0]['pricing']
            return self.update_pricing_from_data(data)
        except Exception as err:
            return self.get_instance_error_msg(str(err))

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
            return self.get_instance_error_msg(str(err))

        self.refresh_from_db()
        new = self.get_pricing_data()
        return self.get_update_success_msg(previous, new)
    # </editor-fold>
# </editor-fold>


# <editor-fold desc="SEMA">
class SemaApiCoreMixin(MessagesMixin):
    @classmethod
    def retrieve_sema_api_token(cls):
        try:
            url = f'{settings.SEMA_BASE_URL}/token/get'
            params = {
                'userName': settings.SEMA_USERNAME,
                'password': settings.SEMA_PASSWORD
            }
            response = requests.get(url=url, params=params)
            response.raise_for_status()
            response = json.loads(response.text)
            if response.get('success', False):
                return response['token']
            else:
                raise Exception(response.get('message', 'Bad request'))
        except Exception:
            raise

    @classmethod
    def retrieve_sema_api_content_token(cls, token=None):
        try:
            if not token:
                token = cls.retrieve_sema_api_token()

            url = f'{settings.SEMA_BASE_URL}/token/getcontenttoken'
            params = {'token': token}
            response = requests.get(url=url, params=params)
            response.raise_for_status()
            response = json.loads(response.text)
            if response.get('success', False):
                return response['contenttoken']
            else:
                raise Exception(response.get('message', 'Bad request'))
        except Exception:
            raise


class SemaApiYearMixin(SemaApiCoreMixin):
    @classmethod
    def retrieve_sema_years(cls, dataset_id=None, token=None):
        try:
            if not token:
                token = cls.retrieve_sema_api_token()

            url = f'{settings.SEMA_BASE_URL}/lookup/years'
            params = {
                'token': token,
                'branddatasetids': dataset_id
            }
            response = requests.get(url=url, params=params)
            response.raise_for_status()
            response = json.loads(response.text)
            if response.get('success', False):
                return response['Years']
            else:
                raise Exception(response.get('message', 'Bad request'))
        except Exception:
            raise


class SemaApiMakeMixin(SemaApiCoreMixin):
    @classmethod
    def retrieve_sema_makes(cls, dataset_id=None, year=None, token=None):
        try:
            if not token:
                token = cls.retrieve_sema_api_token()

            url = f'{settings.SEMA_BASE_URL}/lookup/makes'
            params = {
                'token': token,
                'branddatasetids': dataset_id,
                'year': year
            }
            response = requests.get(url=url, params=params)
            response.raise_for_status()
            response = json.loads(response.text)
            if response.get('success', False):
                return response['Makes']
            else:
                raise Exception(response.get('message', 'Bad request'))
        except Exception:
            raise


class SemaApiModelMixin(SemaApiCoreMixin):
    @classmethod
    def retrieve_sema_models(cls, dataset_id=None, year=None,
                             make_id=None, token=None):
        try:
            if not token:
                token = cls.retrieve_sema_api_token()

            url = f'{settings.SEMA_BASE_URL}/lookup/models'
            params = {
                'token': token,
                'branddatasetids': dataset_id,
                'year': year,
                'makeid': make_id
            }
            response = requests.get(url=url, params=params)
            response.raise_for_status()
            response = json.loads(response.text)
            if response.get('success', False):
                return response['Models']
            else:
                raise Exception(response.get('message', 'Bad request'))
        except Exception:
            raise


class SemaApiSubmodelMixin(SemaApiCoreMixin):
    @classmethod
    def retrieve_sema_submodels(cls, dataset_id=None, year=None,
                                make_id=None, model_id=None, token=None):
        try:
            if not token:
                token = cls.retrieve_sema_api_token()

            url = f'{settings.SEMA_BASE_URL}/lookup/submodels'
            params = {
                'token': token,
                'branddatasetids': dataset_id,
                'year': year,
                'makeid': make_id,
                'modelid': model_id
            }
            response = requests.get(url=url, params=params)
            response.raise_for_status()
            response = json.loads(response.text)
            if response.get('success', False):
                return response['Submodels']
            else:
                raise Exception(response.get('message', 'Bad request'))
        except Exception:
            raise


class SemaApiBaseVehicleMixin(SemaApiCoreMixin):
    @classmethod
    def retrieve_sema_base_vehicles(cls, dataset_id=None, year=None,
                                    make_id=None, token=None):
        try:
            if not token:
                token = cls.retrieve_sema_api_token()

            url = f'{settings.SEMA_BASE_URL}/lookup/models'
            params = {
                'token': token,
                'branddatasetids': dataset_id,
                'year': year,
                'makeid': make_id
            }
            response = requests.get(url=url, params=params)
            response.raise_for_status()
            response = json.loads(response.text)
            if response.get('success', False):
                return response['Models']
            else:
                raise Exception(response.get('message', 'Bad request'))
        except Exception:
            raise


class SemaApiVehicleMixin(SemaApiCoreMixin):
    @classmethod
    def retrieve_sema_vehicles(cls, dataset_id=None, year=None,
                               make_id=None, model_id=None, token=None):
        try:
            if not token:
                token = cls.retrieve_sema_api_token()

            url = f'{settings.SEMA_BASE_URL}/lookup/submodels'
            params = {
                'token': token,
                'branddatasetids': dataset_id,
                'year': year,
                'makeid': make_id,
                'modelid': model_id
            }
            response = requests.get(url=url, params=params)
            response.raise_for_status()
            response = json.loads(response.text)
            if response.get('success', False):
                return response['Submodels']
            else:
                raise Exception(response.get('message', 'Bad request'))
        except Exception:
            raise


class SemaApiBrandMixin(SemaApiCoreMixin):
    @classmethod
    def retrieve_sema_brands(cls, token=None):
        try:
            if not token:
                token = cls.retrieve_sema_api_token()

            url = f'{settings.SEMA_BASE_URL}/export/branddatasets'
            params = {'token': token}
            response = requests.get(url=url, params=params)
            response.raise_for_status()
            response = json.loads(response.text)
            if response.get('success', False):
                return response['BrandDatasets']
            else:
                raise Exception(response.get('message', 'Bad request'))
        except Exception:
            raise


class SemaApiDatasetMixin(SemaApiCoreMixin):
    @classmethod
    def retrieve_sema_datasets(cls, token=None):
        try:
            if not token:
                token = cls.retrieve_sema_api_token()

            url = f'{settings.SEMA_BASE_URL}/export/branddatasets'
            params = {'token': token}
            response = requests.get(url=url, params=params)
            response.raise_for_status()
            response = json.loads(response.text)
            if response.get('success', False):
                return response['BrandDatasets']
            else:
                raise Exception(response.get('message', 'Bad request'))
        except Exception:
            raise

    @classmethod
    def retrieve_sema_products(cls, dataset_id, token=None):
        try:
            if not token:
                token = cls.retrieve_sema_api_token()

            url = f'{settings.SEMA_BASE_URL}/lookup/products'
            data = {
                'token': token,
                'branddatasetid': dataset_id
            }
            response = requests.post(url=url, json=data)
            response.raise_for_status()
            response = json.loads(response.text)
            if response.get('success', False):
                return response['Products']
            else:
                raise Exception(response.get('message', 'Bad request'))
        except Exception:
            raise


class SemaApiCategoryMixin(SemaApiCoreMixin):
    @classmethod
    def retrieve_sema_categories(cls, dataset_id, token=None):
        try:
            if not token:
                token = cls.retrieve_sema_api_token()

            url = f'{settings.SEMA_BASE_URL}/lookup/categories'
            data = {
                'token': token,
                'branddatasetid': dataset_id
            }
            response = requests.post(url=url, json=data)
            response.raise_for_status()
            response = json.loads(response.text)
            if response.get('success', False):
                return response['Categories']
            else:
                raise Exception(response.get('message', 'Bad request'))
        except Exception:
            raise


class SemaApiProductMixin(SemaApiCoreMixin):
    @classmethod
    def retrieve_sema_product_html(cls, product_id, token=None):
        include_sema_header_footer = False
        try:
            if not token:
                token = cls.retrieve_sema_api_token()
            content_token = cls.retrieve_sema_api_content_token(token)
            url = f'{settings.SEMA_BASE_URL}/content/product'
            url += f'?contenttoken={content_token}'
            params = {
                'productid': product_id,
                'stripHeaderFooter': str(~include_sema_header_footer).lower()
            }
            response = requests.get(url=url, params=params)
            return str(response.text).strip()
        except Exception:
            raise


class SemaYearMixin(SemaApiYearMixin):
    @classmethod
    def import_years_from_sema_api(cls, dataset_id=None, token=None):
        try:
            if not token:
                token = cls.retrieve_sema_api_token()
            data = cls.retrieve_sema_years(dataset_id, token)
            return cls.create_years_from_data(data)
        except Exception as err:
            return cls.get_class_error_msg(str(err))

    @classmethod
    def create_years_from_data(cls, data):
        msgs = []
        for item in data:
            try:
                year, created = cls.objects.get_or_create(year=item)
                if created:
                    msgs.append(year.get_create_success_msg())
            except Exception as err:
                msgs.append(cls.get_class_error_msg(str(err)))
        if not msgs:
            msgs.append(cls.get_class_up_to_date_msg())
        return msgs


class SemaMakeMixin(SemaApiMakeMixin):
    @classmethod
    def import_makes_from_sema_api(cls, dataset_id=None,
                                   year=None, token=None):
        try:
            if not token:
                token = cls.retrieve_sema_api_token()
            data = cls.retrieve_sema_makes(dataset_id, year, token)
            return cls.create_makes_from_data(data)
        except Exception as err:
            return cls.get_class_error_msg(str(err))

    @classmethod
    def create_makes_from_data(cls, data):
        msgs = []
        for item in data:
            try:
                make, created = cls.objects.get_or_create(
                    make_id=item['MakeID'],
                    name=item['MakeName']
                )
                if created:
                    msgs.append(make.get_create_success_msg())
            except Exception as err:
                msgs.append(cls.get_class_error_msg(str(err)))
        if not msgs:
            msgs.append(cls.get_class_up_to_date_msg())
        return msgs


class SemaModelMixin(SemaApiModelMixin):
    def get_model_data(self):
        return {
            'Name': self.name,
        }

    @classmethod
    def import_models_from_sema_api(cls, token=None):
        try:
            if not token:
                token = cls.retrieve_sema_api_token()
            data = cls.retrieve_sema_models(token=token)
            for item in data:
                del item['BaseVehicleID']
            data = [dict(t) for t in {tuple(item.items()) for item in data}]
            return cls.create_models_from_data(data)
        except Exception as err:
            return cls.get_class_error_msg(str(err))

    @classmethod
    def create_models_from_data(cls, data):
        msgs = []
        for item in data:
            try:
                model = cls.objects.get(model_id=item['ModelID'])
                previous = model.get_model_data()
                model.name = item['ModelName']
                model.save()
                model.refresh_from_db()
                new = model.get_model_data()
                msgs.append(model.get_update_success_msg(previous, new))
            except cls.DoesNotExist:
                model = cls.objects.create(
                    model_id=item['ModelID'],
                    name=item['ModelName']
                )
                msgs.append(model.get_create_success_msg())
            except Exception as err:
                msgs.append(cls.get_class_error_msg(str(err)))
        if not msgs:
            msgs.append(cls.get_class_up_to_date_msg())
        return msgs


class SemaSubmodelMixin(SemaApiSubmodelMixin):
    def get_submodel_data(self):
        return {
            'Name': self.name,
        }

    @classmethod
    def import_submodels_from_sema_api(cls, token=None):
        try:
            if not token:
                token = cls.retrieve_sema_api_token()
            data = cls.retrieve_sema_submodels(token=token)
            for item in data:
                del item['VehicleID']
            data = [dict(t) for t in {tuple(item.items()) for item in data}]
            return cls.create_submodels_from_data(data)
        except Exception as err:
            return cls.get_class_error_msg(str(err))

    @classmethod
    def create_submodels_from_data(cls, data):
        msgs = []
        for item in data:
            try:
                submodel = cls.objects.get(submodel_id=item['SubmodelID'])
                previous = submodel.get_submodel_data()
                submodel.name = item['SubmodelName']
                submodel.save()
                submodel.refresh_from_db()
                new = submodel.get_submodel_data()
                msgs.append(submodel.get_update_success_msg(previous, new))
            except cls.DoesNotExist:
                submodel = cls.objects.create(
                    submodel_id=item['SubmodelID'],
                    name=item['SubmodelName']
                )
                msgs.append(submodel.get_create_success_msg())
            except Exception as err:
                msgs.append(cls.get_class_error_msg(str(err)))
        if not msgs:
            msgs.append(cls.get_class_up_to_date_msg())
        return msgs


class SemaBaseVehicleMixin(SemaApiBaseVehicleMixin):
    @staticmethod
    def get_year(year):
        from product.models import SemaYear

        try:
            return SemaYear.objects.get(year=year)
        except Exception:
            raise

    @staticmethod
    def get_make(make_id):
        from product.models import SemaMake

        try:
            return SemaMake.objects.get(make_id=make_id)
        except Exception:
            raise

    @staticmethod
    def get_model(model_id):
        from product.models import SemaModel

        try:
            return SemaModel.objects.get(model_id=model_id)
        except Exception:
            raise

    def get_base_vehicle_data(self):
        return {
            'Year': str(self.year),
            'Make': str(self.make),
            'Model': str(self.model)
        }

    @classmethod
    def import_base_vehicles_from_sema_api(cls, year, make_id, token=None):
        try:
            if not token:
                token = cls.retrieve_sema_api_token()
            data = cls.retrieve_sema_base_vehicles(
                year=year,
                make_id=make_id,
                token=token
            )
            return cls.create_base_vehicles_from_data(year, make_id, data)
        except Exception as err:
            return [cls.get_class_error_msg(str(err))]

    @classmethod
    def create_base_vehicles_from_data(cls, year, make_id, data):
        msgs = []
        for item in data:
            try:
                base_vehicle = cls.objects.get(
                    base_vehicle_id=item['BaseVehicleID']
                )
                previous = base_vehicle.get_base_vehicle_data()
                base_vehicle.year = cls.get_year(year)
                base_vehicle.make = cls.get_make(make_id)
                base_vehicle.model = cls.get_model(item['ModelID'])
                base_vehicle.save()
                base_vehicle.refresh_from_db()
                new = base_vehicle.get_base_vehicle_data()
                msgs.append(base_vehicle.get_update_success_msg(previous, new))
            except cls.DoesNotExist:
                base_vehicle = cls.objects.create(
                    base_vehicle_id=item['BaseVehicleID'],
                    year=cls.get_year(year),
                    make=cls.get_make(make_id),
                    model=cls.get_model(item['ModelID'])
                )
                msgs.append(base_vehicle.get_create_success_msg())
            except Exception as err:
                msgs.append(cls.get_class_error_msg(str(err)))
        if not msgs:
            msgs.append(cls.get_class_up_to_date_msg())
        return msgs


class SemaVehicleMixin(SemaApiVehicleMixin):
    @staticmethod
    def get_base_vehicle(base_vehicle_id):
        from product.models import SemaBaseVehicle

        try:
            return SemaBaseVehicle.objects.get(base_vehicle_id=base_vehicle_id)
        except Exception:
            raise

    @staticmethod
    def get_submodel(submodel_id):
        from product.models import SemaSubmodel

        try:
            return SemaSubmodel.objects.get(submodel_id=submodel_id)
        except Exception:
            raise

    def get_vehicle_data(self):
        return {
            'Base Vehicle': str(self.base_vehicle),
            'Submodel': str(self.submodel)
        }

    @classmethod
    def import_vehicles_from_sema_api(cls, base_vehicle_id, year, make_id,
                                      model_id, token=None):
        try:
            if not token:
                token = cls.retrieve_sema_api_token()
            data = cls.retrieve_sema_vehicles(
                year=year,
                make_id=make_id,
                model_id=model_id,
                token=token
            )
            return cls.create_vehicles_from_data(base_vehicle_id, data)
        except Exception as err:
            return [cls.get_class_error_msg(str(err))]

    @classmethod
    def create_vehicles_from_data(cls, base_vehicle_id, data):
        msgs = []
        for item in data:
            try:
                vehicle = cls.objects.get(vehicle_id=item['VehicleID'])
                previous = vehicle.get_vehicle_data()
                vehicle.base_vehicle = cls.get_base_vehicle(base_vehicle_id)
                vehicle.submodel = cls.get_submodel(item['SubmodelID'])
                vehicle.save()
                vehicle.refresh_from_db()
                new = vehicle.get_vehicle_data()
                msgs.append(vehicle.get_update_success_msg(previous, new))
            except cls.DoesNotExist:
                vehicle = cls.objects.create(
                    vehicle_id=item['VehicleID'],
                    base_vehicle=cls.get_base_vehicle(base_vehicle_id),
                    submodel=cls.get_submodel(item['SubmodelID'])
                )
                msgs.append(vehicle.get_create_success_msg())
            except Exception as err:
                msgs.append(cls.get_class_error_msg(str(err)))
        if not msgs:
            msgs.append(cls.get_class_up_to_date_msg())
        return msgs


class SemaBrandMixin(SemaApiBrandMixin):
    def get_brand_data(self):
        return {
            'Name': self.name
        }

    @classmethod
    def import_brands_from_sema_api(cls, token=None):
        try:
            if not token:
                token = cls.retrieve_sema_api_token()
            data = cls.retrieve_sema_brands(token)
            return cls.create_brands_from_data(data)
        except Exception as err:
            return cls.get_class_error_msg(str(err))

    @classmethod
    def create_brands_from_data(cls, data):
        msgs = []
        for item in data:
            try:
                brand = cls.objects.get(brand_id=item['AAIABrandId'])
                previous = brand.get_brand_data()
                brand.name = item['BrandName']
                brand.save()
                brand.refresh_from_db()
                new = brand.get_brand_data()
                msgs.append(brand.get_update_success_msg(previous, new))
            except cls.DoesNotExist:
                brand = cls.objects.create(
                    brand_id=item['AAIABrandId'],
                    name=item['BrandName']
                )
                msgs.append(brand.get_create_success_msg())
            except Exception as err:
                msgs.append(cls.get_class_error_msg(str(err)))
        if not msgs:
            msgs.append(cls.get_class_up_to_date_msg())
        return msgs


class SemaDatasetMixin(SemaApiDatasetMixin):
    @staticmethod
    def get_brand(brand_id):
        from product.models import SemaBrand
        try:
            return SemaBrand.objects.get(brand_id=brand_id)
        except Exception:
            raise

    def get_dataset_data(self):
        return {
            'Name': self.name,
            'Brand': str(self.brand)
        }

    @classmethod
    def unauthorize_datasets(cls):
        cls.objects.all().update(is_authorized=False)

    @classmethod
    def import_datasets_from_sema_api(cls, token=None):
        try:
            if not token:
                token = cls.retrieve_sema_api_token()
            data = cls.retrieve_sema_datasets(token)
            return cls.create_datasets_from_data(data)
        except Exception as err:
            return cls.get_class_error_msg(str(err))

    @classmethod
    def create_datasets_from_data(cls, data):
        msgs = []
        cls.unauthorize_datasets()
        for item in data:
            try:
                dataset = cls.objects.get(dataset_id=item['DatasetId'])
                previous = dataset.get_dataset_data()
                dataset.name = item['DatasetName']
                dataset.brand = cls.get_brand(item['AAIABrandId'])
                dataset.is_authorized = True
                dataset.save()
                dataset.refresh_from_db()
                new = dataset.get_dataset_data()
                msgs.append(dataset.get_update_success_msg(previous, new))
            except cls.DoesNotExist:
                dataset = cls.objects.create(
                    dataset_id=item['DatasetId'],
                    name=item['DatasetName'],
                    brand=cls.get_brand(item['AAIABrandId']),
                    is_authorized=True
                )
                msgs.append(dataset.get_create_success_msg())
            except Exception as err:
                msgs.append(cls.get_class_error_msg(str(err)))
        if not msgs:
            msgs.append(cls.get_class_up_to_date_msg())
        return msgs

    def import_products_from_sema_api(self, token=None):
        try:
            if not token:
                token = self.retrieve_sema_api_token()
            data = self.retrieve_sema_products(self.dataset_id, token)
            return self.create_products_from_data(data)
        except Exception as err:
            return self.get_instance_error_msg(str(err))

    def create_products_from_data(self, data):
        from product.models import SemaProduct
        return SemaProduct.create_products_from_data(self.dataset_id, data)


class SemaCategoryMixin(SemaApiCategoryMixin):
    @classmethod
    def get_category(cls, category_id):
        try:
            return cls.objects.get(category_id=category_id)
        except cls.DoesNotExist:
            raise Exception(f'Parent {category_id} does not exist')
        except Exception as err:
            raise

    def get_category_data(self):
        return {
            'Name': self.name,
            'Parent': str(self.parent_category)
        }

    @classmethod
    def import_categories_from_sema_api(cls, dataset_id, token=None):
        try:
            if not token:
                token = cls.retrieve_sema_api_token()
            data = cls.retrieve_sema_categories(dataset_id, token)
            return cls.create_categories_from_data(data)
        except Exception as err:
            return cls.get_class_error_msg(str(err))

    @classmethod
    def create_categories_from_data(cls, data):
        msgs = []
        for item in data:
            try:
                subcategories = item.pop('Categories', [])
                msgs.append(cls.create_category_from_data(item))
                if subcategories:
                    msgs += cls.create_categories_from_data(subcategories)
            except Exception as err:
                msgs.append(cls.get_class_error_msg(str(err)))
        if not msgs:
            msgs.append(cls.get_class_up_to_date_msg())
        return msgs

    @classmethod
    def create_category_from_data(cls, item):
        try:
            category = cls.objects.get(category_id=item['CategoryId'])
            previous = category.get_category_data()
            category.name = item['Name']
            if item['ParentId']:
                parent = cls.get_category(item['ParentId'])
            else:
                parent = None
            category.parent_category = parent
            category.save()
            category.refresh_from_db()
            new = category.get_category_data()
            msg = category.get_update_success_msg(previous, new)
        except cls.DoesNotExist:
            if item['ParentId']:
                parent = cls.get_category(item['ParentId'])
            else:
                parent = None
            category = cls.objects.create(
                category_id=item['CategoryId'],
                name=item['Name'],
                parent_category=parent
            )
            msg = category.get_create_success_msg()
        except Exception as err:
            msg = cls.get_class_error_msg(str(err))
        return msg


class SemaProductMixin(SemaApiProductMixin):
    @staticmethod
    def get_dataset(dataset_id):
        from product.models import SemaDataset

        try:
            return SemaDataset.objects.get(dataset_id=dataset_id)
        except Exception:
            raise

    def get_product_data(self):
        return {
            'Part': self.part_number,
            'Dataset': str(self.dataset)
        }

    @classmethod
    def create_products_from_data(cls, dataset_id, data):
        msgs = []
        for item in data:
            try:
                product = cls.objects.get(product_id=item['ProductId'])
                previous = product.get_product_data()
                product.part_number = item['PartNumber']
                product.dataset = cls.get_dataset(dataset_id)
                product.save()
                product.refresh_from_db()
                new = product.get_product_data()
                msgs.append(product.get_update_success_msg(previous, new))
            except cls.DoesNotExist:
                product = cls.objects.create(
                    product_id=item['ProductId'],
                    part_number=item['PartNumber'],
                    dataset=cls.get_dataset(dataset_id),
                )
                msgs.append(product.get_create_success_msg())
            except Exception as err:
                msgs.append(cls.get_class_error_msg(str(err)))
        if not msgs:
            msgs.append(cls.get_class_up_to_date_msg())
        return msgs

    def update_html_from_sema_api(self, token=None):
        if not self.product_id:
            return self.get_instance_error_msg("SEMA product ID required")

        try:
            if not token:
                token = self.retrieve_sema_api_token()
            html = self.retrieve_sema_product_html(self.product_id, token)
            return self.update_html_from_data(html)
        except Exception as err:
            return self.get_instance_error_msg(str(err))

    def update_html_from_data(self, html):
        try:
            self.html = html
            self.save()
        except Exception as err:
            return self.get_instance_error_msg(str(err))

        self.refresh_from_db()
        return self.get_update_success_msg()
# </editor-fold>
