from django.contrib import messages

from core.admin.actions import BaseActions, RelevancyActions


class ShopifyVendorActions(BaseActions):
    pass


class ShopifyTagActions(BaseActions):
    pass


class ShopifyCollectionRuleActions(BaseActions):
    pass


class ShopifyCollectionActions(RelevancyActions):
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


class ShopifyProductActions(RelevancyActions):
    def update_calculated_fields_queryset_action(self, request, queryset):
        msgs = []
        try:
            msgs += queryset.perform_calculated_fields_update()
            for obj in queryset:
                for variant in obj.variants.all():
                    msgs.append(variant.perform_calculated_fields_update())
            self.display_messages(request, msgs, include_info=False)
        except Exception as err:
            messages.error(request, str(err))
    update_calculated_fields_queryset_action.allowed_permissions = ('view',)
    update_calculated_fields_queryset_action.short_description = (
        'Update calculated fields for selected %(verbose_name_plural)s'
    )

    def update_calculated_fields_object_action(self, request, obj):
        msgs = []
        try:
            msgs.append(obj.perform_calculated_fields_update())
            for variant in obj.variants.all():
                msgs.append(variant.perform_calculated_fields_update())
            self.display_messages(request, msgs, include_info=False)
        except Exception as err:
            messages.error(request, str(err))
    update_calculated_fields_object_action.allowed_permissions = ('view',)
    update_calculated_fields_object_action.label = "Update Calculated Fields"
    update_calculated_fields_object_action.short_description = (
        'Updates calculated fields. '
        'WARNING: Related objects must be up-to-date.'
    )

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
