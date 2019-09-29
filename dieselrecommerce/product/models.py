from django.db.models import (
    Model,
    BooleanField,
    CharField,
    DecimalField,
    ForeignKey,
    IntegerField,
    PositiveIntegerField,
    PositiveSmallIntegerField,
    CASCADE
)

from .apis import (
    PremierProductMixin,
    SemaBrandMixin,
    SemaDatasetMixin,
    SemaProductMixin
)
from .managers import PremierProductManager


class PremierProduct(Model, PremierProductMixin):
    premier_part_number = CharField(
        max_length=20,
        unique=True,
        primary_key=True
    )
    vendor_part_number = CharField(
        max_length=20,
    )
    description = CharField(
        max_length=500
    )
    manufacturer = CharField(
        max_length=50
    )
    cost = DecimalField(
        decimal_places=2,
        max_digits=10
    )
    cost_cad = DecimalField(
        blank=True,
        decimal_places=2,
        help_text='API field',
        max_digits=10,
        null=True,
        verbose_name='cost CAD'
    )
    cost_usd = DecimalField(
        blank=True,
        decimal_places=2,
        help_text='API field',
        max_digits=10,
        null=True,
        verbose_name='cost USD'
    )
    jobber = DecimalField(
        decimal_places=2,
        max_digits=10
    )
    jobber_cad = DecimalField(
        blank=True,
        decimal_places=2,
        help_text='API field',
        max_digits=10,
        null=True,
        verbose_name='jobber CAD'
    )
    jobber_usd = DecimalField(
        blank=True,
        decimal_places=2,
        help_text='API field',
        max_digits=10,
        null=True,
        verbose_name='jobber USD'
    )
    msrp = DecimalField(
        decimal_places=2,
        max_digits=10,
        verbose_name='MSRP'
    )
    msrp_cad = DecimalField(
        blank=True,
        decimal_places=2,
        help_text='API field',
        max_digits=10,
        null=True,
        verbose_name='MSRP CAD'
    )
    msrp_usd = DecimalField(
        blank=True,
        decimal_places=2,
        help_text='API field',
        max_digits=10,
        null=True,
        verbose_name='MSRP USD'
    )
    map = DecimalField(
        decimal_places=2,
        max_digits=10,
        verbose_name='MAP'
    )
    map_cad = DecimalField(
        blank=True,
        decimal_places=2,
        help_text='API field',
        max_digits=10,
        null=True,
        verbose_name='MAP CAD'
    )
    map_usd = DecimalField(
        blank=True,
        decimal_places=2,
        help_text='API field',
        max_digits=10,
        null=True,
        verbose_name='MAP USD'
    )
    part_status = CharField(
        max_length=20
    )
    weight = DecimalField(
        blank=True,
        decimal_places=2,
        help_text='lbs',
        max_digits=10,
        null=True
    )
    length = DecimalField(
        blank=True,
        decimal_places=2,
        help_text='in',
        max_digits=10,
        null=True
    )
    width = DecimalField(
        blank=True,
        decimal_places=2,
        help_text='in',
        max_digits=10,
        null=True
    )
    height = DecimalField(
        blank=True,
        decimal_places=2,
        help_text='in',
        max_digits=10,
        null=True
    )
    upc = CharField(
        blank=True,
        max_length=50,
        verbose_name='UPC'
    )
    inventory_ab = IntegerField(
        blank=True,
        help_text='API field',
        null=True,
        verbose_name='Alberta inventory'
    )
    inventory_po = IntegerField(
        blank=True,
        help_text='API field',
        null=True,
        verbose_name='PO inventory'
    )
    inventory_ut = IntegerField(
        blank=True,
        help_text='API field',
        null=True,
        verbose_name='Utah inventory'
    )
    inventory_ky = IntegerField(
        blank=True,
        help_text='API field',
        null=True,
        verbose_name='Kentucky inventory'
    )
    inventory_tx = IntegerField(
        blank=True,
        help_text='API field',
        null=True,
        verbose_name='Texas inventory'
    )
    inventory_ca = IntegerField(
        blank=True,
        help_text='API field',
        null=True,
        verbose_name='California inventory'
    )
    inventory_wa = IntegerField(
        blank=True,
        help_text='API field',
        null=True,
        verbose_name='Washington inventory'
    )
    inventory_co = IntegerField(
        blank=True,
        help_text='API field',
        null=True,
        verbose_name='Colorado inventory'
    )

    objects = PremierProductManager()

    def __str__(self):
        return f'{self.premier_part_number} :: {self.manufacturer}'


class SemaYear(Model):
    year = PositiveSmallIntegerField(
        primary_key=True,
        unique=True
    )

    class Meta:
        verbose_name = 'SEMA year'

    def __str__(self):
        return str(self.year)


class SemaMake(Model):
    make_id = PositiveIntegerField(
        primary_key=True,
        unique=True
    )
    name = CharField(
        max_length=50,
    )

    class Meta:
        verbose_name = 'SEMA make'

    def __str__(self):
        return str(self.name)


class SemaModel(Model):
    model_id = PositiveIntegerField(
        primary_key=True,
        unique=True
    )
    base_vehicle_id = PositiveIntegerField(
        unique=True
    )
    name = CharField(
        max_length=50,
    )
    make = ForeignKey(
        SemaMake,
        on_delete=CASCADE
    )

    class Meta:
        verbose_name = 'SEMA model'

    def __str__(self):
        return f'{self.name} :: {self.make}'


class SemaSubmodel(Model):
    submodel_id = PositiveIntegerField(
        primary_key=True,
        unique=True
    )
    vehicle_id = PositiveIntegerField(
        unique=True
    )
    name = CharField(
        max_length=50,
    )
    model = ForeignKey(
        SemaModel,
        on_delete=CASCADE
    )

    class Meta:
        verbose_name = 'SEMA submodel'

    def __str__(self):
        return f'{self.name} :: {self.model}'


class SemaBrand(Model, SemaBrandMixin):
    brand_id = CharField(
        primary_key=True,
        max_length=10,
        unique=True
    )
    name = CharField(
        max_length=50,
    )

    class Meta:
        verbose_name = 'SEMA brand'

    @property
    def dataset_count(self):
        return self.sema_datasets.count()

    def __str__(self):
        return f'{self.brand_id} :: {self.name}'


class SemaDataset(Model, SemaDatasetMixin):
    dataset_id = PositiveIntegerField(
        primary_key=True,
        unique=True
    )
    name = CharField(
        max_length=50,
    )
    is_authorized = BooleanField(
        default=False,
        help_text='brand has given access to dataset'
    )
    brand = ForeignKey(
        SemaBrand,
        on_delete=CASCADE,
        related_name='sema_datasets'
    )

    class Meta:
        verbose_name = 'SEMA dataset'

    def __str__(self):
        return f'{self.dataset_id} :: {self.name}'


class SemaProduct(Model, SemaProductMixin):
    product_id = PositiveIntegerField(
        primary_key=True,
        unique=True
    )
    part_number = CharField(
        max_length=20
    )
    dataset = ForeignKey(
        SemaDataset,
        on_delete=CASCADE,
        related_name='sema_products',
    )

    class Meta:
        verbose_name = 'SEMA product'

    def __str__(self):
        return f'{self.product_id}'
