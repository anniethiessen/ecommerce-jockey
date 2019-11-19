from django.db.models import QuerySet, Manager


class ShopifyCollectionQuerySet(QuerySet):
    def perform_calculated_fields_update(self):
        msgs = []
        for collection in self:
            try:
                msgs.append(collection.perform_calculated_fields_update())
            except Exception as err:
                msgs.append(self.model.get_class_error_msg(str(err)))

        if not msgs:
            msgs.append(self.model.get_class_up_to_date_msg())
        return msgs

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


class ShopifyProductQuerySet(QuerySet):
    def perform_calculated_fields_update(self):
        msgs = []
        for product in self:
            try:
                msgs.append(product.perform_calculated_fields_update())
            except Exception as err:
                msgs.append(self.model.get_class_error_msg(str(err)))

        if not msgs:
            msgs.append(self.model.get_class_up_to_date_msg())
        return msgs

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


class ShopifyVariantQuerySet(QuerySet):
    def perform_calculated_fields_update(self):
        msgs = []
        for variant in self:
            try:
                msgs.append(variant.perform_calculated_fields_update())
            except Exception as err:
                msgs.append(self.model.get_class_error_msg(str(err)))

        if not msgs:
            msgs.append(self.model.get_class_up_to_date_msg())
        return msgs


class ShopifyOptionQuerySet(QuerySet):
    pass


class ShopifyCollectionManager(Manager):
    def get_queryset(self):
        return ShopifyCollectionQuerySet(
            self.model,
            using=self._db
        )

    def perform_calculated_fields_update(self):
        msgs = []
        try:
            return self.get_queryset().perform_calculated_fields_update()
        except Exception as err:
            msgs.append(self.model.get_class_error_msg(str(err)))

        if not msgs:
            msgs.append(self.model.get_class_up_to_date_msg())
        return msgs

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


class ShopifyProductManager(Manager):
    def get_queryset(self):
        return ShopifyProductQuerySet(
            self.model,
            using=self._db
        )

    def perform_calculated_fields_update(self):
        msgs = []
        try:
            return self.get_queryset().perform_calculated_fields_update()
        except Exception as err:
            msgs.append(self.model.get_class_error_msg(str(err)))

        if not msgs:
            msgs.append(self.model.get_class_up_to_date_msg())
        return msgs

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


class ShopifyVariantManager(Manager):
    def get_queryset(self):
        return ShopifyVariantQuerySet(
            self.model,
            using=self._db
        )

    def perform_calculated_fields_update(self):
        msgs = []
        try:
            return self.get_queryset().perform_calculated_fields_update()
        except Exception as err:
            msgs.append(self.model.get_class_error_msg(str(err)))

        if not msgs:
            msgs.append(self.model.get_class_up_to_date_msg())
        return msgs

    def create_from_api_data(self, product, data):
        try:
            variant = self.create(product=product)
            variant.update_from_api_data(data)
            return variant.get_create_success_msg()
        except Exception as err:
            return self.model.get_class_error_msg(str(err))


class ShopifyOptionManager(Manager):
    def get_queryset(self):
        return ShopifyOptionQuerySet(
            self.model,
            using=self._db
        )

    def create_from_api_data(self, product, data):
        try:
            option = self.create(product=product)
            option.update_from_api_data(data)
            return option.get_create_success_msg()
        except Exception as err:
            return self.model.get_class_error_msg(str(err))
