from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import (
    ShopifyCollection,
    ShopifyCollectionCalculator,
    ShopifyProductCalculator,
    ShopifyProduct,
    ShopifyVariant
)


@receiver(post_save, sender=ShopifyProduct)
def create_full_shopify_product(sender, instance, created, **kwargs):
    if created:
        variant = ShopifyVariant.objects.create(product=instance)
        ShopifyProductCalculator.objects.create(product=instance)


@receiver(post_save, sender=ShopifyCollection)
def create_full_shopify_collection(sender, instance, created, **kwargs):
    if created:
        ShopifyCollectionCalculator.objects.create(collection=instance)
