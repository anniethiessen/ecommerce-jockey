import json

from pygments import highlight
from pygments.lexers.web import JSONLexer
from pygments.formatters.html import HtmlFormatter

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


def get_changelist_view_link(model, link_name, query=None):
    url = reverse(
        f'admin:{model._meta.app_label}_'
        f'{model._meta.model_name.lower()}_changelist'
    )

    if query:
        url = f'{url}?{query}'

    return mark_safe(f'<a href="{url}">{link_name}</a>')


def get_image_preview(image_link, width=150):
    try:
        return mark_safe(f'<img src="{image_link}" width="{width}" />')
    except Exception:
        raise


def get_images_preview(image_links, width=50):
    try:
        html = ''
        for image_link in image_links:
            html += f'<div><img src="{image_link}" width="{width}" /></div>'
        return mark_safe(f'<div style="width:{width * 3}px;">{html}</div>')
    except Exception:
        raise


def get_json_preview(json_value):
    try:
        response = json.dumps(json.loads(json_value), indent=2)
        formatter = HtmlFormatter(style='colorful')
        response = highlight(response, JSONLexer(), formatter)
        style = f'<style>{formatter.get_style_defs()}</style><br>'
        return mark_safe(style + response)
    except Exception:
        raise


def get_html_preview(html):
    try:
        return mark_safe(html)
    except Exception:
        raise
