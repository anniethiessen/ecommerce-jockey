from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import ShopifyCalculator, ShopifyProduct, ShopifyVariant


@receiver(post_save, sender=ShopifyProduct)
def create_shopify_full_product(sender, instance, created, **kwargs):
    if created:
        variant = ShopifyVariant.objects.create(product=instance)
        ShopifyCalculator.objects.create(product=instance)
        instance.perform_calculated_fields_update()
        variant.perform_calculated_fields_update()
