from django.contrib import messages

from core.admin.actions import RelevancyActions


class CreateAndLinkActions(RelevancyActions):
    def create_and_link_items_class_action(self, request, queryset):
        msgs = []
        try:
            msgs = self.model.objects.create_and_link()
        except Exception as err:
            msgs.append(self.model.get_class_error_msg(str(err)))
        self.display_messages(request, msgs, include_info=False)

    create_and_link_items_class_action.allowed_permissions = ('view',)
    create_and_link_items_class_action.label = 'Create/Link items'
    create_and_link_items_class_action.short_description = (
        'Create and/or link items from related items'
    )


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
        'Check if any unlinked Premier manufacturers, SEMA brands, '
        'or Shopify vendors exist'
    )


class ItemActions(CreateAndLinkActions):
    def mark_as_relevant_queryset_action(self, request, queryset):
        msgs = []
        for obj in queryset:
            try:
                if obj.is_relevant:
                    msgs.append(
                        obj.get_instance_up_to_date_msg(
                            message="Already relevant"
                        )
                    )
                else:
                    obj.is_relevant = True
                    obj.save()
                    msgs.append(
                        obj.get_update_success_msg(
                            message="Updated to relevant"
                        )
                    )

                if obj.premier_product.is_relevant:
                    msgs.append(
                        obj.premier_product.get_instance_up_to_date_msg(
                            message="Already relevant"
                        )
                    )
                else:
                    obj.premier_product.is_relevant = True
                    obj.premier_product.save()
                    msgs.append(
                        obj.premier_product.get_update_success_msg(
                            message="Updated to relevant"
                        )
                    )

                if obj.sema_product:
                    if obj.sema_product.is_relevant:
                        msgs.append(
                            obj.sema_product.get_instance_up_to_date_msg(
                                message="Already relevant"
                            )
                        )
                    else:
                        obj.sema_product.is_relevant = True
                        obj.sema_product.save()
                        msgs.append(
                            obj.sema_product.get_update_success_msg(
                                message="Updated to relevant"
                            )
                        )
            except Exception as err:
                msgs.append(
                    obj.get_instance_error_msg(str(err))
                )
        self.display_messages(request, msgs, include_info=False)
    mark_as_relevant_queryset_action.allowed_permissions = ('view',)
    mark_as_relevant_queryset_action.short_description = (
        'Mark selected %(verbose_name_plural)s and related objects as relevant'
    )

    def mark_as_irrelevant_queryset_action(self, request, queryset):
        msgs = []
        for obj in queryset:
            try:
                if not obj.is_relevant:
                    msgs.append(
                        obj.get_instance_up_to_date_msg(
                            message="Already NOT relevant"
                        )
                    )
                else:
                    obj.is_relevant = False
                    obj.save()
                    msgs.append(
                        obj.get_update_success_msg(
                            message="Updated to NOT relevant"
                        )
                    )

                if not obj.premier_product.is_relevant:
                    msgs.append(
                        obj.premier_product.get_instance_up_to_date_msg(
                            message="Already NOT relevant"
                        )
                    )
                else:
                    obj.premier_product.is_relevant = False
                    obj.premier_product.save()
                    msgs.append(
                        obj.premier_product.get_update_success_msg(
                            message="Updated to NOT relevant"
                        )
                    )

                if obj.sema_product:
                    if not obj.sema_product.is_relevant:
                        msgs.append(
                            obj.sema_product.get_instance_up_to_date_msg(
                                message="Already NOT relevant"
                            )
                        )
                    else:
                        obj.sema_product.is_relevant = False
                        obj.sema_product.save()
                        msgs.append(
                            obj.sema_product.get_update_success_msg(
                                message="Updated to NOT relevant"
                            )
                        )
            except Exception as err:
                msgs.append(
                    obj.get_instance_error_msg(str(err))
                )
        self.display_messages(request, msgs, include_info=False)
    mark_as_irrelevant_queryset_action.allowed_permissions = ('view',)
    mark_as_irrelevant_queryset_action.short_description = (
        'Mark selected %(verbose_name_plural)s '
        'and related objects as NOT relevant'
    )

    def create_shopify_products_queryset_action(self, request, queryset):
        try:
            msgs = queryset.create_shopify_products()
            self.display_messages(request, msgs, include_info=False)
        except Exception as err:
            messages.error(request, str(err))
    create_shopify_products_queryset_action.allowed_permissions = ('view',)
    create_shopify_products_queryset_action.short_description = (
        'Create Shopify products for selected %(verbose_name_plural)s'
    )

    def create_shopify_products_object_action(self, request, obj):
        try:
            queryset = self.model.objects.filter(pk=obj.pk)
            msgs = queryset.create_shopify_products()
            self.display_messages(request, msgs, include_info=False)
        except Exception as err:
            messages.error(request, str(err))
    create_shopify_products_object_action.allowed_permissions = ('view',)
    create_shopify_products_object_action.label = 'Create Shopify Product'
    create_shopify_products_object_action.short_description = (
        'Create Shopify product for item'
    )


class CategoryPathActions(CreateAndLinkActions):
    def create_shopify_collections_queryset_action(self, request, queryset):
        try:
            msgs = queryset.create_shopify_collections()
            self.display_messages(request, msgs, include_info=False)
        except Exception as err:
            messages.error(request, str(err))
    create_shopify_collections_queryset_action.allowed_permissions = ('view',)
    create_shopify_collections_queryset_action.short_description = (
        'Create Shopify collections for selected %(verbose_name_plural)s'
    )

    def create_shopify_collections_object_action(self, request, obj):
        try:
            queryset = self.model.objects.filter(pk=obj.pk)
            msgs = queryset.create_shopify_collections()
            self.display_messages(request, msgs, include_info=False)
        except Exception as err:
            messages.error(request, str(err))
    create_shopify_collections_object_action.allowed_permissions = ('view',)
    create_shopify_collections_object_action.label = 'Create Shopify Collections'
    create_shopify_collections_object_action.short_description = (
        'Create Shopify collection for item'
    )
