from django.contrib import messages

from core.admin.actions import RelevancyActions


class PremierManufacturerActions(RelevancyActions):
    pass


class PremierProductActions(RelevancyActions):
    def update_inventory_queryset_action(self, request, queryset):
        try:
            msgs = queryset.perform_inventory_update_from_api()
            self.display_messages(request, msgs, include_info=False)
        except Exception as err:
            messages.error(request, str(err))
    update_inventory_queryset_action.allowed_permissions = ('view',)
    update_inventory_queryset_action.short_description = (
        'Update selected %(verbose_name_plural)s\' inventory from Premier API'
    )

    def update_inventory_object_action(self, request, obj):
        try:
            msg = obj.perform_inventory_update_from_api()
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
            msgs = queryset.perform_pricing_update_from_api()
            self.display_messages(request, msgs, include_info=False)
        except Exception as err:
            messages.error(request, str(err))
    update_pricing_queryset_action.allowed_permissions = ('view',)
    update_pricing_queryset_action.short_description = (
        'Update selected %(verbose_name_plural)s\' pricing from Premier API'
    )

    def update_pricing_object_action(self, request, obj):
        try:
            msg = obj.perform_pricing_update_from_api()
            self.display_message(request, msg)
        except Exception as err:
            messages.error(request, str(err))
    update_pricing_object_action.allowed_permissions = ('view',)
    update_pricing_object_action.label = "Update Pricing from API"
    update_pricing_object_action.short_description = (
        'Update this Premier product\'s pricing from Premier API'
    )

    def update_primary_image_queryset_action(self, request, queryset):
        try:
            msgs = queryset.perform_primary_image_update_from_media_root()
            self.display_messages(request, msgs, include_info=False)
        except Exception as err:
            messages.error(request, str(err))
    update_primary_image_queryset_action.allowed_permissions = ('view',)
    update_primary_image_queryset_action.short_description = (
        'Update selected %(verbose_name_plural)s\' primary image from media'
    )

    def update_primary_image_object_action(self, request, obj):
        try:
            msg = obj.perform_primary_image_update_from_media_root()
            self.display_message(request, msg)
        except Exception as err:
            messages.error(request, str(err))
    update_primary_image_object_action.allowed_permissions = ('view',)
    update_primary_image_object_action.label = "Update Image"
    update_primary_image_object_action.short_description = (
        'Update this Premier product\'s primary image from media directory'
    )
