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


class RelevancyActions(BaseActions):
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
            except Exception as err:
                msgs.append(
                    obj.get_instance_error_msg(str(err))
                )
        self.display_messages(request, msgs, include_info=False)
    mark_as_relevant_queryset_action.allowed_permissions = ('view',)
    mark_as_relevant_queryset_action.short_description = (
        'Mark selected %(verbose_name_plural)s as relevant'
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
            except Exception as err:
                msgs.append(
                    obj.get_instance_error_msg(str(err))
                )
        self.display_messages(request, msgs, include_info=False)
    mark_as_irrelevant_queryset_action.allowed_permissions = ('view',)
    mark_as_irrelevant_queryset_action.short_description = (
        'Mark selected %(verbose_name_plural)s as NOT relevant'
    )
