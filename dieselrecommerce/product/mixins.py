import json
import time

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
    def get_class_nothing_new_msg(cls):
        return (
            "Info: "
            f"{cls._meta.verbose_name.title()}, "
            "nothing new"
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

    def get_update_success_msg(self, previous_data=None, new_data=None,
                               include_up_to_date=True):
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
            elif include_up_to_date:
                msg = self.get_instance_up_to_date_msg()
            else:
                msg = None
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
            try:
                token = cls.retrieve_premier_api_token()
            except Exception as err:
                raise Exception(f"Token error: {err}")

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
        if not token:
            try:
                token = cls.retrieve_premier_api_token()
            except Exception as err:
                return cls.get_class_error_msg(f"Token error: {err}")

        try:
            url = f'{settings.PREMIER_BASE_URL}/inventory'
            params = {'itemNumbers': ','.join(part_numbers)}
            headers = cls.get_premier_api_headers(token)
            response = requests.get(url=url, headers=headers,
                                    params=params)
            response.raise_for_status()
            return json.loads(response.text)
        except Exception:
            raise

    @classmethod
    def retrieve_premier_api_pricing(cls, part_numbers, token=None):
        if not token:
            try:
                token = cls.retrieve_premier_api_token()
            except Exception as err:
                return cls.get_class_error_msg(f"Token error: {err}")

        try:
            url = f'{settings.PREMIER_BASE_URL}/pricing'
            params = {'itemNumbers': ','.join(part_numbers)}
            headers = cls.get_premier_api_headers(token)
            response = requests.get(url=url, headers=headers,
                                    params=params)
            response.raise_for_status()
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
            return self.get_instance_error_msg("Premier Part Number required")

        if not token:
            try:
                token = self.retrieve_premier_api_token()
            except Exception as err:
                return self.get_instance_error_msg(f"Token error: {err}")

        try:
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

        if not token:
            try:
                token = self.retrieve_premier_api_token()
            except Exception as err:
                return self.get_instance_error_msg(f"Token error: {err}")

        try:
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
            if response.status_code == 409:
                time.sleep(1)
                return cls.retrieve_sema_api_token()
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
        if not token:
            try:
                token = cls.retrieve_sema_api_token()
            except Exception as err:
                raise Exception(f"Token error: {err}")

        try:
            url = f'{settings.SEMA_BASE_URL}/token/getcontenttoken'
            params = {'token': token}
            response = requests.get(url=url, params=params)
            if response.status_code == 409:
                time.sleep(1)
                return cls.retrieve_sema_api_content_token(token)
            response.raise_for_status()
            response = json.loads(response.text)
            if response.get('success', False):
                return response['contenttoken']
            else:
                raise Exception(response.get('message', 'Bad request'))
        except Exception:
            raise


class SemaApiBrandMixin(SemaApiCoreMixin):
    @classmethod
    def retrieve_sema_brands(cls, token=None):
        if not token:
            try:
                token = cls.retrieve_sema_api_token()
            except Exception as err:
                raise Exception(f"Token error: {err}")

        try:
            url = f'{settings.SEMA_BASE_URL}/export/branddatasets'
            params = {'token': token}
            response = requests.get(url=url, params=params)
            if response.status_code == 409:
                time.sleep(1)
                return cls.retrieve_sema_brands(token)
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
        if not token:
            try:
                token = cls.retrieve_sema_api_token()
            except Exception as err:
                raise Exception(f"Token error: {err}")

        try:
            url = f'{settings.SEMA_BASE_URL}/export/branddatasets'
            params = {'token': token}
            response = requests.get(url=url, params=params)
            if response.status_code == 409:
                time.sleep(1)
                return cls.retrieve_sema_datasets(token)
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
        if not token:
            try:
                token = cls.retrieve_sema_api_token()
            except Exception as err:
                raise Exception(f"Token error: {err}")

        try:
            url = f'{settings.SEMA_BASE_URL}/lookup/products'
            data = {
                'token': token,
                'branddatasetid': dataset_id
            }
            response = requests.post(url=url, json=data)
            if response.status_code == 409:
                time.sleep(1)
                return cls.retrieve_sema_products(dataset_id, token)
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
        if not token:
            try:
                token = cls.retrieve_sema_api_token()
            except Exception as err:
                raise Exception(f"Token error: {err}")

        try:
            url = f'{settings.SEMA_BASE_URL}/lookup/categories'
            data = {
                'token': token,
                'branddatasetid': dataset_id
            }
            response = requests.post(url=url, json=data)
            if response.status_code == 409:
                time.sleep(1)
                return cls.retrieve_sema_categories(dataset_id, token)
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

        if not token:
            try:
                token = cls.retrieve_sema_api_token()
            except Exception as err:
                raise Exception(f"Token error: {err}")

        try:
            content_token = cls.retrieve_sema_api_content_token(token)
            url = f'{settings.SEMA_BASE_URL}/content/product'
            url += f'?contenttoken={content_token}'
            params = {
                'productid': product_id,
                'stripHeaderFooter': str(~include_sema_header_footer).lower()
            }
            response = requests.get(url=url, params=params)
            if response.status_code == 409:
                time.sleep(1)
                return cls.retrieve_sema_product_html(product_id, token)
            return str(response.text).strip()
        except Exception:
            raise


class SemaBrandMixin(SemaApiBrandMixin):
    def get_brand_data(self):
        return {
            'Name': self.name
        }

    @classmethod
    def import_brands_from_sema_api(cls, token=None):
        if not token:
            try:
                token = cls.retrieve_sema_api_token()
            except Exception as err:
                return cls.get_class_error_msg(f"Token error: {err}")

        try:
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
        if not token:
            try:
                token = cls.retrieve_sema_api_token()
            except Exception as err:
                return cls.get_class_error_msg(f"Token error: {err}")

        try:
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
        if not token:
            try:
                token = self.retrieve_sema_api_token()
            except Exception as err:
                return self.get_instance_error_msg(f"Token error: {err}")

        try:
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
        if not token:
            try:
                token = cls.retrieve_sema_api_token()
            except Exception as err:
                return cls.get_class_error_msg(f"Token error: {err}")

        try:
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
            if parent:
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

        if not token:
            try:
                token = self.retrieve_sema_api_token()
            except Exception as err:
                return self.get_instance_error_msg(f"Token error: {err}")

        try:
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
