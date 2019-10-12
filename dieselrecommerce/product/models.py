from django.db.models import (
    Model,
    BooleanField,
    CharField,
    DecimalField,
    ForeignKey,
    IntegerField,
    OneToOneField,
    PositiveIntegerField,
    PositiveSmallIntegerField,
    TextField,
    CASCADE,
    SET_NULL,
    Q
)

from .apis import SemaApi
from .managers import (
    PremierProductManager,
    SemaBaseVehicleManager,
    SemaBrandManager,
    SemaCategoryManager,
    SemaDatasetManager,
    SemaMakeManager,
    SemaModelManager,
    SemaProductManager,
    SemaSubmodelManager,
    SemaYearManager,
    SemaVehicleManager
)
from .mixins import (
    ManufacturerMixin,
    MessagesMixin,
    PremierProductMixin,
    ProductMixin,
    SemaBaseVehicleMixin,
    SemaBrandMixin,
    SemaCategoryMixin,
    SemaDatasetMixin,
    SemaMakeMixin,
    SemaModelMixin,
    SemaProductMixin,
    SemaSubmodelMixin,
    SemaVehicleMixin
)


sema_api = SemaApi()


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


class SemaYear(Model, MessagesMixin):
    year = PositiveSmallIntegerField(
        primary_key=True,
        unique=True
    )
    is_authorized = BooleanField(
        default=False,
        help_text='brand has given access to dataset'
    )

    def get_data(self):
        return {
            'is_authorized': self.is_authorized
        }

    @classmethod
    def import_from_api(cls, brand_id=None, dataset_id=None, new_only=False):
        msgs = []

        if (brand_id or dataset_id) and new_only:
            msgs.append(
                cls.get_class_error_msg(
                    "New only import cannot be used with filters"
                )
            )
            return msgs

        data = sema_api.retrieve_years(brand_id, dataset_id)

        if not new_only:
            msgs += cls.unauthorize_from_api_data(data)

        for item in data:
            try:
                year = cls.objects.get(year=item)
                if not new_only:
                    msgs.append(year.update_from_api_data(item))
            except cls.DoesNotExist:
                msgs.append(cls.create_from_api_data(item))
            except Exception as err:
                msgs.append(cls.get_class_error_msg(f"{item}: {err}"))

        if not msgs:
            if new_only:
                msgs.append(cls.get_class_nothing_new_msg())
            else:
                msgs.append(cls.get_class_up_to_date_msg())
        return msgs

    @classmethod
    def unauthorize_from_api_data(cls, data, include_up_to_date=True):
        msgs = []
        unauthorized_years = cls.objects.filter(~Q(year__in=data))

        if include_up_to_date:
            for year in unauthorized_years.filter(is_authorized=False):
                msgs.append(year.get_instance_up_to_date_msg())

        for year in unauthorized_years.filter(is_authorized=True):
            previous = year.get_data()
            year.is_authorized = False
            year.save()
            year.refresh_from_db()
            new = year.get_data()
            msgs.append(year.get_update_success_msg(previous, new))

        return msgs

    @classmethod
    def create_from_api_data(cls, data):
        try:
            year = cls.objects.create(
                year=data,
                is_authorized=True
            )
            msg = year.get_create_success_msg()
        except Exception as err:
            msg = cls.get_class_error_msg(f"{data}: {err}")

        return msg

    def update_from_api_data(self, data, include_up_to_date=True):
        try:
            previous = self.get_data()
            self.is_authorized = True
            self.save()
            self.refresh_from_db()
            new = self.get_data()
            msg = self.get_update_success_msg(
                previous,
                new,
                include_up_to_date
            )
        except Exception as err:
            msg = self.get_instance_error_msg(f"{data}: {err}")

        return msg

    objects = SemaYearManager()

    class Meta:
        ordering = ['year']
        verbose_name = 'SEMA year'

    def __str__(self):
        return str(self.year)


class SemaMake(Model, SemaMakeMixin):
    make_id = PositiveIntegerField(
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

    objects = SemaMakeManager()

    class Meta:
        ordering = ['name']
        verbose_name = 'SEMA make'

    def __str__(self):
        return str(self.name)


class SemaModel(Model, SemaModelMixin):
    model_id = PositiveIntegerField(
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

    objects = SemaModelManager()

    class Meta:
        ordering = ['name']
        verbose_name = 'SEMA model'

    def __str__(self):
        return str(self.name)


class SemaSubmodel(Model, SemaSubmodelMixin):
    submodel_id = PositiveIntegerField(
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

    objects = SemaSubmodelManager()

    class Meta:
        ordering = ['name']
        verbose_name = 'SEMA submodel'

    def __str__(self):
        return str(self.name)


class SemaBaseVehicle(Model, SemaBaseVehicleMixin):
    base_vehicle_id = PositiveIntegerField(
        primary_key=True,
        unique=True
    )
    year = ForeignKey(
        SemaYear,
        on_delete=CASCADE,
        related_name='base_vehicles'
    )
    make = ForeignKey(
        SemaMake,
        on_delete=CASCADE,
        related_name='base_vehicles'
    )
    model = ForeignKey(
        SemaModel,
        on_delete=CASCADE,
        related_name='base_vehicles'
    )
    is_authorized = BooleanField(
        default=False,
        help_text='brand has given access to dataset'
    )

    objects = SemaBaseVehicleManager()

    class Meta:
        ordering = ['make', 'model', 'year']
        verbose_name = 'SEMA base vehicle'

    def __str__(self):
        return f'{self.year} :: {self.make} :: {self.model}'


class SemaVehicle(Model, SemaVehicleMixin):
    vehicle_id = PositiveIntegerField(
        primary_key=True,
        unique=True
    )
    base_vehicle = ForeignKey(
        SemaBaseVehicle,
        on_delete=CASCADE,
        related_name='vehicles'
    )
    submodel = ForeignKey(
        SemaSubmodel,
        on_delete=CASCADE,
        related_name='vehicles'
    )
    is_authorized = BooleanField(
        default=False,
        help_text='brand has given access to dataset'
    )

    objects = SemaVehicleManager()

    class Meta:
        ordering = ['base_vehicle', 'submodel']
        verbose_name = 'SEMA vehicle'

    def __str__(self):
        return f'{self.base_vehicle} :: {self.submodel}'


class SemaBrand(Model, SemaBrandMixin):
    brand_id = CharField(
        primary_key=True,
        max_length=10,
        unique=True
    )
    name = CharField(
        max_length=50,
    )
    is_authorized = BooleanField(
        default=False,
        help_text='brand has given access to dataset'
    )

    objects = SemaBrandManager()

    class Meta:
        ordering = ['name']
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

    objects = SemaDatasetManager()

    class Meta:
        ordering = ['name']
        verbose_name = 'SEMA dataset'

    def __str__(self):
        return f'{self.dataset_id} :: {self.name} :: {self.brand}'


class SemaCategory(Model, SemaCategoryMixin):
    category_id = PositiveIntegerField(
        primary_key=True,
        unique=True
    )
    name = CharField(
        max_length=50,
    )
    parent_category = ForeignKey(
        'self',
        blank=True,
        null=True,
        on_delete=SET_NULL,
        related_name='child_categories'
    )
    is_authorized = BooleanField(
        default=False,
        help_text='brand has given access to dataset'
    )

    objects = SemaCategoryManager()

    @property
    def child_category_count(self):
        return self.child_categories.all().count()

    class Meta:
        ordering = ['name']
        verbose_name = 'SEMA category'
        verbose_name_plural = 'SEMA categories'

    def __str__(self):
        if not self.parent_category:
            return self.name
        return f'{self.parent_category} :: {self.name}'


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
    html = TextField(
        blank=True,
        verbose_name='HTML'
    )
    is_authorized = BooleanField(
        default=False,
        help_text='brand has given access to dataset'
    )

    objects = SemaProductManager()

    class Meta:
        ordering = ['dataset', 'part_number']
        verbose_name = 'SEMA product'

    def __str__(self):
        return f'{self.product_id} :: {self.dataset}'


class Product(Model, ProductMixin):
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
        related_name='product',
        on_delete=SET_NULL,
        verbose_name='SEMA product'
    )

    def __str__(self):
        s = str(self.pk)
        if self.premier_product:
            s = ' :: '.join([s, str(self.premier_product)])
        if self.sema_product:
            s = ' :: '.join([s, str(self.sema_product)])
        return s


class Manufacturer(Model, ManufacturerMixin):
    premier_manufacturer = CharField(
        max_length=50,
        unique=True
    )
    sema_brand = CharField(
        max_length=50,
        unique=True,
        verbose_name='SEMA brand'
    )

    def __str__(self):
        s = str(self.pk)
        if self.premier_manufacturer:
            s = ' :: '.join([s, self.premier_manufacturer])
        if self.sema_brand:
            s = ' :: '.join([s, self.sema_brand])
        return s
