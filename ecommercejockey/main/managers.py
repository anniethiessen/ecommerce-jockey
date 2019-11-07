from django.db.models import Manager, QuerySet


class VendorQuerySet(QuerySet):
    pass


class ItemQuerySet(QuerySet):
    def create_shopify_products(self):
        from .models import ShopifyProduct

        msgs = []
        for item in self:
            if item.shopify_product:
                msgs.append(
                    item.get_instance_error_msg(
                        error='Shopify product already exists'
                    )
                )
                continue

            if not (item.premier_product and item.sema_product):
                msgs.append(
                    item.get_instance_error_msg(
                        error='Missing Premier and/or SEMA products'
                    )
                )
                continue

            try:
                vendor = item.premier_product.manufacturer.vendor.shopify_vendor
                shopify_product = ShopifyProduct.objects.create(vendor=vendor)
                item.shopify_product = shopify_product
                item.save()
                msgs.append(shopify_product.get_create_success_msg())
            except Exception as err:
                msgs.append(item.get_instance_error_msg(str(err)))

        if not msgs:
            msgs.append(self.model.get_class_up_to_date_msg())
        return msgs


class VendorManager(Manager):
    def check_unlinked_vendors(self):
        from premier.models import PremierManufacturer
        from sema.models import SemaBrand
        from shopify.models import ShopifyVendor

        msgs = []

        premier_manufacturers = PremierManufacturer.objects.all()
        sema_brands = SemaBrand.objects.filter(is_authorized=True)
        shopify_vendors = ShopifyVendor.objects.all()
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

        for _vendor in shopify_vendors:
            try:
                vendor = self.model.objects.get(shopify_vendor=_vendor)
                msgs.append(
                    vendor.get_instance_up_to_date_msg(
                        message='Already exists'
                    )
                )
            except self.model.DoesNotExist:
                msgs.append(
                    _vendor.get_instance_error_msg('Does not exist')
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
    def create_from_relevant(self):
        from premier.models import PremierProduct
        from sema.models import SemaProduct

        msgs = []
        premier_products = PremierProduct.objects.filter(
            is_relevant=True,
            item__isnull=True
        )
        sema_products = SemaProduct.objects.filter(
            is_relevant=True,
            items__isnull=True
        )

        for product in premier_products:
            try:
                item = self.model.objects.get(premier_product=product)
                msgs.append(
                    item.get_instance_up_to_date_msg(
                        message='Already exists'
                    )
                )
            except self.model.DoesNotExist:
                try:
                    item = self.model.objects.get(
                        sema_product__dataset__brand__vendor__premier_manufacturer=product.manufacturer,
                        sema_product__part_number=product.vendor_part_number
                    )
                    item.premier_product = product
                    item.save()
                    msgs.append(
                        item.get_update_success_msg(
                            message=f"{product} added"
                        )
                    )
                except self.model.DoesNotExist:
                    item = self.model.objects.create(
                        premier_product=product
                    )
                    msgs.append(item.get_create_success_msg())
                except Exception as err:
                    msgs.append(self.model.get_class_error_msg(str(err)))
            except Exception as err:
                msgs.append(self.model.get_class_error_msg(str(err)))

        for product in sema_products:
            try:
                item = self.model.objects.get(sema_product=product)
                msgs.append(
                    item.get_instance_up_to_date_msg(
                        message='Already exists'
                    )
                )
            except self.model.DoesNotExist:
                try:
                    item = self.model.objects.get(
                        premier_product__manufacturer__vendor__sema_brand=product.dataset.brand,
                        premier_product__vendor_part_number=product.part_number
                    )
                    item.sema_product = product
                    item.save()
                    msgs.append(
                        item.get_update_success_msg(
                            message=f"{product} added"
                        )
                    )
                except self.model.DoesNotExist:
                    item = self.model.objects.create(
                        sema_product=product
                    )
                    msgs.append(item.get_create_success_msg())
                except Exception as err:
                    msgs.append(self.model.get_class_error_msg(str(err)))
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

    def create_shopify_products(self):
        msgs = []

        try:
            msgs += self.get_queryset().create_shopify_products()
        except Exception as err:
            msgs.append(self.model.get_class_error_msg(str(err)))

        if not msgs:
            msgs.append(self.model.get_class_up_to_date_msg())
        return msgs

    def get_queryset(self):
        return ItemQuerySet(
            self.model,
            using=self._db
        )
