from django.db.models import Manager, QuerySet


class VendorQuerySet(QuerySet):
    pass


class ItemQuerySet(QuerySet):
    pass


class VendorManager(Manager):
    def check_unlinked_vendors(self):
        from premier.models import PremierManufacturer
        from .models import SemaBrand

        msgs = []

        premier_manufacturers = PremierManufacturer.objects.all()
        sema_brands = SemaBrand.objects.filter(is_authorized=True)
        vendors = self.model.objects.all()

        for manufacturer in premier_manufacturers:
            try:
                vendor = self.model.objects.get(
                    premier_manufacturer=manufacturer
                )
                msgs.append(
                    manufacturer.get_instance_up_to_date_msg(
                        message='Already exists'
                    )
                )
            except self.model.DoesNotExist:
                msgs.append(
                    manufacturer.get_instance_error_msg('Does not exist')
                )
            except Exception as err:
                msgs.append(self.model.get_class_error_msg(str(err)))

        for brand in sema_brands:
            try:
                vendor = self.model.objects.get(sema_brand=brand)
                msgs.append(
                    brand.get_instance_up_to_date_msg(
                        message='Already exists'
                    )
                )
            except self.model.DoesNotExist:
                msgs.append(
                    brand.get_instance_error_msg('Does not exist')
                )
            except Exception as err:
                msgs.append(self.model.get_class_error_msg(str(err)))

        return msgs

    def get_queryset(self):
        return VendorQuerySet(
            self.model,
            using=self._db
        )


class ItemManager(Manager):
    def create_products_from_premier_products(self):
        from premier.models import PremierProduct

        msgs = []

        try:
            premier_products = PremierProduct.objects.filter(is_relevant=True)
            for premier_product in premier_products:
                try:
                    product = self.model.objects.get(
                        premier_product=premier_product
                    )
                    msgs.append(
                        product.get_instance_up_to_date_msg(
                            message=f'Already exists'
                        )
                    )
                except self.model.DoesNotExist:
                    product = self.model.objects.create(
                        premier_product=premier_product
                    )
                    msgs.append(product.get_create_success_msg())
        except Exception as err:
            msgs.append(self.model.get_class_error_msg(str(err)))

        return msgs

    def link_products(self):
        from premier.models import PremierProduct
        from .models import SemaProduct, Vendor

        msgs = []
        premier_products = self.model.objects.filter(
            premier_product__isnull=False,
            sema_product__isnull=True
        )
        sema_products = self.model.objects.filter(
            sema_product__isnull=False,
            premier_product__isnull=True
        )

        for product in premier_products:
            try:
                vendor = Vendor.objects.get(
                    premier_manufacturer=product.premier_product.manufacturer
                )
                sema_product = SemaProduct.objects.get(
                    dataset__brand=vendor.sema_brand,
                    part_number=product.premier_product.vendor_part_number,
                )
                product.sema_product = sema_product
                product.save()
                msgs.append(
                    product.get_update_success_msg(
                        message=f"{sema_product} added to {product}"
                    )
                )
            except Vendor.DoesNotExist:
                msgs.append(
                    product.premier_product.get_instance_error_msg(
                        "Vendor does not exist"
                    )
                )
            except SemaProduct.DoesNotExist:
                msgs.append(
                    product.premier_product.get_instance_error_msg(
                        "SEMA product does not exist"
                    )
                )
            except Exception as err:
                msgs.append(product.get_instance_error_msg(str(err)))

        for product in sema_products:
            try:
                vendor = Vendor.objects.get(
                    sema_brand=product.sema_product.dataset.brand
                )
                premier_product = PremierProduct.objects.get(
                    manufacturer=vendor.premier_manufacturer,
                    vendor_part_number=product.sema_product.part_number
                )
                product.premier_product = premier_product
                product.save()
                msgs.append(
                    product.get_update_success_msg(
                        message=f"{premier_product} added to {product}"
                    )
                )
            except Vendor.DoesNotExist:
                msgs.append(
                    product.sema_product.dataset.brand.get_instance_error_msg(
                        "Vendor does not exist"
                    )
                )
            except PremierProduct.DoesNotExist:
                msgs.append(
                    product.sema_product.get_instance_error_msg(
                        "Premier product does not exist"
                    )
                )
            except Exception as err:
                msgs.append(product.get_instance_error_msg(str(err)))

        if not msgs:
            msgs.append(self.model.get_class_up_to_date_msg())
        return msgs

    def get_queryset(self):
        return ItemQuerySet(
            self.model,
            using=self._db
        )
