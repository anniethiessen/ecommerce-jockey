from django.contrib.contenttypes.models import ContentType
from django.db.models import (
    Model,
    ForeignKey,
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
        blank=True,
        on_delete=SET_NULL,
        null=True,
        related_name='vendor'
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
    def relevancy_warnings(self):
        msgs = []

        if (self.premier_manufacturer
                and self.premier_manufacturer.relevancy_warnings):
            msgs.append(
                f"PREMIER: {self.premier_manufacturer.relevancy_warnings}"
            )

        if (self.sema_brand
                and self.sema_brand.relevancy_warnings):
            msgs.append(f"SEMA: {self.sema_brand.relevancy_warnings}")

        if (self.shopify_vendor
                and self.shopify_vendor.warnings):
            msgs.append(f"SHOPIFY: {self.shopify_vendor.warnings}")

        return ', '.join(msgs)
    relevancy_warnings.fget.short_description = 'Warnings'

    @property
    def relevancy_errors(self):
        msgs = []

        if self.is_relevant:
            if self.premier_manufacturer and not self.premier_manufacturer.is_relevant:
                msgs.append('Premier manufacturer not relevant')

            if self.sema_brand and not self.sema_brand.is_relevant:
                error = 'SEMA brand not relevant'
                msgs.append(error)

            if not self.premier_manufacturer:
                error = 'Missing Premier manufacturer'
                msgs.append(error)

            if not self.sema_brand:
                error = 'Missing SEMA brand'
                msgs.append(error)

            if not self.shopify_vendor:
                error = 'Missing Shopify vendor'
                msgs.append(error)

        if (self.premier_manufacturer
                and self.premier_manufacturer.relevancy_errors):
            msgs.append(
                f"PREMIER: {self.premier_manufacturer.relevancy_errors}"
            )

        if (self.sema_brand
                and self.sema_brand.relevancy_errors):
            msgs.append(f"SEMA: {self.sema_brand.relevancy_errors}")

        if (self.shopify_vendor
                and self.shopify_vendor.errors):
            msgs.append(f"SHOPIFY: {self.shopify_vendor.errors}")

        return ', '.join(msgs)
    relevancy_errors.fget.short_description = 'Errors'
    # </editor-fold>

    objects = VendorManager()

    def __str__(self):
        return f'{self.premier_manufacturer} :: {self.sema_brand}'


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
    def relevancy_warnings(self):
        msgs = []

        if (self.sema_root_category
                and self.sema_root_category.relevancy_warnings):
            msgs.append(
                f"SEMA ROOT: {self.sema_root_category.relevancy_warnings}"
            )

        if (self.sema_branch_category
                and self.sema_branch_category.relevancy_warnings):
            msgs.append(
                f"SEMA BRANCH: {self.sema_branch_category.relevancy_warnings}"
            )

        if (self.sema_leaf_category
                and self.sema_leaf_category.relevancy_warnings):
            msgs.append(
                f"SEMA LEAF: {self.sema_leaf_category.relevancy_warnings}"
            )

        if (self.shopify_root_collection
                and self.shopify_root_collection.warnings):
            msgs.append(
                f"SHOPIFY ROOT: {self.shopify_root_collection.warnings}"
            )

        if (self.shopify_branch_collection
                and self.shopify_branch_collection.warnings):
            msgs.append(
                f"SHOPIFY BRANCH: {self.shopify_branch_collection.warnings}"
            )

        if (self.shopify_leaf_collection
                and self.shopify_leaf_collection.warnings):
            msgs.append(
                f"SHOPIFY LEAF: {self.shopify_leaf_collection.warnings}"
            )

        return ', '.join(msgs)
    relevancy_warnings.fget.short_description = 'Warnings'

    @property
    def relevancy_errors(self):
        msgs = []

        if self.is_relevant:
            if self.sema_root_category and not self.sema_root_category.is_relevant:
                error = 'SEMA root category not relevant'
                msgs.append(error)

            if self.sema_branch_category and not self.sema_branch_category.is_relevant:
                error = 'SEMA branch category not relevant'
                msgs.append(error)

            if self.sema_leaf_category and not self.sema_leaf_category.is_relevant:
                error = 'SEMA leaf category not relevant'
                msgs.append(error)

            if not self.sema_root_category:
                error = 'Missing SEMA root category'
                msgs.append(error)

            if not self.sema_branch_category:
                error = 'Missing SEMA branch category'
                msgs.append(error)

            if not self.sema_leaf_category:
                error = 'Missing SEMA leaf category'
                msgs.append(error)

            if not self.shopify_root_collection:
                error = 'Missing Shopify root collection'
                msgs.append(error)

            if not self.shopify_branch_collection:
                error = 'Missing Shopify branch collection'
                msgs.append(error)

            if not self.shopify_leaf_collection:
                error = 'Missing Shopify leaf collection'
                msgs.append(error)

        if (self.sema_root_category
                and self.sema_root_category.relevancy_errors):
            msgs.append(
                f"SEMA ROOT: {self.sema_root_category.relevancy_errors}"
            )

        if (self.sema_branch_category
                and self.sema_branch_category.relevancy_errors):
            msgs.append(
                f"SEMA BRANCH: {self.sema_branch_category.relevancy_errors}"
            )

        if (self.sema_leaf_category
                and self.sema_leaf_category.relevancy_errors):
            msgs.append(
                f"SEMA LEAF: {self.sema_leaf_category.relevancy_errors}"
            )

        if (self.shopify_root_collection
                and self.shopify_root_collection.errors):
            msgs.append(
                f"SHOPIFY ROOT: {self.shopify_root_collection.errors}"
            )

        if (self.shopify_branch_collection
                and self.shopify_branch_collection.errors):
            msgs.append(
                f"SHOPIFY BRANCH: {self.shopify_branch_collection.errors}"
            )

        if (self.shopify_leaf_collection
                and self.shopify_leaf_collection.errors):
            msgs.append(
                f"SHOPIFY LEAF: {self.shopify_leaf_collection.errors}"
            )

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
    def relevancy_warnings(self):
        msgs = []

        if (self.premier_product
                and self.premier_product.relevancy_warnings):
            msgs.append(
                f"PREMIER: {self.premier_product.relevancy_warnings}"
            )

        if (self.sema_product
                and self.sema_product.relevancy_warnings):
            msgs.append(f"SEMA: {self.sema_product.relevancy_warnings}")

        if (self.shopify_product
                and self.shopify_product.warnings):
            msgs.append(f"SHOPIFY: {self.shopify_product.warnings}")

        return ', '.join(msgs)
    relevancy_warnings.fget.short_description = 'Warnings'

    @property
    def relevancy_errors(self):
        msgs = []
        if self.is_relevant:
            if self.premier_product and not self.premier_product.is_relevant:
                msgs.append('Premier product not relevant')

            if self.sema_product and not self.sema_product.is_relevant:
                error = 'SEMA product not relevant'
                msgs.append(error)

            if not self.premier_product:
                error = 'Missing Premier product'
                msgs.append(error)

            if not self.sema_product:
                error = 'Missing SEMA product'
                msgs.append(error)

            if not self.shopify_product:
                error = 'Missing Shopify product'
                msgs.append(error)

        if (self.premier_product
                and self.premier_product.relevancy_errors):
            msgs.append(
                f"PREMIER: {self.premier_product.relevancy_errors}"
            )

        if (self.sema_product
                and self.sema_product.relevancy_errors):
            msgs.append(f"SEMA: {self.sema_product.relevancy_errors}")

        if (self.shopify_product
                and self.shopify_product.errors):
            msgs.append(f"SHOPIFY: {self.shopify_product.errors}")

        return ', '.join(msgs)
    relevancy_errors.fget.short_description = 'Errors'
    # </editor-fold>

    objects = ItemManager()

    def __str__(self):
        return ' :: '.join(
            [
                str(product) for product
                in [self.premier_product, self.sema_product]
                if product
            ]
        )
