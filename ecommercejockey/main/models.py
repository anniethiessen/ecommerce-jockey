from django.contrib.contenttypes.models import ContentType
from django.db.models import (
    Model,
    CharField,
    ForeignKey,
    ManyToManyField,
    OneToOneField,
    CASCADE,
    SET_NULL
)

from core.models import (
    NotesBaseModel,
    RelevancyBaseModel
)
from .managers import (
    ItemManager,
    CategoryPathManager,
    VendorManager
)


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
    from premier.models import PremierProduct
    from sema.models import SemaProduct
    from shopify.models import ShopifyProduct

    premier_product = OneToOneField(
        PremierProduct,
        related_name='item',
        on_delete=CASCADE
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
            self.premier_product.may_be_relevant
            and self.sema_product
        )

    @property
    def relevancy_errors(self):
        msgs = []
        if self.is_relevant:
            if self.premier_product:
                if not self.premier_product.is_relevant:
                    msgs.append('Premier product not relevant')
                if self.premier_product.relevancy_errors:
                    msgs.append(
                        f"PREMIER: {self.premier_product.relevancy_errors}"
                    )
            else:
                msgs.append('Missing Premier product')

            if self.sema_product:
                if not self.sema_product.is_relevant:
                    msgs.append('SEMA product not relevant')
                if self.sema_product.relevancy_errors:
                    msgs.append(f"SEMA: {self.sema_product.relevancy_errors}")
            else:
                msgs.append('Missing SEMA product')
        else:
            if self.premier_product.is_relevant:
                msgs.append('Premier product relevant')
            if self.sema_product and self.sema_product.is_relevant:
                msgs.append('SEMA product relevant')
        return ', '.join(msgs)
    relevancy_errors.fget.short_description = 'Errors'

    objects = ItemManager()

    def __str__(self):
        return str(self.premier_product)


class CategoryPath(RelevancyBaseModel, NotesBaseModel):
    from sema.models import SemaCategory
    from shopify.models import ShopifyCollection

    sema_root_category = ForeignKey(
        SemaCategory,
        on_delete=CASCADE,
        related_name='root_category_paths'
    )
    sema_branch_category = ForeignKey(
        SemaCategory,
        on_delete=CASCADE,
        related_name='branch_category_paths'
    )
    sema_leaf_category = ForeignKey(
        SemaCategory,
        on_delete=CASCADE,
        related_name='leaf_category_paths'
    )
    shopify_collections = ManyToManyField(
        ShopifyCollection,
        related_name='category_paths'
    )

    @property
    def shopify_collection_count(self):
        return self.shopify_collections.count()

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
            if not self.sema_root_category.is_relevant:
                msgs.append('Root category not relevant')
            if not self.sema_branch_category.is_relevant:
                msgs.append('Branch category not relevant')
            if not self.sema_leaf_category.is_relevant:
                msgs.append('Leaf category not relevant')
        return ', '.join(msgs)
    relevancy_errors.fget.short_description = 'Errors'

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
