from django.db.models.signals import post_save
from django.dispatch import receiver

from shopify.models import ShopifyProduct
from .models import Item


@receiver(post_save, sender=Item)
def create_shopify_product(sender, instance, created, **kwargs):
    if created and not instance.shopify_product:
        if instance.premier_product:
            vendor = instance.premier_product.manufacturer.vendor.shopify_vendor
        elif instance.sema_product:
            vendor = instance.sema_product.dataset.brand.vendor.shopify_vendor
        else:
            vendor = None
        instance.shopify_product = ShopifyProduct.objects.create(vendor=vendor)
        instance.save()
