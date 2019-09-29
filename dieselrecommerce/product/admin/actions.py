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
                if msg[:7] == 'Success':
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
        try:
            token = self.model.retrieve_premier_api_token()
        except Exception as err:
            messages.error(request, f"Token error: {err}")
            return

        try:
            msg = obj.update_inventory_from_premier_api(token)
            if msg[:7] == 'Success':
                messages.success(request, msg)
            else:
                messages.error(request, msg)
        except Exception as err:
            messages.error(request, str(err))
    update_inventory_object_action.allowed_permissions = ('view',)
    update_inventory_object_action.label = "Update Inventory from API"
    update_inventory_object_action.short_description = (
        'Update this premier product\'s inventory from Premier API'
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
                if msg[:7] == 'Success':
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
        try:
            token = self.model.retrieve_premier_api_token()
        except Exception as err:
            messages.error(request, f"Token error: {err}")
            return

        try:
            msg = obj.update_pricing_from_premier_api(token)
            if msg[:7] == 'Success':
                messages.success(request, msg)
            else:
                messages.error(request, msg)
        except Exception as err:
            messages.error(request, str(err))
    update_pricing_object_action.allowed_permissions = ('view',)
    update_pricing_object_action.label = "Update Pricing from API"
    update_pricing_object_action.short_description = (
        'Update this premier product\'s pricing from Premier API'
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
                if msg[:7] == 'Success':
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
                if msg[:7] == 'Success':
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
            messages.error(request, f"Dataset {obj} not authorized")
            return

        try:
            token = self.model.retrieve_sema_api_token()
        except Exception as err:
            messages.error(request, f"Token error: {err}")
            return

        try:
            msgs = obj.import_products_from_sema_api(token)
            for msg in msgs:
                if msg[:7] == 'Success':
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