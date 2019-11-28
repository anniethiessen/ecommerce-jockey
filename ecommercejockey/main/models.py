from django.contrib.contenttypes.models import ContentType
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
    RelevancyBaseModel as RelevancyModel
)
from .managers import (
    ItemManager,
    CategoryPathManager,
    VendorManager
)


class RelevancyBaseModel(RelevancyModel):
    relevancy_exceptions = CharField(
        blank=True,
        max_length=255
    )

    class Meta:
        abstract = True


class Vendor(RelevancyBaseModel, NotesBaseModel):
    from premier.models import PremierManufacturer
    from sema.models import SemaBrand
    from shopify.models import ShopifyVendor

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

    # <editor-fold desc="relevancy properties ...">
    @property
    def may_be_relevant(self):
        return bool(
            self.premier_manufacturer
            and self.premier_manufacturer.is_relevant
            and self.sema_brand and self.sema_brand.is_relevant
        )

    @property
    def relevancy_errors(self):
        msgs = []

        if self.is_relevant:
            if not self.premier_manufacturer:
                error = 'Missing Premier manufacturer'
                msgs.append(error)
            if not self.sema_brand:
                error = 'Missing SEMA brand'
                msgs.append(error)

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
    # </editor-fold>

    objects = VendorManager()

    def __str__(self):
        return self.slug


class CategoryPath(RelevancyBaseModel, NotesBaseModel):
    from sema.models import SemaCategory
    from shopify.models import ShopifyCollection

    sema_root_category = ForeignKey(
        SemaCategory,
        on_delete=CASCADE,
        related_name='root_category_paths'
    )
    shopify_root_collection = ForeignKey(
        ShopifyCollection,
        blank=True,
        null=True,
        on_delete=SET_NULL,
        related_name='root_category_paths'
    )
    sema_branch_category = ForeignKey(
        SemaCategory,
        on_delete=CASCADE,
        related_name='branch_category_paths'
    )
    shopify_branch_collection = ForeignKey(
        ShopifyCollection,
        blank=True,
        null=True,
        on_delete=SET_NULL,
        related_name='branch_category_paths'
    )
    sema_leaf_category = ForeignKey(
        SemaCategory,
        on_delete=CASCADE,
        related_name='leaf_category_paths'
    )
    shopify_leaf_collection = ForeignKey(
        ShopifyCollection,
        blank=True,
        null=True,
        on_delete=SET_NULL,
        related_name='leaf_category_paths'
    )

    # <editor-fold desc="relevancy properties ...">
    @property
    def may_be_relevant(self):
        return bool(
            self.sema_root_category.is_relevant
            and self.sema_branch_category.is_relevant
            and self.sema_leaf_category.is_relevant
        )

    @property
    def relevancy_errors(self):
        msgs = []
        if self.is_relevant:
            pass
        return ', '.join(msgs)
    relevancy_errors.fget.short_description = 'Errors'
    # </editor-fold>

    objects = CategoryPathManager()

    class Meta:
        unique_together = [
            'sema_root_category',
            'sema_branch_category',
            'sema_leaf_category'
        ]

    def __str__(self):
        return (
            f'{self.sema_root_category} '
            f':: {self.sema_branch_category} '
            f':: {self.sema_leaf_category}')


class Item(RelevancyBaseModel, NotesBaseModel):
    from premier.models import PremierProduct
    from sema.models import SemaProduct
    from shopify.models import ShopifyProduct

    premier_product = OneToOneField(
        PremierProduct,
        blank=True,
        null=True,
        related_name='item',
        on_delete=SET_NULL
    )
    sema_product = OneToOneField(
        SemaProduct,
        blank=True,
        null=True,
        related_name='item',
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

    # <editor-fold desc="relevancy properties ...">
    @property
    def may_be_relevant(self):
        return bool(
            self.premier_product and self.premier_product.is_relevant
            and self.sema_product and self.sema_product.is_relevant
        )

    @property
    def relevancy_errors(self):
        msgs = []
        if self.is_relevant:
            if self.premier_product:
                if not self.premier_product.is_relevant:
                    msgs.append('Premier product not relevant')
                if self.premier_product.relevancy_errors:
                    error = f"PREMIER: {self.premier_product.relevancy_errors}"
                    msgs.append(error)
            else:
                error = 'Missing Premier product'
                msgs.append(error)
            if self.sema_product:
                if not self.sema_product.is_relevant:
                    error = 'SEMA product not relevant'
                    msgs.append(error)
                if self.sema_product.relevancy_errors:
                    error = f"SEMA: {self.sema_product.relevancy_errors}"
                    msgs.append(error)
            else:
                error = 'Missing SEMA product'
                msgs.append(error)
        else:
            if self.premier_product.is_relevant:
                error = 'Premier product relevant'
                msgs.append(error)
            if self.sema_product and self.sema_product.is_relevant:
                error = 'SEMA product relevant'
                msgs.append(error)
        return ', '.join(msgs)
    relevancy_errors.fget.short_description = 'Errors'
    # </editor-fold>

    objects = ItemManager()

    def __str__(self):
        return str(self.premier_product)
