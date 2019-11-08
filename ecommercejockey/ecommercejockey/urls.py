from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from main.views import ProductOrderCreateView


urlpatterns = [
    path(
        'admin/',
        admin.site.urls
    ),
    path(
        'webhooks/products/order/',
        ProductOrderCreateView.as_view()
    )
]


if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATIC_ROOT
    )

    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
