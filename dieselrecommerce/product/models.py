from django.db.models import (
    Model,
    BooleanField,
    CharField,
    DecimalField,
    ForeignKey,
    IntegerField,
    ManyToManyField,
    OneToOneField,
    PositiveIntegerField,
    PositiveSmallIntegerField,
    TextField,
    CASCADE,
    SET_NULL
)

from .managers import (
    sema_api,
    PremierProductManager,
    SemaBaseManager,
    SemaBaseVehicleManager,
    SemaBrandManager,
    SemaCategoryManager,
    SemaDatasetManager,
    SemaMakeManager,
    SemaMakeYearManager,
    SemaModelManager,
    SemaProductManager,
    SemaSubmodelManager,
    SemaYearManager,
    SemaVehicleManager
)
from .mixins import (
    ManufacturerMixin,
    MessagesMixin,
    ProductMixin
)


class PremierApiProductInventoryModel(Model, MessagesMixin):
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

    def clear_inventory_fields(self):
        self.inventory_ab = None
        self.inventory_po = None
        self.inventory_ut = None
        self.inventory_ky = None
        self.inventory_tx = None
        self.inventory_ca = None
        self.inventory_wa = None
        self.inventory_co = None
        self.save()

    @property
    def inventory_state(self):
        return {
            'AB': self.inventory_ab,
            'PO': self.inventory_po,
            'UT': self.inventory_ut,
            'KY': self.inventory_ky,
            'TX': self.inventory_tx,
            'CA': self.inventory_ca,
            'WA': self.inventory_wa,
            'CO': self.inventory_co
        }

    def update_inventory_from_api(self):
        if not self.premier_part_number:
            return self.get_instance_error_msg("Premier Part Number required")

        try:
            part_numbers = [self.premier_part_number]
            data = self._meta.model.objects.get_api_inventory_data(
                part_numbers
            )
            data = data[0]['inventory']
            update_fields = self._meta.model.objects.parse_api_inventory_data(
                data
            )
            return self.update_inventory_from_api_data(**update_fields)
        except Exception as err:
            return self.get_instance_error_msg(str(err))

    def update_inventory_from_api_data(self, include_up_to_date=True,
                                       **update_fields):
        try:
            prev = self.inventory_state
            self.clear_inventory_fields()
            for attr, value in update_fields.items():
                if not getattr(self, attr) == value:
                    setattr(self, attr, value)
                    self.save()
            self.refresh_from_db()
            new = self.inventory_state
            msg = self.get_update_success_msg(prev, new, include_up_to_date)
        except Exception as err:
            msg = self.get_instance_error_msg(f"{update_fields}, {err}")
        return msg

    class Meta:
        abstract = True


class PremierApiProductPricingModel(Model, MessagesMixin):
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

    def clear_pricing_fields(self):
        self.cost_cad = None
        self.cost_usd = None
        self.jobber_cad = None
        self.jobber_usd = None
        self.msrp_cad = None
        self.msrp_usd = None
        self.map_cad = None
        self.map_usd = None
        self.save()

    @property
    def pricing_state(self):
        return {
            'Cost CAD': self.cost_cad,
            'Cost USD': self.cost_usd,
            'Jobber CAD': self.jobber_cad,
            'Jobber USD': self.jobber_usd,
            'MSRP CAD': self.msrp_cad,
            'MSRP USD': self.msrp_usd,
            'MAP CAD': self.map_cad,
            'MAP USD': self.map_usd
        }

    def update_pricing_from_api(self):
        if not self.premier_part_number:
            return self.get_instance_error_msg("Premier Part Number required")

        try:
            part_numbers = [self.premier_part_number]
            data = self._meta.model.objects.get_api_pricing_data(part_numbers)
            data = data[0]['pricing']
            update_fields = self._meta.model.objects.parse_api_pricing_data(
                data
            )
            return self.update_pricing_from_api_data(**update_fields)
        except Exception as err:
            return self.get_instance_error_msg(str(err))

    def update_pricing_from_api_data(self, **update_fields):
        try:
            prev = self.pricing_state
            self.clear_pricing_fields()
            for attr, value in update_fields.items():
                if not getattr(self, attr) == value:
                    setattr(self, attr, value)
                    self.save()
            self.refresh_from_db()
            new = self.pricing_state
            msg = self.get_update_success_msg(prev, new)
        except Exception as err:
            msg = self.get_instance_error_msg(f"{update_fields}, {err}")
        return msg

    class Meta:
        abstract = True


class PremierProduct(PremierApiProductInventoryModel,
                     PremierApiProductPricingModel):
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
    jobber = DecimalField(
        decimal_places=2,
        max_digits=10
    )
    msrp = DecimalField(
        decimal_places=2,
        max_digits=10,
        verbose_name='MSRP'
    )
    map = DecimalField(
        decimal_places=2,
        max_digits=10,
        verbose_name='MAP'
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

    objects = PremierProductManager()

    def __str__(self):
        return f'{self.premier_part_number} :: {self.manufacturer}'


class SemaBaseModel(Model, MessagesMixin):
    is_authorized = BooleanField(
        default=False,
        help_text='brand has given access to dataset'
    )

    @property
    def state(self):
        return {
            'Authorized': self.is_authorized
        }

    def update_from_api_data(self, **update_fields):
        try:
            prev = self.state
            if not self.is_authorized:
                self.is_authorized = True
                self.save()
            for attr, value in update_fields.items():
                if isinstance(
                        self._meta.model._meta.get_field(attr),
                        ManyToManyField):
                    getattr(self, attr).add(value)
                    self.save()
                elif not getattr(self, attr) == value:
                    setattr(self, attr, value)
                    self.save()
            self.refresh_from_db()
            new = self.state
            msg = self.get_update_success_msg(prev, new)
        except Exception as err:
            msg = self.get_instance_error_msg(f"{update_fields}, {err}")
        return msg

    def unauthorize(self):
        try:
            if self.is_authorized:
                previous = self.state
                self.is_authorized = False
                self.save()
                self.refresh_from_db()
                new = self.state
                msg = self.get_update_success_msg(previous, new)
            else:
                msg = self.get_instance_up_to_date_msg()
        except Exception as err:
            msg = self.get_instance_error_msg(str(err))
        return msg

    objects = SemaBaseManager()

    class Meta:
        abstract = True


class SemaBrand(SemaBaseModel):
    brand_id = CharField(
        primary_key=True,
        max_length=10,
        unique=True
    )
    name = CharField(
        max_length=50,
    )

    @property
    def state(self):
        state = dict(super().state)
        state.update(
            {
                'Name': self.name
            }
        )
        return state

    @property
    def dataset_count(self):
        return self.sema_datasets.filter(is_authorized=True).count()

    def import_datasets_from_api(self):
        return SemaDataset.objects.import_from_api(brand_ids=[self.brand_id])

    objects = SemaBrandManager()

    class Meta:
        ordering = ['name']
        verbose_name = 'SEMA brand'

    def __str__(self):
        return str(self.name)


class SemaDataset(SemaBaseModel):
    dataset_id = PositiveIntegerField(
        primary_key=True,
        unique=True
    )
    name = CharField(
        max_length=50,
    )
    brand = ForeignKey(
        SemaBrand,
        on_delete=CASCADE,
        related_name='sema_datasets'
    )

    @property
    def state(self):
        state = dict(super().state)
        state.update(
            {
                'Name': self.name,
                'Brand': str(self.brand)
            }
        )
        return state

    objects = SemaDatasetManager()

    class Meta:
        ordering = ['name']
        verbose_name = 'SEMA dataset'

    def __str__(self):
        return f'{self.brand} :: {self.name}'


class SemaYear(SemaBaseModel):
    year = PositiveSmallIntegerField(
        primary_key=True,
        unique=True
    )

    @property
    def state(self):
        return super().state

    objects = SemaYearManager()

    class Meta:
        ordering = ['year']
        verbose_name = 'SEMA year'

    def __str__(self):
        return str(self.year)


class SemaMake(SemaBaseModel):
    make_id = PositiveIntegerField(
        primary_key=True,
        unique=True
    )
    name = CharField(
        max_length=50,
    )

    @property
    def state(self):
        state = dict(super().state)
        state.update(
            {
                'Name': self.name
            }
        )
        return state

    objects = SemaMakeManager()

    class Meta:
        ordering = ['name']
        verbose_name = 'SEMA make'

    def __str__(self):
        return str(self.name)


class SemaModel(SemaBaseModel):
    model_id = PositiveIntegerField(
        primary_key=True,
        unique=True
    )
    name = CharField(
        max_length=50,
    )

    @property
    def state(self):
        state = dict(super().state)
        state.update(
            {
                'Name': self.name
            }
        )
        return state

    objects = SemaModelManager()

    class Meta:
        ordering = ['name']
        verbose_name = 'SEMA model'

    def __str__(self):
        return str(self.name)


class SemaSubmodel(SemaBaseModel):
    submodel_id = PositiveIntegerField(
        primary_key=True,
        unique=True
    )
    name = CharField(
        max_length=50,
    )

    @property
    def state(self):
        state = dict(super().state)
        state.update(
            {
                'Name': self.name
            }
        )
        return state

    objects = SemaSubmodelManager()

    class Meta:
        ordering = ['name']
        verbose_name = 'SEMA submodel'

    def __str__(self):
        return str(self.name)


class SemaMakeYear(SemaBaseModel):
    year = ForeignKey(
        SemaYear,
        on_delete=CASCADE,
        related_name='make_years'
    )
    make = ForeignKey(
        SemaMake,
        on_delete=CASCADE,
        related_name='make_years'
    )

    @property
    def state(self):
        state = dict(super().state)
        state.update(
            {
                'Year': str(self.year),
                'Make': str(self.make)
            }
        )
        return state

    objects = SemaMakeYearManager()

    class Meta:
        ordering = ['make', 'year']
        unique_together = ['make', 'year']
        verbose_name = 'SEMA make year'

    def __str__(self):
        return f'{self.year} :: {self.make}'


class SemaBaseVehicle(SemaBaseModel):
    base_vehicle_id = PositiveIntegerField(
        primary_key=True,
        unique=True
    )
    make_year = ForeignKey(
        SemaMakeYear,
        on_delete=CASCADE,
        related_name='base_vehicles'
    )
    model = ForeignKey(
        SemaModel,
        on_delete=CASCADE,
        related_name='base_vehicles'
    )

    @property
    def state(self):
        state = dict(super().state)
        state.update(
            {
                'Make Year': str(self.make_year),
                'Model': str(self.model)
            }
        )
        return state

    objects = SemaBaseVehicleManager()

    class Meta:
        ordering = ['make_year', 'model']
        verbose_name = 'SEMA base vehicle'

    def __str__(self):
        return f'{self.make_year} :: {self.model}'


class SemaVehicle(SemaBaseModel):
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

    @property
    def state(self):
        state = dict(super().state)
        state.update(
            {
                'Base Vehicle': str(self.base_vehicle),
                'Submodel': str(self.submodel)
            }
        )
        return state

    objects = SemaVehicleManager()

    class Meta:
        ordering = ['base_vehicle', 'submodel']
        verbose_name = 'SEMA vehicle'

    def __str__(self):
        return f'{self.base_vehicle} :: {self.submodel}'


class SemaCategory(SemaBaseModel):
    category_id = PositiveIntegerField(
        primary_key=True,
        unique=True
    )
    name = CharField(
        max_length=50,
    )
    parent_categories = ManyToManyField(
        'self',
        blank=True,
        related_name='child_categories',
        symmetrical=False
    )

    @property
    def state(self):
        state = dict(super().state)
        state.update(
            {
                'Name': self.name,
                'Parent': str(self.parent_categories.all())
            }
        )
        return state

    @property
    def parent_category_count(self):
        return self.parent_categories.all().count()
    parent_category_count.fget.short_description = 'Parent Count'

    @property
    def child_category_count(self):
        return self.child_categories.all().count()
    child_category_count.fget.short_description = 'Child Count'

    @property
    def level(self):
        if self.parent_category_count == 0:
            return '1'
        else:
            if self.child_category_count == 0:
                return '3'
            else:
                return '2'

    objects = SemaCategoryManager()

    class Meta:
        ordering = ['name']
        verbose_name = 'SEMA category'
        verbose_name_plural = 'SEMA categories'

    def __str__(self):
        return f'{self.level}: {self.name}'


class SemaProduct(SemaBaseModel):
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
    categories = ManyToManyField(
        SemaCategory,
        blank=True,
        related_name='categories'
    )

    @property
    def state(self):
        state = dict(super().state)
        state.update(
            {
                'Part': self.part_number,
                'Dataset': str(self.dataset)
            }
        )
        return state

    def update_html_from_api(self):
        try:
            html = sema_api.retrieve_product_html(self.product_id)
            self.html = html
            self.save()
            self.refresh_from_db()
            return self.get_update_success_msg()
        except Exception as err:
            return self.get_instance_error_msg(str(err))

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
