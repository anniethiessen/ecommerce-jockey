from django.apps import AppConfig


class ShopifyAppConfig(AppConfig):
    name = 'shopify'
    verbose_name = 'Shopify'

    def ready(self):
        # noinspection PyUnresolvedReferences
        from .signals import (
            create_full_shopify_collection,
            create_full_shopify_product
        )
