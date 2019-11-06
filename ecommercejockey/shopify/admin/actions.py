from django.contrib import messages

from core.admin.actions import BaseActions, RelevancyActions


class ShopifyVendorActions(BaseActions):
    pass


class ShopifyTagActions(BaseActions):
    pass


class ShopifyCollectionRuleActions(BaseActions):
    pass


class ShopifyCollectionActions(RelevancyActions):
    pass


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


class ShopifyImageActions(BaseActions):
    pass


class ShopifyOptionActions(BaseActions):
    pass


class ShopifyVariantActions(BaseActions):
    pass
