from django.db.models import Manager, QuerySet


class VendorQuerySet(QuerySet):
    pass


class ItemQuerySet(QuerySet):
    def create_shopify_products(self):
        from shopify.models import ShopifyProduct

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
                shopify_product.perform_calculated_fields_update()
                shopify_product.variants.first().perform_calculated_fields_update()
                msgs.append(shopify_product.get_create_success_msg())
            except Exception as err:
                msgs.append(item.get_instance_error_msg(str(err)))

        if not msgs:
            msgs.append(self.model.get_class_up_to_date_msg())
        return msgs


class CategoryPathQuerySet(QuerySet):
    def create_shopify_collections(self):
        from shopify.models import ShopifyCollection

        msgs = []
        for category_path in self:
            if (category_path.shopify_root_collection
                    and category_path.shopify_branch_collection
                    and category_path.shopify_leaf_collection):
                msgs.append(
                    category_path.get_instance_error_msg(
                        error='Shopify collections already exists'
                    )
                )
                continue

            if category_path.shopify_root_collection:
                root_collection = category_path.shopify_root_collection
            else:
                try:
                    title = category_path.sema_root_category.name
                    root_collection, created = ShopifyCollection.objects.get_or_create(
                        title=title,
                        parent_collection=None
                    )
                    category_path.shopify_root_collection = root_collection
                    category_path.save()
                    if created:
                        msgs.append(root_collection.get_create_success_msg())
                    msgs.append(
                        category_path.get_update_success_msg(
                            message=f'{root_collection} added'
                        )
                    )
                except Exception as err:
                    msgs.append(category_path.get_instance_error_msg(str(err)))
                    continue

            if category_path.shopify_branch_collection:
                branch_collection = category_path.shopify_branch_collection
            else:
                try:
                    title = (
                        f'{category_path.sema_root_category.name} '
                        f'// {category_path.sema_branch_category.name}'
                    )
                    branch_collection, created = ShopifyCollection.objects.get_or_create(
                        title=title,
                        parent_collection=root_collection
                    )
                    category_path.shopify_branch_collection = branch_collection
                    category_path.save()
                    if created:
                        msgs.append(branch_collection.get_create_success_msg())
                    msgs.append(
                        category_path.get_update_success_msg(
                            message=f'{branch_collection} added'
                        )
                    )
                except Exception as err:
                    msgs.append(category_path.get_instance_error_msg(str(err)))
                    continue

            if not category_path.shopify_leaf_collection:
                try:
                    title = (
                        f'{category_path.sema_root_category.name} '
                        f'// {category_path.sema_branch_category.name} '
                        f'// {category_path.sema_leaf_category.name}'
                    )
                    leaf_collection, created = ShopifyCollection.objects.get_or_create(
                        title=title,
                        parent_collection=branch_collection
                    )
                    category_path.shopify_leaf_collection = leaf_collection
                    category_path.save()
                    if created:
                        msgs.append(leaf_collection.get_create_success_msg())
                    msgs.append(
                        category_path.get_update_success_msg(
                            message=f'{leaf_collection} added'
                        )
                    )
                except Exception as err:
                    msgs.append(category_path.get_instance_error_msg(str(err)))
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
    def create_and_link(self):
        from premier.models import PremierProduct
        from sema.models import SemaProduct
        from .models import Vendor

        msgs = []

        premier_products = PremierProduct.objects.filter(item__isnull=True)
        for premier_product in premier_products:
            try:
                item = self.create(premier_product=premier_product)
                msgs.append(item.get_create_success_msg())
            except Exception as err:
                msgs.append(premier_product.get_instance_error_msg(str(err)))

        incomplete_items = self.filter(sema_product__isnull=True)
        for item in incomplete_items:
            try:
                sema_product = SemaProduct.objects.get(
                    dataset__brand__vendor=item.premier_product.manufacturer.vendor,
                    part_number=item.premier_product.vendor_part_number
                )
                item.sema_product = sema_product
                item.save()
                msgs.append(
                    item.get_update_success_msg(
                        message=f"Sema product {sema_product} added"
                    )
                )
            except SemaProduct.DoesNotExist:
                msgs.append(
                    item.get_instance_error_msg(
                        error="Sema product does not exist"
                    )
                )
            except Exception as err:
                msgs.append(item.get_instance_error_msg(str(err)))

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


class CategoryPathManager(Manager):
    def create_and_link(self):
        from sema.models import SemaCategory

        msgs = []
        categories = SemaCategory.objects.all()

        for category in categories:
            if category.level == '1':
                root_category = category
                for child_category in category.child_categories.all():
                    branch_category = child_category
                    for grandchild_category in child_category.child_categories.all():
                        leaf_category = grandchild_category
                        try:
                            path = self.get(
                                sema_root_category=root_category,
                                sema_branch_category=branch_category,
                                sema_leaf_category=leaf_category
                            )
                            msgs.append(
                                path.get_instance_up_to_date_msg(
                                    message='Already exists'
                                )
                            )
                        except self.model.DoesNotExist:
                            path = self.create(
                                sema_root_category=root_category,
                                sema_branch_category=branch_category,
                                sema_leaf_category=leaf_category
                            )
                            msgs.append(path.get_create_success_msg())
                        except Exception as err:
                            msgs.append(
                                self.model.get_class_error_msg(str(err))
                            )
            elif category.level == '2':
                branch_category = category
                for parent_category in category.parent_categories.all():
                    root_category = parent_category
                    for child_category in category.child_categories.all():
                        leaf_category = child_category
                        try:
                            path = self.get(
                                sema_root_category=root_category,
                                sema_branch_category=branch_category,
                                sema_leaf_category=leaf_category
                            )
                            msgs.append(
                                path.get_instance_up_to_date_msg(
                                    message='Already exists'
                                )
                            )
                        except self.model.DoesNotExist:
                            path = self.create(
                                sema_root_category=root_category,
                                sema_branch_category=branch_category,
                                sema_leaf_category=leaf_category
                            )
                            msgs.append(path.get_create_success_msg())
                        except Exception as err:
                            msgs.append(
                                self.model.get_class_error_msg(str(err))
                            )
            elif category.level == '3':
                leaf_category = category
                for parent_category in category.parent_categories.all():
                    branch_category = parent_category
                    for grandparent_category in parent_category.parent_categories.all():
                        root_category = grandparent_category
                        try:
                            path = self.get(
                                sema_root_category=root_category,
                                sema_branch_category=branch_category,
                                sema_leaf_category=leaf_category
                            )
                            msgs.append(
                                path.get_instance_up_to_date_msg(
                                    message='Already exists'
                                )
                            )
                        except self.model.DoesNotExist:
                            path = self.create(
                                sema_root_category=root_category,
                                sema_branch_category=branch_category,
                                sema_leaf_category=leaf_category
                            )
                            msgs.append(path.get_create_success_msg())
                        except Exception as err:
                            msgs.append(
                                self.model.get_class_error_msg(str(err))
                            )
            else:
                msgs.append(category.get_instance_error_msg('Invalid level'))
                continue

        if not msgs:
            msgs.append(self.model.get_class_up_to_date_msg())
        return msgs

    def create_shopify_collections(self):
        msgs = []

        try:
            msgs += self.get_queryset().create_shopify_collections()
        except Exception as err:
            msgs.append(self.model.get_class_error_msg(str(err)))

        if not msgs:
            msgs.append(self.model.get_class_up_to_date_msg())
        return msgs

    def get_queryset(self):
        return CategoryPathQuerySet(
            self.model,
            using=self._db
        )
