from django.contrib.admin import FieldListFilter
from django.urls import reverse
from django.utils.safestring import mark_safe


def get_custom_filter_title(title):
    # noinspection PyAbstractClass
    class Wrapper(FieldListFilter):
        def __new__(cls, *args, **kwargs):
            instance = FieldListFilter.create(*args, **kwargs)
            instance.title = title
            return instance
    return Wrapper


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


def get_image_preview(image_link, width="150"):
    return mark_safe(
        f'<img src="{image_link}" width={width} />'
    )
