from django.db.models import (
    Model,
    CharField,
    ForeignKey,
    OneToOneField,
    TextField,
    CASCADE,
    SET_NULL
)

from core.models import RelevancyBaseModel
from premier.models import (
    PremierManufacturer,
    PremierProduct
)
from sema.models import (
    SemaBrand,
    SemaProduct
)
from .managers import (
    ItemManager,
    VendorManager
)


class Vendor(RelevancyBaseModel):
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
    slug = CharField(
        max_length=20,
        unique=True
    )

    objects = VendorManager()

    def __str__(self):
        return f'{self.premier_manufacturer.name} :: {self.sema_brand.name}'


class Item(RelevancyBaseModel):
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
    notes = TextField(
        blank=True
    )

    objects = ItemManager()

    def __str__(self):
        s = str(self.pk)
        if self.premier_product:
            s = ' :: '.join([s, str(self.premier_product)])
        if self.sema_product:
            s = ' :: '.join([s, str(self.sema_product)])
        return s
