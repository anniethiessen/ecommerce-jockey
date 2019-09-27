from django.urls import reverse
from django.utils.safestring import mark_safe


def get_change_view_link(instance, link_name, query=None):
    url = reverse(
        (
            f'admin:{instance._meta.app_label}_'
            f'{instance._meta.object_name.lower()}_change'
        ),
        args=(instance.pk,)
    )

    if query:
        url = f'{url}?{query}'

    return mark_safe(f'<a href="{url}">{link_name}</a>')
