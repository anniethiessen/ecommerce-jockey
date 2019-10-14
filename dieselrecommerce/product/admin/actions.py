from django.contrib import messages


class PremierProductActions(object):
    def update_inventory_queryset_action(self, request, queryset):
        try:
            token = self.model.retrieve_premier_api_token()
        except Exception as err:
            messages.error(request, f"Token error: {err}")
            return

        try:
            msgs = queryset.update_inventory_from_premier_api(token)
            for msg in msgs:
                if msg[:4] == 'Info':
                    messages.info(request, msg)
                elif msg[:7] == 'Success':
                    messages.success(request, msg)
                else:
                    messages.error(request, msg)
        except Exception as err:
            messages.error(request, str(err))
    update_inventory_queryset_action.allowed_permissions = ('view',)
    update_inventory_queryset_action.short_description = (
        'Update selected %(verbose_name_plural)s\' inventory from Premier API'
    )

    def update_inventory_object_action(self, request, obj):
        if not obj.premier_part_number:
            messages.error(request, "Premier Part Number required")
            return

        try:
            token = self.model.retrieve_premier_api_token()
        except Exception as err:
            messages.error(request, f"Token error: {err}")
            return

        try:
            msg = obj.update_inventory_from_premier_api(token)
            if msg[:4] == 'Info':
                messages.info(request, msg)
            elif msg[:7] == 'Success':
                messages.success(request, msg)
            else:
                messages.error(request, msg)
        except Exception as err:
            messages.error(request, str(err))
    update_inventory_object_action.allowed_permissions = ('view',)
    update_inventory_object_action.label = "Update Inventory from API"
    update_inventory_object_action.short_description = (
        'Update this Premier product\'s inventory from Premier API'
    )

    def update_pricing_queryset_action(self, request, queryset):
        try:
            token = self.model.retrieve_premier_api_token()
        except Exception as err:
            messages.error(request, f"Token error: {err}")
            return

        try:
            msgs = queryset.update_pricing_from_premier_api(token)
            for msg in msgs:
                if msg[:4] == 'Info':
                    messages.info(request, msg)
                elif msg[:7] == 'Success':
                    messages.success(request, msg)
                else:
                    messages.error(request, msg)
        except Exception as err:
            messages.error(request, str(err))
    update_pricing_queryset_action.allowed_permissions = ('view',)
    update_pricing_queryset_action.short_description = (
        'Update selected %(verbose_name_plural)s\' pricing from Premier API'
    )

    def update_pricing_object_action(self, request, obj):
        if not obj.premier_part_number:
            messages.error(request, "Premier Part Number required")
            return

        try:
            token = self.model.retrieve_premier_api_token()
        except Exception as err:
            messages.error(request, f"Token error: {err}")
            return

        try:
            msg = obj.update_pricing_from_premier_api(token)
            if msg[:4] == 'Info':
                messages.info(request, msg)
            elif msg[:7] == 'Success':
                messages.success(request, msg)
            else:
                messages.error(request, msg)
        except Exception as err:
            messages.error(request, str(err))
    update_pricing_object_action.allowed_permissions = ('view',)
    update_pricing_object_action.label = "Update Pricing from API"
    update_pricing_object_action.short_description = (
        'Update this Premier product\'s pricing from Premier API'
    )


class BaseActions(object):
    def display_message(self, request, msg):
        if msg[:4] == 'Info':
            messages.warning(request, msg)
        elif msg[:7] == 'Success':
            messages.success(request, msg)
        else:
            messages.error(request, msg)


class SemaBaseActions(BaseActions):
    def import_full_class_action(self, request, queryset):
        try:
            msgs = self.model.import_from_api()
            for msg in msgs:
                self.display_message(request, msg)
        except Exception as err:
            messages.error(request, str(err))
    import_full_class_action.allowed_permissions = ('view',)
    import_full_class_action.label = 'Full Import from API'
    import_full_class_action.short_description = (
        'Create, update, authorize, and unauthorize '
        'all available objects from SEMA API'
    )

    def import_new_class_action(self, request, queryset):
        try:
            msgs = self.model.import_from_api(new_only=True)
            for msg in msgs:
                self.display_message(request, msg)
        except Exception as err:
            messages.error(request, str(err))
    import_new_class_action.allowed_permissions = ('view',)
    import_new_class_action.label = 'Import New from API'
    import_new_class_action.short_description = (
        'Create new available objects from SEMA API '
        '(does not update, authorize, or unauthorize existing)'
    )


class SemaYearActions(SemaBaseActions):
    pass


class SemaMakeActions(SemaBaseActions):
    pass


class SemaModelActions(SemaBaseActions):
    pass


class SemaSubmodelActions(SemaBaseActions):
    pass


class SemaBaseVehicleActions(SemaBaseActions):
    def import_full_class_action(self, request, queryset):
        super().import_full_class_action(request, queryset)
    import_full_class_action.short_description = (
        'Create, update, authorize, and unauthorize '
        'all available objects from SEMA API. '
        'WARNING: Years and makes must be up-to-date'
    )

    def import_new_class_action(self, request, queryset):
        super().import_new_class_action(request, queryset)
    import_new_class_action.short_description = (
        'Create new available objects from SEMA API '
        '(does not update, authorize, or unauthorize existing). '
        'WARNING: Years and makes must be up-to-date'
    )


class SemaVehicleActions(object):
    def import_vehicles_class_action(self, request, queryset):
        from product.models import SemaBaseVehicle

        msgs = []
        base_vehicles = SemaBaseVehicle.objects.all()

        try:
            token = self.model.retrieve_sema_api_token()
        except Exception as err:
            messages.error(request, f"Token error: {err}")
            return

        for base_vehicle in base_vehicles:
            try:
                msgs += self.model.import_vehicles_from_sema_api(
                    base_vehicle_id=base_vehicle.base_vehicle_id,
                    year=base_vehicle.year.year,
                    make_id=base_vehicle.make.make_id,
                    model_id=base_vehicle.model.model_id,
                    token=token
                )
            except Exception as err:
                msgs.append(self.model.get_class_error_msg(str(err)))

        for msg in msgs:
            if msg[:4] == 'Info':
                messages.info(request, msg)
            elif msg[:7] == 'Success':
                messages.success(request, msg)
            else:
                messages.error(request, msg)
    import_vehicles_class_action.allowed_permissions = ('view',)
    import_vehicles_class_action.label = 'Import Vehicles from API'
    import_vehicles_class_action.short_description = (
        'Import all available vehicles from SEMA API'
    )


class SemaBrandActions(object):
    def import_brands_class_action(self, request, queryset):
        try:
            token = self.model.retrieve_sema_api_token()
        except Exception as err:
            messages.error(request, f"Token error: {err}")
            return

        try:
            msgs = self.model.import_brands_from_sema_api(token)
            for msg in msgs:
                if msg[:4] == 'Info':
                    messages.info(request, msg)
                elif msg[:7] == 'Success':
                    messages.success(request, msg)
                else:
                    messages.error(request, msg)
        except Exception as err:
            messages.error(request, str(err))
    import_brands_class_action.allowed_permissions = ('view',)
    import_brands_class_action.label = 'Import Brands from API'
    import_brands_class_action.short_description = (
        'Import brands from SEMA API'
    )


class SemaDatasetActions(object):
    def import_datasets_class_action(self, request, queryset):
        try:
            token = self.model.retrieve_sema_api_token()
        except Exception as err:
            messages.error(request, f"Token error: {err}")
            return

        try:
            msgs = self.model.import_datasets_from_sema_api(token)
            for msg in msgs:
                if msg[:4] == 'Info':
                    messages.info(request, msg)
                elif msg[:7] == 'Success':
                    messages.success(request, msg)
                else:
                    messages.error(request, msg)
        except Exception as err:
            messages.error(request, str(err))
    import_datasets_class_action.allowed_permissions = ('view',)
    import_datasets_class_action.label = 'Import Datasets from API'
    import_datasets_class_action.short_description = (
        'Import datasets from SEMA API'
    )

    def import_products_object_action(self, request, obj):
        if not obj.is_authorized:
            messages.error(request, "Dataset needs to be authorized")
            return

        try:
            token = self.model.retrieve_sema_api_token()
        except Exception as err:
            messages.error(request, f"Token error: {err}")
            return

        try:
            msgs = obj.import_products_from_sema_api(token)
            for msg in msgs:
                if msg[:4] == 'Info':
                    messages.info(request, msg)
                elif msg[:7] == 'Success':
                    messages.success(request, msg)
                else:
                    messages.error(request, msg)
        except Exception as err:
            messages.error(request, str(err))
    import_products_object_action.allowed_permissions = ('view',)
    import_products_object_action.label = 'Import Products from API'
    import_products_object_action.short_description = (
        'Import products from SEMA API'
    )

    def import_products_queryset_action(self, request, queryset):
        try:
            token = self.model.retrieve_sema_api_token()
        except Exception as err:
            messages.error(request, f"Token error: {err}")
            return

        try:
            msgs = queryset.import_products_from_sema_api(token)
            for msg in msgs:
                if msg[:4] == 'Info':
                    messages.info(request, msg)
                elif msg[:7] == 'Success':
                    messages.success(request, msg)
                else:
                    messages.error(request, msg)
        except Exception as err:
            messages.error(request, str(err))
    import_products_queryset_action.allowed_permissions = ('view',)
    import_products_queryset_action.short_description = (
        'Import products from SEMA API for selected %(verbose_name_plural)s'
    )


class SemaCategoryActions(object):
    def import_categories_class_action(self, request, queryset):
        from product.models import SemaDataset

        msgs = []
        datasets = SemaDataset.objects.all()

        try:
            token = self.model.retrieve_sema_api_token()
        except Exception as err:
            messages.error(request, f"Token error: {err}")
            return

        for dataset in datasets:
            try:
                msgs += self.model.import_categories_from_sema_api(
                    dataset_id=dataset.dataset_id,
                    token=token
                )
            except Exception as err:
                msgs.append(self.model.get_class_error_msg(str(err)))

        for msg in msgs:
            if msg[:4] == 'Info':
                messages.info(request, msg)
            elif msg[:7] == 'Success':
                messages.success(request, msg)
            else:
                messages.error(request, msg)
    import_categories_class_action.allowed_permissions = ('view',)
    import_categories_class_action.label = 'Import Categories from API'
    import_categories_class_action.short_description = (
        'Import all available categories from SEMA API'
    )


class SemaProductActions(object):
    def update_html_object_action(self, request, obj):
        if not obj.product_id:
            messages.error(request, "SEMA product ID required")
            return

        try:
            token = self.model.retrieve_sema_api_token()
        except Exception as err:
            messages.error(request, f"Token error: {err}")
            return

        try:
            msg = obj.update_html_from_sema_api(token)
            if msg[:4] == 'Info':
                messages.info(request, msg)
            elif msg[:7] == 'Success':
                messages.success(request, msg)
            else:
                messages.error(request, msg)
        except Exception as err:
            messages.error(request, str(err))
    update_html_object_action.allowed_permissions = ('view',)
    update_html_object_action.label = "Update HTML from API"
    update_html_object_action.short_description = (
        'Update this SEMA product\'s HTML from SEMA API'
    )

    def update_html_queryset_action(self, request, queryset):
        try:
            token = self.model.retrieve_sema_api_token()
        except Exception as err:
            messages.error(request, f"Token error: {err}")
            return

        try:
            msgs = queryset.update_html_from_sema_api(token)
            for msg in msgs:
                if msg[:4] == 'Info':
                    messages.info(request, msg)
                elif msg[:7] == 'Success':
                    messages.success(request, msg)
                else:
                    messages.error(request, msg)
        except Exception as err:
            messages.error(request, str(err))
    update_html_queryset_action.allowed_permissions = ('view',)
    update_html_queryset_action.short_description = (
        'Update selected %(verbose_name_plural)s\' HTML from SEMA API'
    )


class ProductActions(object):
    def link_products_class_action(self, request, queryset):
        try:
            msgs = self.model.link_products()
            for msg in msgs:
                if msg[:4] == 'Info':
                    messages.info(request, msg)
                elif msg[:7] == 'Success':
                    messages.success(request, msg)
                else:
                    messages.error(request, msg)
        except Exception as err:
            messages.error(request, str(err))
    link_products_class_action.allowed_permissions = ('view',)
    link_products_class_action.label = 'Link products'
    link_products_class_action.short_description = (
        'Create product if Premier product and Sema product exist'
    )


class ManufacturerActions(object):
    def check_unlinked_manufacturers_class_action(self, request, queryset):
        try:
            msgs = self.model.check_unlinked_manufacturers()
            for msg in msgs:
                if msg[:4] == 'Info':
                    messages.info(request, msg)
                elif msg[:7] == 'Success':
                    messages.success(request, msg)
                else:
                    messages.error(request, msg)
        except Exception as err:
            messages.error(request, str(err))
    check_unlinked_manufacturers_class_action.allowed_permissions = ('view',)
    check_unlinked_manufacturers_class_action.label = 'Check manufacturers'
    check_unlinked_manufacturers_class_action.short_description = (
        'Check if any unlinked Premier manufacturers and SEMA brands exist')
