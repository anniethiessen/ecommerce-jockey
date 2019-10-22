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
