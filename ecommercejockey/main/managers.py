from django.db.models import Manager, QuerySet, Q


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
                msgs.append(shopify_product.get_create_success_msg())
            except Exception as err:
                msgs.append(item.get_instance_error_msg(str(err)))

        if not msgs:
            msgs.append(self.model.get_class_up_to_date_msg())
        return msgs


class CategoryPathQuerySet(QuerySet):
    def create_shopify_collections(self):
        from shopify.models import ShopifyCollection, ShopifyTag

        msgs = []
        for category_path in self:
            root_collection_title = category_path.sema_root_category.name
            root_collection_tag, _ = ShopifyTag.objects.get_or_create(
                name=category_path.sema_root_category.tag_name
            )
            root_collection_tags = ShopifyTag.objects.filter(
                pk=root_collection_tag.pk
            )
            try:
                root_collection = category_path.shopify_collections.get(
                    title=root_collection_title
                )
                if root_collection_tag not in root_collection.tags.all():
                    root_collection.tags.add(root_collection_tag)
                    root_collection.save()
                    msgs.append(
                        root_collection.get_update_success_msg(
                            message=f'Tag {root_collection_tag} added'
                        )
                    )
            except ShopifyCollection.DoesNotExist:
                root_collection = None
                existing_collections = ShopifyCollection.objects.filter(
                    title=root_collection_title
                )
                for existing_collection in existing_collections:
                    existing_tags = set(existing_collection.tags.all())
                    root_tags = set(root_collection_tags)
                    if ((not root_tags.difference(existing_tags))
                            and (not existing_tags.difference(root_tags))):
                        root_collection = existing_collection
                        break
                if not root_collection:
                    root_collection = ShopifyCollection.objects.create(
                        title=root_collection_title
                    )
                    for tag in root_collection_tags:
                        root_collection.tags.add(tag)
                    root_collection.save()
                    msgs.append(root_collection.get_create_success_msg())

                category_path.shopify_collections.add(root_collection)
                category_path.save()
                msgs.append(
                    category_path.get_update_success_msg(
                        message=f'Collection {root_collection} added'
                    )
                )
            except Exception as err:
                msgs.append(category_path.get_instance_error_msg(str(err)))

            branch_collection_title = (
                f'{root_collection_title} '
                f'/ {category_path.sema_branch_category.name}'
            )
            # branch_collection_title = category_path.sema_branch_category.name
            branch_collection_tag, _ = ShopifyTag.objects.get_or_create(
                name=category_path.sema_branch_category.tag_name
            )
            branch_collection_tags = ShopifyTag.objects.filter(
                Q(pk=root_collection_tag.pk)
                | Q(pk=branch_collection_tag.pk)
            )
            try:
                branch_collection = category_path.shopify_collections.get(
                    title=branch_collection_title
                )
                if root_collection_tag not in branch_collection.tags.all():
                    branch_collection.tags.add(root_collection_tag)
                    branch_collection.save()
                    msgs.append(
                        branch_collection.get_update_success_msg(
                            message=f'Tag {root_collection_tag} added'
                        )
                    )
                if branch_collection_tag not in branch_collection.tags.all():
                    branch_collection.tags.add(branch_collection_tag)
                    branch_collection.save()
                    msgs.append(
                        branch_collection.get_update_success_msg(
                            message=f'Tag {branch_collection_tag} added'
                        )
                    )
            except ShopifyCollection.DoesNotExist:
                branch_collection = None
                existing_collections = ShopifyCollection.objects.filter(
                    title=branch_collection_title
                )
                for existing_collection in existing_collections:
                    existing_tags = set(existing_collection.tags.all())
                    branch_tags = set(branch_collection_tags)
                    if ((not branch_tags.difference(existing_tags))
                            and (not existing_tags.difference(branch_tags))):
                        branch_collection = existing_collection
                        break
                if not branch_collection:
                    branch_collection = ShopifyCollection.objects.create(
                        title=branch_collection_title
                    )
                    for tag in branch_collection_tags:
                        branch_collection.tags.add(tag)
                    branch_collection.save()
                    msgs.append(branch_collection.get_create_success_msg())

                category_path.shopify_collections.add(branch_collection)
                category_path.save()
                msgs.append(
                    category_path.get_update_success_msg(
                        message=f'Collection {branch_collection} added'
                    )
                )
            except Exception as err:
                msgs.append(category_path.get_instance_error_msg(str(err)))

            leaf_collection_title = (
                f'{branch_collection_title} '
                f'/ {category_path.sema_leaf_category.name}'
            )
            # leaf_collection_title = category_path.sema_leaf_category.name
            leaf_collection_tag, _ = ShopifyTag.objects.get_or_create(
                name=category_path.sema_leaf_category.tag_name
            )
            leaf_collection_tags = ShopifyTag.objects.filter(
                Q(pk=root_collection_tag.pk)
                | Q(pk=branch_collection_tag.pk)
                | Q(pk=leaf_collection_tag.pk)
            )
            try:
                leaf_collection = category_path.shopify_collections.get(
                    title=leaf_collection_title
                )
                if root_collection_tag not in leaf_collection.tags.all():
                    leaf_collection.tags.add(root_collection_tag)
                    leaf_collection.save()
                    msgs.append(
                        leaf_collection.get_update_success_msg(
                            message=f'Tag {root_collection_tag} added'
                        )
                    )
                if branch_collection_tag not in leaf_collection.tags.all():
                    leaf_collection.tags.add(branch_collection_tag)
                    leaf_collection.save()
                    msgs.append(
                        leaf_collection.get_update_success_msg(
                            message=f'Tag {branch_collection_tag} added'
                        )
                    )
                if leaf_collection_tag not in leaf_collection.tags.all():
                    leaf_collection.tags.add(leaf_collection_tag)
                    leaf_collection.save()
                    msgs.append(
                        leaf_collection.get_update_success_msg(
                            message=f'Tag {leaf_collection_tag} added'
                        )
                    )
            except ShopifyCollection.DoesNotExist:
                leaf_collection = None
                existing_collections = ShopifyCollection.objects.filter(
                    title=leaf_collection_title
                )
                for existing_collection in existing_collections:
                    existing_tags = set(existing_collection.tags.all())
                    leaf_tags = set(leaf_collection_tags)
                    if ((not leaf_tags.difference(existing_tags))
                            and (not existing_tags.difference(leaf_tags))):
                        leaf_collection = existing_collection
                        break
                if not leaf_collection:
                    leaf_collection = ShopifyCollection.objects.create(
                        title=leaf_collection_title
                    )
                    for tag in leaf_collection_tags:
                        leaf_collection.tags.add(tag)
                    leaf_collection.save()
                    msgs.append(leaf_collection.get_create_success_msg())

                category_path.shopify_collections.add(leaf_collection)
                category_path.save()
                msgs.append(
                    category_path.get_update_success_msg(
                        message=f'Collection {leaf_collection} added'
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
