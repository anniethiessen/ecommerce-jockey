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
