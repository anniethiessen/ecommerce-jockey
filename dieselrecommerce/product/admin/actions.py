from django.contrib import messages


class PremierAPIActions(object):
    def update_inventory_action(self, request, queryset):
        try:
            token = self.model.retrieve_premier_api_token()
        except Exception as err:
            messages.error(request, f"Token error: {err}")
            return

        try:
            msgs = queryset.update_inventory_from_premier_api(token)
            for msg in msgs:
                if msg[:7] == 'Success':
                    messages.success(request, msg)
                else:
                    messages.error(request, msg)
        except Exception as err:
            messages.error(request, str(err))

        # for msg in msgs:
        #     if msg[:7] == 'Success':
        #         messages.success(request, msg)
        #         continue
        #     else:
        #         messages.error(request, msg)
        #         continue

        # for instance in queryset:
        #     try:
        #         msg = instance.update_inventory_from_premier_api(token)
        #         if msg[:7] == 'Success':
        #             messages.success(request, msg)
        #         else:
        #             messages.error(request, msg)
        #     except Exception as err:
        #         messages.error(request, str(err))
    update_inventory_action.allowed_permissions = ('view',)
    update_inventory_action.short_description = (
        'Update selected %(verbose_name_plural)s inventory from Premier API'
    )
