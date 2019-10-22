class MessagesMixin(object):
    @classmethod
    def get_class_up_to_date_msg(cls, message="everything up-to-date"):
        return (
            "Info: "
            f"{cls._meta.verbose_name.title()}, {message}"
        )

    def get_instance_up_to_date_msg(self, message="already up-to-date"):
        return (
            "Info: "
            f"{self._meta.model._meta.verbose_name.title()} {self}, {message}"
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
                               message=None, include_up_to_date=True):
        msg = (
            "Success: "
            f"{self._meta.model._meta.verbose_name.title()} {self} updated"
        )
        if message:
            msg += f', {message}'
        elif previous_data and new_data:
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
