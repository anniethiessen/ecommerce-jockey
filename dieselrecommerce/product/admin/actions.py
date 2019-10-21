from django.contrib import messages


class BaseActions(object):
    def display_messages(self, request, msgs, include_info=True):
        if not include_info:
            msgs = [msg for msg in msgs if not msg[:4] == 'Info']
            if not msgs:
                msgs.append(self.model.get_class_up_to_date_msg())

        for msg in msgs:
            self.display_message(request, msg)

    def display_message(self, request, msg):
        if msg[:4] == 'Info':
            messages.warning(request, msg)
        elif msg[:7] == 'Success':
            messages.success(request, msg)
        else:
            messages.error(request, msg)


class PremierProductActions(BaseActions):
    def update_inventory_queryset_action(self, request, queryset):
        try:
            msgs = queryset.update_inventory_from_api()
            self.display_messages(request, msgs, include_info=False)
        except Exception as err:
            messages.error(request, str(err))
    update_inventory_queryset_action.allowed_permissions = ('view',)
    update_inventory_queryset_action.short_description = (
        'Update selected %(verbose_name_plural)s\' inventory from Premier API'
    )

    def update_inventory_object_action(self, request, obj):
        try:
            msg = obj.update_inventory_from_api()
            self.display_message(request, msg)
        except Exception as err:
            messages.error(request, str(err))
    update_inventory_object_action.allowed_permissions = ('view',)
    update_inventory_object_action.label = "Update Inventory from API"
    update_inventory_object_action.short_description = (
        'Update this Premier product\'s inventory from Premier API'
    )

    def update_pricing_queryset_action(self, request, queryset):
        try:
            msgs = queryset.update_pricing_from_api()
            self.display_messages(request, msgs, include_info=False)
        except Exception as err:
            messages.error(request, str(err))
    update_pricing_queryset_action.allowed_permissions = ('view',)
    update_pricing_queryset_action.short_description = (
        'Update selected %(verbose_name_plural)s\' pricing from Premier API'
    )

    def update_pricing_object_action(self, request, obj):
        try:
            msg = obj.update_pricing_from_api()
            self.display_message(request, msg)
        except Exception as err:
            messages.error(request, str(err))
    update_pricing_object_action.allowed_permissions = ('view',)
    update_pricing_object_action.label = "Update Pricing from API"
    update_pricing_object_action.short_description = (
        'Update this Premier product\'s pricing from Premier API'
    )


class SemaBaseActions(BaseActions):
    def import_and_unauthorize_class_action(self, request, queryset):
        try:
            msgs = self.model.objects.import_and_unauthorize_from_api()
            self.display_messages(request, msgs, include_info=False)
        except Exception as err:
            messages.error(request, str(err))
    import_and_unauthorize_class_action.allowed_permissions = ('view',)
    import_and_unauthorize_class_action.label = 'Import from API'
    import_and_unauthorize_class_action.short_description = (
        'Create or update all available objects from SEMA API. '
        'Unauthorizes existing objects no longer returned by API. '
        'WARNING: All related objects must be up-to-date'
    )


class SemaBrandActions(SemaBaseActions):
    def import_datasets_object_action(self, request, obj):
        try:
            msgs = obj.import_datasets_from_api()
            self.display_messages(request, msgs, include_info=False)
        except Exception as err:
            messages.error(request, str(err))
    import_datasets_object_action.allowed_permissions = ('view',)
    import_datasets_object_action.label = "Import Datasets from API"
    import_datasets_object_action.short_description = (
        'Create or update all available datasets of this brand from SEMA API. '
        'Does not unauthorizes existing objects no longer returned by API. '
        'WARNING: Brand must be up-to-date'
    )

    def import_datasets_queryset_action(self, request, queryset):
        try:
            msgs = queryset.import_datasets_from_api()
            self.display_messages(request, msgs, include_info=False)
        except Exception as err:
            messages.error(request, str(err))
    import_datasets_queryset_action.allowed_permissions = ('view',)
    import_datasets_queryset_action.short_description = (
        'Import datasets for selected %(verbose_name_plural)s\' from SEMA API'
    )


class SemaDatasetActions(SemaBaseActions):
    pass

    # def import_products_object_action(self, request, obj):
    #     if not obj.is_authorized:
    #         messages.error(request, "Dataset needs to be authorized")
    #         return
    #
    #     try:
    #         token = self.model.retrieve_sema_api_token()
    #     except Exception as err:
    #         messages.error(request, f"Token error: {err}")
    #         return
    #
    #     try:
    #         msgs = obj.import_products_from_sema_api(token)
    #         for msg in msgs:
    #             if msg[:4] == 'Info':
    #                 messages.info(request, msg)
    #             elif msg[:7] == 'Success':
    #                 messages.success(request, msg)
    #             else:
    #                 messages.error(request, msg)
    #     except Exception as err:
    #         messages.error(request, str(err))
    # import_products_object_action.allowed_permissions = ('view',)
    # import_products_object_action.label = 'Import Products from API'
    # import_products_object_action.short_description = (
    #     'Import products from SEMA API'
    # )
    #
    # def import_products_queryset_action(self, request, queryset):
    #     try:
    #         token = self.model.retrieve_sema_api_token()
    #     except Exception as err:
    #         messages.error(request, f"Token error: {err}")
    #         return
    #
    #     try:
    #         msgs = queryset.import_products_from_sema_api(token)
    #         for msg in msgs:
    #             if msg[:4] == 'Info':
    #                 messages.info(request, msg)
    #             elif msg[:7] == 'Success':
    #                 messages.success(request, msg)
    #             else:
    #                 messages.error(request, msg)
    #     except Exception as err:
    #         messages.error(request, str(err))
    # import_products_queryset_action.allowed_permissions = ('view',)
    # import_products_queryset_action.short_description = (
    #     'Import products from SEMA API for selected %(verbose_name_plural)s'
    # )


class SemaYearActions(SemaBaseActions):
    pass


class SemaMakeActions(SemaBaseActions):
    pass


class SemaModelActions(SemaBaseActions):
    pass


class SemaSubmodelActions(SemaBaseActions):
    pass


class SemaMakeYearActions(SemaBaseActions):
    pass


class SemaBaseVehicleActions(SemaBaseActions):
    pass


class SemaVehicleActions(SemaBaseActions):
    pass


class SemaCategoryActions(SemaBaseActions):
    def update_products_object_action(self, request, obj):
        try:
            msgs = obj.update_products_from_api()
            self.display_messages(request, msgs)
        except Exception as err:
            messages.error(request, str(err))
    update_products_object_action.allowed_permissions = ('view',)
    update_products_object_action.label = "Update products from API"
    update_products_object_action.short_description = (
        'Update SEMA product\'s for this category from SEMA API'
    )

    def update_products_queryset_action(self, request, queryset):
        try:
            msgs = queryset.update_products_from_api()
            self.display_messages(request, msgs)
        except Exception as err:
            messages.error(request, str(err))
    update_products_queryset_action.allowed_permissions = ('view',)
    update_products_queryset_action.short_description = (
        'Update selected %(verbose_name_plural)s\' products from SEMA API'
    )


class SemaProductActions(SemaBaseActions):
    def update_categories_class_action(self, request, queryset):
        try:
            msgs = self.model.objects.update_categories_from_api()
            self.display_messages(request, msgs)
        except Exception as err:
            messages.error(request, str(err))
    update_categories_class_action.allowed_permissions = ('view',)
    update_categories_class_action.label = "Update categories from API"
    update_categories_class_action.short_description = (
        'Update all SEMA product\'s categories from SEMA API'
    )

    def update_html_object_action(self, request, obj):
        try:
            msg = obj.update_html_from_api()
            self.display_message(request, msg)
        except Exception as err:
            messages.error(request, str(err))
    update_html_object_action.allowed_permissions = ('view',)
    update_html_object_action.label = "Update HTML from API"
    update_html_object_action.short_description = (
        'Update this SEMA product\'s HTML from SEMA API'
    )

    def update_html_queryset_action(self, request, queryset):
        try:
            msgs = queryset.update_html_from_api()
            self.display_messages(request, msgs, include_info=False)
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
