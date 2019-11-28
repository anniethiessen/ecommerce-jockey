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


def get_changelist_view_link(instance, link_name, query=None):
    url = reverse(
        f'admin:{instance._meta.app_label}_'
        f'{instance._meta.object_name.lower()}_changelist'
    )

    if query:
        url = f'{url}?{query}'

    return mark_safe(f'<a href="{url}">{link_name}</a>')


def get_image_preview(image_link, width="150"):
    try:
        return mark_safe(
            f'<img src="{image_link}" width={width} />'
        )
    except Exception:
        raise


def get_images_preview(image_links, width="150"):
    try:
        images_html = ''
        for image_link in image_links:
            images_html += f'<img src="{image_link}" width={width} />'
        return mark_safe(
            f'<div>{images_html}</div>'
        )
    except Exception:
        raise
