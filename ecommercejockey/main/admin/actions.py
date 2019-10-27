from django.contrib import messages

from core.admin.actions import RelevancyActions


class VendorActions(RelevancyActions):
    def check_unlinked_vendors_class_action(self, request, queryset):
        try:
            msgs = self.model.objects.check_unlinked_vendors()
            self.display_messages(request, msgs, include_info=False)
        except Exception as err:
            messages.error(request, str(err))
    check_unlinked_vendors_class_action.allowed_permissions = ('view',)
    check_unlinked_vendors_class_action.label = 'Check for vendors'
    check_unlinked_vendors_class_action.short_description = (
        'Check if any unlinked Premier manufacturers and SEMA brands exist')


class ItemActions(RelevancyActions):
    def create_items_class_action(self, request, queryset):
        msgs = []
        try:
            msgs = self.model.objects.create_from_relevant()
        except Exception as err:
            msgs.append(self.model.get_class_error_msg(str(err)))
        self.display_messages(request, msgs, include_info=False)
    create_items_class_action.allowed_permissions = ('view',)
    create_items_class_action.label = 'Create items'
    create_items_class_action.short_description = (
        'Create items from relevant Premier and SEMA products'
    )

    def link_products_class_action(self, request, queryset):
        msgs = []
        try:
            msgs = self.model.objects.link_products()
            self.display_messages(request, msgs, include_info=False)
        except Exception as err:
            messages.error(request, str(err))
    link_products_class_action.allowed_permissions = ('view',)
    link_products_class_action.label = 'Link products'
    link_products_class_action.short_description = (
        'Link missing Premier and SEMA products by part numbers'
    )
