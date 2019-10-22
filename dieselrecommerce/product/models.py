from django.db.models import (
    Model,
    ForeignKey,
    OneToOneField,
    CASCADE,
    SET_NULL
)

from core.mixins import MessagesMixin
from premier.models import (
    PremierManufacturer,
    PremierProduct
)
from sema.models import (
    SemaBrand,
    SemaProduct
)
from .managers import (
    ProductManager,
    VendorManager
)


class Vendor(Model, MessagesMixin):
    premier_manufacturer = OneToOneField(
        PremierManufacturer,
        on_delete=CASCADE
    )
    sema_brand = OneToOneField(
        SemaBrand,
        on_delete=CASCADE,
        verbose_name='SEMA brand'
    )

    objects = VendorManager()

    def __str__(self):
        return f'{self.premier_manufacturer.name} :: {self.sema_brand.name}'


class Product(Model, MessagesMixin):
    premier_product = OneToOneField(
        PremierProduct,
        blank=True,
        null=True,
        related_name='product',
        on_delete=SET_NULL
    )
    sema_product = ForeignKey(
        SemaProduct,
        blank=True,
        null=True,
        related_name='products',
        on_delete=SET_NULL,
        verbose_name='SEMA product'
    )

    objects = ProductManager()

    def __str__(self):
        s = str(self.pk)
        if self.premier_product:
            s = ' :: '.join([s, str(self.premier_product)])
        if self.sema_product:
            s = ' :: '.join([s, str(self.sema_product)])
        return s
