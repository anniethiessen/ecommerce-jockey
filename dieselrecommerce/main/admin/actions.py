from django.contrib import messages

from core.admin.actions import BaseActions


class VendorActions(BaseActions):
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


class ItemActions(BaseActions):
    def create_items_class_action(self, request, queryset):
        msgs = []
        try:
            msgs = self.model.objects.create_products_from_premier_products()
        except Exception as err:
            msgs.append(self.model.get_class_error_msg(str(err)))
        self.display_messages(request, msgs, include_info=False)
    create_items_class_action.allowed_permissions = ('view',)
    create_items_class_action.label = 'Create items'
    create_items_class_action.short_description = (
        'Create items from relevant Premier products'
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
        'Create product if Premier product and Sema product exist'
    )
