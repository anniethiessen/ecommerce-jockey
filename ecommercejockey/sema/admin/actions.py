from django.contrib import messages

from core.admin.actions import RelevancyActions


class SemaBaseActions(RelevancyActions):
    def import_new_class_action(self, request, queryset):
        try:
            msgs = self.model.objects.perform_import_from_api(new_only=True)
            self.display_messages(request, msgs, include_info=False)
        except Exception as err:
            messages.error(request, str(err))
    import_new_class_action.allowed_permissions = ('view',)
    import_new_class_action.label = 'Import New from API'
    import_new_class_action.short_description = (
        'Create new objects from SEMA API. '
        'WARNING: All related objects must be up-to-date'
    )

    def import_class_action(self, request, queryset):
        try:
            msgs = self.model.objects.perform_import_from_api(new_only=False)
            self.display_messages(request, msgs, include_info=False)
        except Exception as err:
            messages.error(request, str(err))
    import_class_action.allowed_permissions = ('view',)
    import_class_action.label = 'Import from API'
    import_class_action.short_description = (
        'Create or update all available objects from SEMA API. '
        'WARNING: All related objects must be up-to-date'
    )

    def unauthorize_class_action(self, request, queryset):
        try:
            msgs = self.model.objects.perform_unauthorize_from_api()
            self.display_messages(request, msgs, include_info=False)
        except Exception as err:
            messages.error(request, str(err))
    unauthorize_class_action.allowed_permissions = ('view',)
    unauthorize_class_action.label = 'Unauthorize from API'
    unauthorize_class_action.short_description = (
        'Unauthorizes existing objects no longer returned by API. '
        'WARNING: All related objects must be up-to-date'
    )

    def sync_class_action(self, request, queryset):
        try:
            msgs = self.model.objects.perform_api_sync()
            self.display_messages(request, msgs, include_info=False)
        except Exception as err:
            messages.error(request, str(err))
    sync_class_action.allowed_permissions = ('view',)
    sync_class_action.label = 'Sync with API'
    sync_class_action.short_description = (
        'Create or update all available objects from SEMA API. '
        'Unauthorizes existing objects no longer returned by API. '
        'WARNING: All related objects must be up-to-date'
    )


class SemaDatasetVehiclesActions(SemaBaseActions):
    def update_dataset_vehicles_queryset_action(self, request, queryset):
        try:
            msgs = queryset.perform_dataset_vehicles_update_from_api()
            self.display_messages(request, msgs, include_info=False)
        except Exception as err:
            messages.error(request, str(err))
    update_dataset_vehicles_queryset_action.allowed_permissions = ('view',)
    update_dataset_vehicles_queryset_action.short_description = (
        'Add vehicles to selected %(verbose_name_plural)s from SEMA API'
    )

    def update_dataset_vehicles_object_action(self, request, obj):
        try:
            msgs = obj.perform_dataset_vehicles_update_from_api()
            self.display_messages(request, msgs, include_info=False)
        except Exception as err:
            messages.error(request, str(err))
    update_dataset_vehicles_object_action.allowed_permissions = ('view',)
    update_dataset_vehicles_object_action.label = (
        "Update Vehicles from API"
    )
    update_dataset_vehicles_object_action.short_description = (
        'Add vehicles to this object from SEMA API. '
        'Does not remove existing vehicles no longer returned by API. '
        'WARNING: Related objects must be up-to-date.'
    )


class SemaDatasetCategoriesActions(SemaBaseActions):
    def update_dataset_categories_queryset_action(self, request, queryset):
        try:
            msgs = queryset.perform_dataset_categories_update_from_api()
            self.display_messages(request, msgs, include_info=False)
        except Exception as err:
            messages.error(request, str(err))
    update_dataset_categories_queryset_action.allowed_permissions = ('view',)
    update_dataset_categories_queryset_action.short_description = (
        'Add categories to selected %(verbose_name_plural)s from SEMA API'
    )

    def update_dataset_categories_object_action(self, request, obj):
        try:
            msgs = obj.perform_dataset_categories_update_from_api()
            self.display_messages(request, msgs, include_info=False)
        except Exception as err:
            messages.error(request, str(err))
    update_dataset_categories_object_action.allowed_permissions = ('view',)
    update_dataset_categories_object_action.label = (
        "Update Categories from API"
    )
    update_dataset_categories_object_action.short_description = (
        'Add categories to this object from SEMA API. '
        'Does not remove existing categories no longer returned by API. '
        'WARNING: Related objects must be up-to-date.'
    )


class SemaProductVehiclesActions(SemaBaseActions):
    def update_product_vehicles_queryset_action(self, request, queryset):
        try:
            msgs = queryset.perform_product_vehicle_update()
            self.display_messages(request, msgs, include_info=False)
        except Exception as err:
            messages.error(request, str(err))
    update_product_vehicles_queryset_action.allowed_permissions = ('view',)
    update_product_vehicles_queryset_action.short_description = (
        'Add vehicles to selected %(verbose_name_plural)s from SEMA API'
    )

    def update_product_vehicles_object_action(self, request, obj):
        try:
            msgs = obj.perform_product_vehicle_update()
            self.display_messages(request, msgs, include_info=False)
        except Exception as err:
            messages.error(request, str(err))
    update_product_vehicles_object_action.allowed_permissions = ('view',)
    update_product_vehicles_object_action.label = (
        "Update Vehicles from API"
    )
    update_product_vehicles_object_action.short_description = (
        'Add vehicles to products of this object from SEMA API. '
        'Does not remove existing vehicles no longer returned by API. '
        'WARNING: Related objects must be up-to-date.'
    )


class SemaCategoryProductsActions(SemaBaseActions):
    def update_category_products_queryset_action(self, request, queryset):
        try:
            msgs = queryset.perform_category_products_update_from_api()
            self.display_messages(request, msgs, include_info=False)
        except Exception as err:
            messages.error(request, str(err))
    update_category_products_queryset_action.allowed_permissions = ('view',)
    update_category_products_queryset_action.short_description = (
        'Add products to selected %(verbose_name_plural)s from SEMA API'
    )

    def update_category_products_object_action(self, request, obj):
        try:
            msgs = obj.perform_category_products_update_from_api()
            self.display_messages(request, msgs, include_info=False)
        except Exception as err:
            messages.error(request, str(err))
    update_category_products_object_action.allowed_permissions = ('view',)
    update_category_products_object_action.label = (
        "Update Products from API"
    )
    update_category_products_object_action.short_description = (
        'Add products to this category from SEMA API. '
        'Does not remove existing products no longer returned by API. '
        'WARNING: Related objects must be up-to-date.'
    )


class SemaProductPiesAttributesActions(SemaBaseActions):
    def update_description_pies_object_action(self, request, obj):
        from sema.models import SemaDescriptionPiesAttribute

        try:
            msgs = obj.perform_pies_attribute_update_from_api(
                pies_attr_model=SemaDescriptionPiesAttribute
            )
            self.display_messages(request, msgs, include_info=False)
        except Exception as err:
            messages.error(request, str(err))
    update_description_pies_object_action.allowed_permissions = ('view',)
    update_description_pies_object_action.label = (
        "Update descriptions from API"
    )
    update_description_pies_object_action.short_description = (
        'Update this SEMA product\'s description PIES from SEMA API'
    )

    def update_description_pies_queryset_action(self, request, queryset):
        from sema.models import SemaDescriptionPiesAttribute

        try:
            msgs = queryset.perform_pies_attribute_update_from_api(
                pies_attr_model=SemaDescriptionPiesAttribute
            )
            self.display_messages(request, msgs, include_info=False)
        except Exception as err:
            messages.error(request, str(err))
    update_description_pies_queryset_action.allowed_permissions = ('view',)
    update_description_pies_queryset_action.short_description = (
        'Update selected %(verbose_name_plural)s\' '
        'description PIES from SEMA API'
    )

    def update_digital_assets_pies_object_action(self, request, obj):
        from sema.models import SemaDigitalAssetsPiesAttribute

        try:
            msgs = obj.perform_pies_attribute_update_from_api(
                pies_attr_model=SemaDigitalAssetsPiesAttribute
            )
            self.display_messages(request, msgs, include_info=False)
        except Exception as err:
            messages.error(request, str(err))
    update_digital_assets_pies_object_action.allowed_permissions = ('view',)
    update_digital_assets_pies_object_action.label = (
        "Update assets from API"
    )
    update_digital_assets_pies_object_action.short_description = (
        'Update this SEMA product\'s digital assets PIES from SEMA API'
    )

    def update_digital_assets_pies_queryset_action(self, request, queryset):
        from sema.models import SemaDigitalAssetsPiesAttribute

        try:
            msgs = queryset.perform_pies_attribute_update_from_api(
                pies_attr_model=SemaDigitalAssetsPiesAttribute
            )
            self.display_messages(request, msgs, include_info=False)
        except Exception as err:
            messages.error(request, str(err))
    update_digital_assets_pies_queryset_action.allowed_permissions = ('view',)
    update_digital_assets_pies_queryset_action.short_description = (
        'Update selected %(verbose_name_plural)s\' '
        'digital assets PIES from SEMA API'
    )


class SemaProductHtmlActions(SemaBaseActions):
    def update_html_object_action(self, request, obj):
        try:
            msg = obj.perform_product_html_update_from_api()
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
            msgs = queryset.perform_product_html_update_from_api()
            self.display_messages(request, msgs, include_info=False)
        except Exception as err:
            messages.error(request, str(err))
    update_html_queryset_action.allowed_permissions = ('view',)
    update_html_queryset_action.short_description = (
        'Update selected %(verbose_name_plural)s\' HTML from SEMA API'
    )


class SemaBrandActions(SemaBaseActions):
    pass


class SemaDatasetActions(SemaDatasetCategoriesActions,
                         SemaDatasetVehiclesActions):
    pass


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


class SemaCategoryActions(SemaCategoryProductsActions):
    pass


class SemaProductActions(SemaProductVehiclesActions,
                         SemaProductPiesAttributesActions,
                         SemaProductHtmlActions):
    pass
