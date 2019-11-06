from django.db.models import QuerySet, Manager


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
