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
