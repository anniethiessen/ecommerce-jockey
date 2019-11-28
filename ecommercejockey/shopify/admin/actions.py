from django.contrib import messages

from core.admin.actions import BaseActions


class PublishedActions(BaseActions):
    def mark_as_published_queryset_action(self, request, queryset):
        msgs = []
        for obj in queryset:
            try:
                if obj.is_published:
                    msgs.append(
                        obj.get_instance_up_to_date_msg(
                            message="Already published"
                        )
                    )
                else:
                    obj.is_published = True
                    obj.save()
                    msgs.append(
                        obj.get_update_success_msg(
                            message="Updated to published"
                        )
                    )
            except Exception as err:
                msgs.append(
                    obj.get_instance_error_msg(str(err))
                )
        self.display_messages(request, msgs, include_info=False)
    mark_as_published_queryset_action.allowed_permissions = ('view',)
    mark_as_published_queryset_action.short_description = (
        'Mark selected %(verbose_name_plural)s as published'
    )

    def mark_as_unpublished_queryset_action(self, request, queryset):
        msgs = []
        for obj in queryset:
            try:
                if not obj.is_published:
                    msgs.append(
                        obj.get_instance_up_to_date_msg(
                            message="Already NOT published"
                        )
                    )
                else:
                    obj.is_published = False
                    obj.save()
                    msgs.append(
                        obj.get_update_success_msg(
                            message="Updated to NOT published"
                        )
                    )
            except Exception as err:
                msgs.append(
                    obj.get_instance_error_msg(str(err))
                )
        self.display_messages(request, msgs, include_info=False)
    mark_as_unpublished_queryset_action.allowed_permissions = ('view',)
    mark_as_unpublished_queryset_action.short_description = (
        'Mark selected %(verbose_name_plural)s as NOT published'
    )


class CalculateActions(BaseActions):
    def update_calculated_fields_queryset_action(self, request, queryset):
        msgs = []
        try:
            for obj in queryset:
                msgs.append(obj.perform_calculated_fields_update())
            self.display_messages(request, msgs, include_info=False)
        except Exception as err:
            messages.error(request, str(err))
    update_calculated_fields_queryset_action.allowed_permissions = ('view',)
    update_calculated_fields_queryset_action.short_description = (
        'Update calculated fields for selected %(verbose_name_plural)s'
    )

    def update_calculated_fields_object_action(self, request, obj):
        try:
            msg = obj.perform_calculated_fields_update()
            self.display_message(request, msg)
        except Exception as err:
            messages.error(request, str(err))
    update_calculated_fields_object_action.allowed_permissions = ('view',)
    update_calculated_fields_object_action.label = "Update Calculated Fields"
    update_calculated_fields_object_action.short_description = (
        'Updates calculated fields. '
        'WARNING: Related objects must be up-to-date.'
    )


class ShopifyVendorActions(BaseActions):
    pass


class ShopifyTagActions(BaseActions):
    pass


class ShopifyCollectionRuleActions(BaseActions):
    pass


class ShopifyCollectionActions(PublishedActions, CalculateActions):
    def export_to_api_queryset_action(self, request, queryset):
        msgs = []
        try:
            new = queryset.filter(collection_id__isnull=True)
            existing = queryset.filter(collection_id__isnull=False)
            msgs += new.perform_create_to_api()
            msgs += existing.perform_update_to_api()
            self.display_messages(request, msgs, include_info=False)
        except Exception as err:
            messages.error(request, str(err))
    export_to_api_queryset_action.allowed_permissions = ('view',)
    export_to_api_queryset_action.short_description = (
        'Create or update selected %(verbose_name_plural)s in Shopify'
    )

    def export_to_api_object_action(self, request, obj):
        msgs = []
        try:
            if obj.collection_id:
                msgs += obj.perform_update_to_api()
            else:
                msgs += obj.perform_create_to_api()
            self.display_messages(request, msgs, include_info=False)
        except Exception as err:
            messages.error(request, str(err))
    export_to_api_object_action.allowed_permissions = ('view',)
    export_to_api_object_action.label = "Create/Update in Shopify"
    export_to_api_object_action.short_description = (
        'Creates or updates in Shopify. '
        'WARNING: Related objects must be up-to-date.'
    )

    def import_from_api_queryset_action(self, request, queryset):
        try:
            msgs = queryset.perform_update_from_api()
            self.display_messages(request, msgs, include_info=False)
        except Exception as err:
            messages.error(request, str(err))
    import_from_api_queryset_action.allowed_permissions = ('view',)
    import_from_api_queryset_action.short_description = (
        'Update selected %(verbose_name_plural)s from Shopify'
    )

    def import_from_api_object_action(self, request, obj):
        try:
            msgs = obj.perform_update_from_api()
            self.display_messages(request, msgs, include_info=False)
        except Exception as err:
            messages.error(request, str(err))
    import_from_api_object_action.allowed_permissions = ('view',)
    import_from_api_object_action.label = "Update from Shopify"
    import_from_api_object_action.short_description = (
        'Updates object from Shopify data. '
        'WARNING: Related objects must be up-to-date.'
    )


class ShopifyProductActions(PublishedActions, CalculateActions):
    def export_to_api_queryset_action(self, request, queryset):
        msgs = []
        try:
            new = queryset.filter(product_id__isnull=True)
            existing = queryset.filter(product_id__isnull=False)
            msgs += new.perform_create_to_api()
            msgs += existing.perform_update_to_api()
            self.display_messages(request, msgs, include_info=False)
        except Exception as err:
            messages.error(request, str(err))
    export_to_api_queryset_action.allowed_permissions = ('view',)
    export_to_api_queryset_action.short_description = (
        'Create or update selected %(verbose_name_plural)s in Shopify'
    )

    def export_to_api_object_action(self, request, obj):
        msgs = []
        try:
            if obj.product_id:
                msgs += obj.perform_update_to_api()
            else:
                msgs += obj.perform_create_to_api()
            self.display_messages(request, msgs, include_info=False)
        except Exception as err:
            messages.error(request, str(err))
    export_to_api_object_action.allowed_permissions = ('view',)
    export_to_api_object_action.label = "Create/Update in Shopify"
    export_to_api_object_action.short_description = (
        'Creates or updates in Shopify. '
        'WARNING: Related objects must be up-to-date.'
    )

    def import_from_api_queryset_action(self, request, queryset):
        try:
            msgs = queryset.perform_update_from_api()
            self.display_messages(request, msgs, include_info=False)
        except Exception as err:
            messages.error(request, str(err))
    import_from_api_queryset_action.allowed_permissions = ('view',)
    import_from_api_queryset_action.short_description = (
        'Update selected %(verbose_name_plural)s from Shopify'
    )

    def import_from_api_object_action(self, request, obj):
        try:
            msgs = obj.perform_update_from_api()
            self.display_messages(request, msgs, include_info=False)
        except Exception as err:
            messages.error(request, str(err))
    import_from_api_object_action.allowed_permissions = ('view',)
    import_from_api_object_action.label = "Update from Shopify"
    import_from_api_object_action.short_description = (
        'Updates object from Shopify data. '
        'WARNING: Related objects must be up-to-date.'
    )


class ShopifyImageActions(BaseActions):
    pass


class ShopifyOptionActions(BaseActions):
    pass


class ShopifyVariantActions(BaseActions):
    pass


class ShopifyMetafieldActions(BaseActions):
    pass


class ShopifyProductCalculatorActions(CalculateActions):
    pass


class ShopifyCollectionCalculatorActions(CalculateActions):
    pass
