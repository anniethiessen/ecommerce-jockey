from django.db.models import QuerySet, Manager, Count, Q


class ShopifyVendorQuerySet(QuerySet):
    def with_admin_data(self):
        return self.prefetch_related(
            'products',
        ).annotate(
            _product_count=Count(
                'products',
                distinct=True
            ),
            _product_published_count=Count(
                'products',
                filter=Q(products__is_published=True),
                distinct=True
            )
        )


class ShopifyTagQuerySet(QuerySet):
    def with_admin_data(self):
        return self.prefetch_related(
            'products',
            'collections'
        ).annotate(
            _product_count=Count(
                'products',
                distinct=True
            ),
            _product_published_count=Count(
                'products',
                filter=Q(products__is_published=True),
                distinct=True
            ),
            _collection_count=Count(
                'collections',
                distinct=True
            ),
            _collection_published_count=Count(
                'collections',
                filter=Q(collections__is_published=True),
                distinct=True
            )
        )


class ShopifyCollectionRuleQuerySet(QuerySet):
    def with_admin_data(self):
        return self.prefetch_related(
            'collections'
        ).annotate(
            _collection_count=Count(
                'collections',
                distinct=True
            ),
            _collection_published_count=Count(
                'collections',
                filter=Q(collections__is_published=True),
                distinct=True
            )
        )


class ShopifyCollectionQuerySet(QuerySet):
    def with_admin_data(self):
        return self.select_related(
            'calculator',
            'parent_collection'
        ).prefetch_related(
            'rules',
            'tags',
            'metafields',
            'child_collections'
        ).annotate(
            _rule_count=Count(
                'rules',
                distinct=True
            ),
            _tag_count=Count(
                'tags',
                distinct=True
            ),
            _metafield_count=Count(
                'metafields',
                distinct=True
            ),
            _child_collection_count=Count(
                'child_collections',
                distinct=True
            ),
            _child_collection_published_count=Count(
                'child_collections',
                filter=Q(child_collections__is_published=True),
                distinct=True
            )
        )

    # <editor-fold desc="perform properties ...">
    def perform_create_to_api(self):
        msgs = []
        for collection in self:
            try:
                msgs += collection.perform_create_to_api()
            except Exception as err:
                msgs.append(collection.get_instance_error_msg(str(err)))

        if not msgs:
            msgs.append(self.model.get_class_up_to_date_msg())
        return msgs

    def perform_update_to_api(self):
        msgs = []
        for collection in self:
            try:
                msgs += collection.perform_update_to_api()
            except Exception as err:
                msgs.append(collection.get_instance_error_msg(str(err)))

        if not msgs:
            msgs.append(self.model.get_class_up_to_date_msg())
        return msgs

    def perform_update_from_api(self):
        msgs = []
        for collection in self:
            try:
                msgs += collection.perform_update_from_api()
            except Exception as err:
                msgs.append(collection.get_instance_error_msg(str(err)))

        if not msgs:
            msgs.append(self.model.get_class_up_to_date_msg())
        return msgs
    # </editor-fold>


class ShopifyProductQuerySet(QuerySet):
    def with_admin_data(self):
        return self.select_related(
            'calculator',
            'vendor'
        ).prefetch_related(
            'variants',
            'options',
            'images',
            'tags',
            'metafields'
        ).annotate(
            _variant_count=Count(
                'variants',
                distinct=True
            ),
            _option_count=Count(
                'options',
                distinct=True
            ),
            _image_count=Count(
                'images',
                distinct=True
            ),
            _tag_count=Count(
                'tags',
                distinct=True
            ),
            _metafield_count=Count(
                'metafields',
                distinct=True
            )
        )

    # <editor-fold desc="perform properties ...">
    def perform_create_to_api(self):
        msgs = []
        for product in self:
            try:
                msgs += product.perform_create_to_api()
            except Exception as err:
                msgs.append(product.get_instance_error_msg(str(err)))

        if not msgs:
            msgs.append(self.model.get_class_up_to_date_msg())
        return msgs

    def perform_update_to_api(self):
        msgs = []
        for product in self:
            try:
                msgs += product.perform_update_to_api()
            except Exception as err:
                msgs.append(product.get_instance_error_msg(str(err)))

        if not msgs:
            msgs.append(self.model.get_class_up_to_date_msg())
        return msgs

    def perform_update_from_api(self):
        msgs = []
        for product in self:
            try:
                msgs += product.perform_update_from_api()
            except Exception as err:
                msgs.append(product.get_instance_error_msg(str(err)))

        if not msgs:
            msgs.append(self.model.get_class_up_to_date_msg())
        return msgs
    # </editor-fold>


class ShopifyVariantQuerySet(QuerySet):
    def with_admin_data(self):
        return self.select_related(
            'product'
        )


class ShopifyOptionQuerySet(QuerySet):
    def with_admin_data(self):
        return self.select_related(
            'product'
        )


class ShopifyMetafieldQuerySet(QuerySet):
    def with_admin_data(self):
        return self.select_related(
            'content_type'
        )

    # <editor-fold desc="perform properties ...">
    def perform_create_to_api(self):
        msgs = []
        for metafield in self:
            try:
                msgs += metafield.perform_create_to_api()
            except Exception as err:
                msgs.append(metafield.get_instance_error_msg(str(err)))

        if not msgs:
            msgs.append(self.model.get_class_up_to_date_msg())
        return msgs

    def perform_update_to_api(self):
        msgs = []
        for metafield in self:
            try:
                msgs += metafield.perform_update_to_api()
            except Exception as err:
                msgs.append(metafield.get_instance_error_msg(str(err)))

        if not msgs:
            msgs.append(self.model.get_class_up_to_date_msg())
        return msgs

    def perform_update_from_api(self):
        msgs = []
        for metafield in self:
            try:
                msgs += metafield.perform_update_from_api()
            except Exception as err:
                msgs.append(metafield.get_instance_error_msg(str(err)))

        if not msgs:
            msgs.append(self.model.get_class_up_to_date_msg())
        return msgs
    # </editor-fold>


class ShopifyImageQuerySet(QuerySet):
    def with_admin_data(self):
        return self.select_related(
            'product'
        )

    # <editor-fold desc="perform properties ...">
    def perform_create_to_api(self):
        msgs = []
        for image in self:
            try:
                msgs += image.perform_create_to_api()
            except Exception as err:
                msgs.append(image.get_instance_error_msg(str(err)))

        if not msgs:
            msgs.append(self.model.get_class_up_to_date_msg())
        return msgs

    def perform_update_to_api(self):
        msgs = []
        for image in self:
            try:
                msgs += image.perform_update_to_api()
            except Exception as err:
                msgs.append(image.get_instance_error_msg(str(err)))

        if not msgs:
            msgs.append(self.model.get_class_up_to_date_msg())
        return msgs

    def perform_update_from_api(self):
        msgs = []
        for image in self:
            try:
                msgs += image.perform_update_from_api()
            except Exception as err:
                msgs.append(image.get_instance_error_msg(str(err)))

        if not msgs:
            msgs.append(self.model.get_class_up_to_date_msg())
        return msgs
    # </editor-fold>


class ShopifyProductCalculatorQuerySet(QuerySet):
    def with_admin_data(self):
        return self.select_related(
            'product'
        )


class ShopifyCollectionCalculatorQuerySet(QuerySet):
    def with_admin_data(self):
        return self.select_related(
            'collection'
        )


class ShopifyVendorManager(Manager):
    def get_queryset(self):
        return ShopifyVendorQuerySet(
            self.model,
            using=self._db
        )

    def with_admin_data(self):
        return self.get_queryset().with_admin_data()


class ShopifyTagManager(Manager):
    def get_queryset(self):
        return ShopifyTagQuerySet(
            self.model,
            using=self._db
        )

    def with_admin_data(self):
        return self.get_queryset().with_admin_data()


class ShopifyCollectionRuleManager(Manager):
    def get_queryset(self):
        return ShopifyCollectionRuleQuerySet(
            self.model,
            using=self._db
        )

    def with_admin_data(self):
        return self.get_queryset().with_admin_data()


class ShopifyCollectionManager(Manager):
    def get_queryset(self):
        return ShopifyCollectionQuerySet(
            self.model,
            using=self._db
        )

    def with_admin_data(self):
        return self.get_queryset().with_admin_data()

    # <editor-fold desc="perform properties ...">
    def perform_create_to_api(self):
        msgs = []
        try:
            msgs += self.get_queryset().perform_create_to_api()
        except Exception as err:
            msgs.append(self.model.get_class_error_msg(str(err)))

        if not msgs:
            msgs.append(self.model.get_class_up_to_date_msg())
        return msgs

    def perform_update_to_api(self):
        msgs = []
        try:
            msgs += self.get_queryset().perform_update_to_api()
        except Exception as err:
            msgs.append(self.model.get_class_error_msg(str(err)))

        if not msgs:
            msgs.append(self.model.get_class_up_to_date_msg())
        return msgs

    def perform_update_from_api(self):
        msgs = []
        try:
            msgs += self.get_queryset().perform_update_from_api()
        except Exception as err:
            msgs.append(self.model.get_class_error_msg(str(err)))

        if not msgs:
            msgs.append(self.model.get_class_up_to_date_msg())
        return msgs
    # </editor-fold>


class ShopifyProductManager(Manager):
    def get_queryset(self):
        return ShopifyProductQuerySet(
            self.model,
            using=self._db
        )

    def with_admin_data(self):
        return self.get_queryset().with_admin_data()

    # <editor-fold desc="perform properties ...">
    def perform_create_to_api(self):
        msgs = []
        try:
            msgs += self.get_queryset().perform_create_to_api()
        except Exception as err:
            msgs.append(self.model.get_class_error_msg(str(err)))

        if not msgs:
            msgs.append(self.model.get_class_up_to_date_msg())
        return msgs

    def perform_update_to_api(self):
        msgs = []
        try:
            msgs += self.get_queryset().perform_update_to_api()
        except Exception as err:
            msgs.append(self.model.get_class_error_msg(str(err)))

        if not msgs:
            msgs.append(self.model.get_class_up_to_date_msg())
        return msgs

    def perform_update_from_api(self):
        msgs = []
        try:
            msgs += self.get_queryset().perform_update_from_api()
        except Exception as err:
            msgs.append(self.model.get_class_error_msg(str(err)))

        if not msgs:
            msgs.append(self.model.get_class_up_to_date_msg())
        return msgs
    # </editor-fold>


class ShopifyVariantManager(Manager):
    def get_queryset(self):
        return ShopifyVariantQuerySet(
            self.model,
            using=self._db
        )

    def with_admin_data(self):
        return self.get_queryset().with_admin_data()

    # <editor-fold desc="import properties ...">
    def create_from_api_data(self, product, data):
        try:
            variant = self.create(product=product)
            variant.update_from_api_data(data)
            return variant.get_create_success_msg()
        except Exception as err:
            return self.model.get_class_error_msg(str(err))
    # </editor-fold>


class ShopifyOptionManager(Manager):
    def get_queryset(self):
        return ShopifyOptionQuerySet(
            self.model,
            using=self._db
        )

    def with_admin_data(self):
        return self.get_queryset().with_admin_data()

    # <editor-fold desc="import properties ...">
    def create_from_api_data(self, product, data):
        try:
            option = self.create(product=product)
            option.update_from_api_data(data)
            return option.get_create_success_msg()
        except Exception as err:
            return self.model.get_class_error_msg(str(err))
    # </editor-fold>


class ShopifyMetafieldManager(Manager):
    def get_queryset(self):
        return ShopifyMetafieldQuerySet(
            self.model,
            using=self._db
        )

    def with_admin_data(self):
        return self.get_queryset().with_admin_data()

    # <editor-fold desc="perform properties ...">
    def perform_create_to_api(self):
        msgs = []
        try:
            msgs += self.get_queryset().perform_create_to_api()
        except Exception as err:
            msgs.append(self.model.get_class_error_msg(str(err)))

        if not msgs:
            msgs.append(self.model.get_class_up_to_date_msg())
        return msgs

    def perform_update_to_api(self):
        msgs = []
        try:
            msgs += self.get_queryset().perform_update_to_api()
        except Exception as err:
            msgs.append(self.model.get_class_error_msg(str(err)))

        if not msgs:
            msgs.append(self.model.get_class_up_to_date_msg())
        return msgs

    def perform_update_from_api(self):
        msgs = []
        try:
            msgs += self.get_queryset().perform_update_from_api()
        except Exception as err:
            msgs.append(self.model.get_class_error_msg(str(err)))

        if not msgs:
            msgs.append(self.model.get_class_up_to_date_msg())
        return msgs
    # </editor-fold>


class ShopifyImageManager(Manager):
    def get_queryset(self):
        return ShopifyImageQuerySet(
            self.model,
            using=self._db
        )

    def with_admin_data(self):
        return self.get_queryset().with_admin_data()

    # <editor-fold desc="perform properties ...">
    def perform_create_to_api(self):
        msgs = []
        try:
            msgs += self.get_queryset().perform_create_to_api()
        except Exception as err:
            msgs.append(self.model.get_class_error_msg(str(err)))

        if not msgs:
            msgs.append(self.model.get_class_up_to_date_msg())
        return msgs

    def perform_update_to_api(self):
        msgs = []
        try:
            msgs += self.get_queryset().perform_update_to_api()
        except Exception as err:
            msgs.append(self.model.get_class_error_msg(str(err)))

        if not msgs:
            msgs.append(self.model.get_class_up_to_date_msg())
        return msgs

    def perform_update_from_api(self):
        msgs = []
        try:
            msgs += self.get_queryset().perform_update_from_api()
        except Exception as err:
            msgs.append(self.model.get_class_error_msg(str(err)))

        if not msgs:
            msgs.append(self.model.get_class_up_to_date_msg())
        return msgs
    # </editor-fold>


class ShopifyProductCalculatorManager(Manager):
    def get_queryset(self):
        return ShopifyProductCalculatorQuerySet(
            self.model,
            using=self._db
        )

    def with_admin_data(self):
        return self.get_queryset().with_admin_data()


class ShopifyCollectionCalculatorManager(Manager):
    def get_queryset(self):
        return ShopifyCollectionCalculatorQuerySet(
            self.model,
            using=self._db
        )

    def with_admin_data(self):
        return self.get_queryset().with_admin_data()
