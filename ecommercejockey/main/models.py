from django.db.models import (
    Model,
    CharField,
    ForeignKey,
    OneToOneField,
    CASCADE,
    SET_NULL
)

from core.models import (
    NotesBaseModel,
    RelevancyBaseModel
)
from premier.models import (
    PremierManufacturer,
    PremierProduct
)
from sema.models import (
    SemaBrand,
    SemaProduct
)
from shopify.models import (
    ShopifyVendor,
    ShopifyProduct
)
from .managers import (
    ItemManager,
    VendorManager
)


class Vendor(RelevancyBaseModel, NotesBaseModel):
    premier_manufacturer = OneToOneField(
        PremierManufacturer,
        on_delete=CASCADE,
        related_name='vendor'
    )
    sema_brand = OneToOneField(
        SemaBrand,
        on_delete=CASCADE,
        verbose_name='SEMA brand',
        related_name='vendor'
    )
    shopify_vendor = OneToOneField(
        ShopifyVendor,
        on_delete=CASCADE,
        related_name='vendor'
    )
    slug = CharField(
        max_length=20,
        unique=True
    )

    @property
    def may_be_relevant(self):
        return bool(
            self.premier_manufacturer
            and self.premier_manufacturer.is_relevant
            and self.sema_brand and self.sema_brand.is_relevant
            and self.shopify_vendor
            and self.relevancy_errors == ''
        )

    @property
    def relevancy_errors(self):
        msgs = []
        if not self.premier_manufacturer:
            msgs.append('Missing Premier manufacturer')

        if not self.sema_brand:
            msgs.append('Missing SEMA brand')

        if not self.shopify_vendor:
            msgs.append('Missing Shopify vendor')

        if (self.premier_manufacturer
                and self.premier_manufacturer.relevancy_errors):
            msgs.append(
                f"PREMIER: {self.premier_manufacturer.relevancy_errors}"
            )

        if (self.sema_brand
                and self.sema_brand.relevancy_errors):
            msgs.append(f"SEMA: {self.sema_brand.relevancy_errors}")
        return ', '.join(msgs)
    relevancy_errors.fget.short_description = 'Errors'

    objects = VendorManager()

    def __str__(self):
        return self.slug


class Item(RelevancyBaseModel, NotesBaseModel):
    premier_product = OneToOneField(
        PremierProduct,
        blank=True,
        null=True,
        related_name='item',
        on_delete=SET_NULL
    )
    sema_product = ForeignKey(
        SemaProduct,
        blank=True,
        null=True,
        related_name='items',
        on_delete=SET_NULL,
        verbose_name='SEMA product'
    )
    shopify_product = OneToOneField(
        ShopifyProduct,
        blank=True,
        null=True,
        related_name='item',
        on_delete=SET_NULL
    )

    @property
    def may_be_relevant(self):
        return bool(
            self.premier_product and self.premier_product.is_relevant
            and self.sema_product and self.sema_product.is_relevant
            and self.shopify_product
            and self.relevancy_errors == ''
        )

    @property
    def relevancy_errors(self):
        msgs = []
        if not self.premier_product:
            msgs.append('Missing Premier product')

        if not self.sema_product:
            msgs.append('Missing SEMA product')

        if not self.shopify_product:
            msgs.append('Missing Shopify product')

        if self.premier_product and self.premier_product.relevancy_errors:
            msgs.append(
                f"PREMIER: {self.premier_product.relevancy_errors}"
            )

        if self.sema_product and self.sema_product.relevancy_errors:
            msgs.append(f"SEMA: {self.sema_product.relevancy_errors}")
        return ', '.join(msgs)
    relevancy_errors.fget.short_description = 'Errors'

    objects = ItemManager()

    def __str__(self):
        s = str(self.pk)
        if self.premier_product:
            s = ' :: '.join([s, str(self.premier_product)])
        if self.sema_product:
            s = ' :: '.join([s, str(self.sema_product)])
        if self.shopify_product:
            s = ' :: '.join([s, str(self.shopify_product)])
        return s
