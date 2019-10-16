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

from .apis import (
    SemaApi,
    PremierApi
)
from .managers import (
    PremierProductManager,
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


premier_api = PremierApi()
sema_api = SemaApi()


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

    @staticmethod
    def get_api_inventory_data(part_numbers):
        try:
            return premier_api.retrieve_product_inventory(part_numbers)
        except Exception:
            raise

    @classmethod
    def parse_api_inventory_data(cls, data):
        try:
            update_fields = {}
            for item in data:
                field = f'inventory_{item["warehouseCode"][:2].lower()}'
                update_fields[field] = int(item['quantityAvailable'])
            return update_fields
        except Exception:
            raise

    def update_inventory_from_api(self):
        if not self.premier_part_number:
            return self.get_instance_error_msg("Premier Part Number required")

        try:
            part_numbers = [self.premier_part_number]
            data = self.get_api_inventory_data(part_numbers)
            data = data[0]['inventory']
            update_fields = self.parse_api_inventory_data(data)
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

    @staticmethod
    def get_api_pricing_data(part_numbers):
        try:
            return premier_api.retrieve_product_pricing(part_numbers)
        except Exception:
            raise

    @classmethod
    def parse_api_pricing_data(cls, data):
        try:
            update_fields = {}
            for item in data:
                currency = item.pop('currency')
                item['msrp'] = item.pop('retail')
                for key, value in item.items():
                    field = f'{key.lower()}_{currency.lower()}'
                    update_fields[field] = value
            return update_fields
        except Exception:
            raise

    def update_pricing_from_api(self):
        if not self.premier_part_number:
            return self.get_instance_error_msg("Premier Part Number required")

        try:
            part_numbers = [self.premier_part_number]
            data = self.get_api_pricing_data(part_numbers)
            data = data[0]['pricing']
            update_fields = self.parse_api_pricing_data(data)
            return self.update_pricing_from_api_data(**update_fields)
        except Exception as err:
            return self.get_instance_error_msg(str(err))

    def update_pricing_from_api_data(self, include_up_to_date=True,
                                     **update_fields):
        try:
            prev = self.pricing_state
            self.clear_pricing_fields()
            for attr, value in update_fields.items():
                if not getattr(self, attr) == value:
                    setattr(self, attr, value)
                    self.save()
            self.refresh_from_db()
            new = self.pricing_state
            msg = self.get_update_success_msg(prev, new, include_up_to_date)
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


class SemaApiModel(Model, MessagesMixin):
    is_authorized = BooleanField(
        default=False,
        help_text='brand has given access to dataset'
    )

    @property
    def state(self):
        return {
            'Authorized': self.is_authorized
        }

    @classmethod
    def get_api_filter_errors(cls, new_only, *args, **filters):
        errors = []
        if filters and new_only:
            return errors.append("New only import cannot be used with filters")
        return errors

    @classmethod
    def get_pk_list_from_api_data(cls, data):
        raise Exception('Get PK list must be defined')

    @staticmethod
    def get_api_data(**filters):
        raise Exception('Get API data must be defined')

    @classmethod
    def parse_api_data(cls, data):
        raise Exception('Parse API data must be defined')

    @classmethod
    def import_from_api(cls, new_only=False, *args, **filters):
        msgs = []

        try:
            errors = cls.get_api_filter_errors(new_only, **filters)
            if errors:
                msgs.append(cls.get_class_error_msg(errors))
                return msgs
        except Exception as err:
            msgs.append(cls.get_class_error_msg(str(err)))
            return msgs

        try:
            data = cls.get_api_data(**filters)
        except Exception as err:
            msgs.append(cls.get_class_error_msg(str(err)))
            return msgs

        if not new_only:
            try:
                authorized_pks = cls.get_pk_list_from_api_data(data)
                msgs += cls.unauthorize_from_api_data(authorized_pks)
            except Exception as err:
                msgs.append(cls.get_class_error_msg(str(err)))
                return msgs

        try:
            msgs += cls.perform_create_update_from_api_data(new_only, data)
        except Exception as err:
            msgs.append(cls.get_class_error_msg(str(err)))

        if not msgs:
            if new_only:
                msgs.append(cls.get_class_nothing_new_msg())
            else:
                msgs.append(cls.get_class_up_to_date_msg())
        return msgs

    @classmethod
    def perform_create_update_from_api_data(cls, new_only, data):
        msgs = []
        for item in data:
            try:
                pk, update_fields = cls.parse_api_data(item)
            except Exception as err:
                msgs.append(cls.get_class_error_msg(f"{item}: {err}"))
                continue

            nested_data = cls.get_nested_data_from_api_data(item)

            try:
                obj = cls.get_object_from_api_data(pk, **update_fields)
                if not new_only:
                    msgs.append(obj.update_from_api_data(**update_fields))
            except cls.DoesNotExist:
                msgs.append(cls.create_from_api_data(pk, **update_fields))
            except Exception as err:
                msgs.append(cls.get_class_error_msg(f"{item}: {err}"))

            if nested_data:
                msgs += cls.perform_create_update_from_api_data(
                    new_only,
                    nested_data
                )

        return msgs

    @staticmethod
    def get_nested_data_from_api_data(data):
        return None

    @classmethod
    def unauthorize_from_api_data(cls, authorized_pks,
                                  include_up_to_date=True):
        msgs = []
        unauthorized = cls.objects.filter(~Q(pk__in=authorized_pks))

        if include_up_to_date:
            for obj in unauthorized.filter(is_authorized=False):
                msgs.append(obj.get_instance_up_to_date_msg())

        for obj in unauthorized.filter(is_authorized=True):
            previous = obj.state
            obj.is_authorized = False
            obj.save()
            obj.refresh_from_db()
            new = obj.state
            msgs.append(obj.get_update_success_msg(previous, new))

        return msgs

    @classmethod
    def get_object_from_api_data(cls, pk, **update_fields):
        try:
            return cls.objects.get(pk=pk)
        except Exception:
            raise

    @classmethod
    def create_from_api_data(cls, pk, **update_fields):
        try:
            obj = cls.objects.create(
                pk=pk,
                is_authorized=True,
                **update_fields
            )
            msg = obj.get_create_success_msg()
        except Exception as err:
            msg = cls.get_class_error_msg(f"{pk}, {update_fields}, {err}")
        return msg

    def update_from_api_data(self, include_up_to_date=True, **update_fields):
        try:
            prev = self.state
            if not self.is_authorized:
                self.is_authorized = True
                self.save()
            for attr, value in update_fields.items():
                if not getattr(self, attr) == value:
                    setattr(self, attr, value)
                    self.save()
            self.refresh_from_db()
            new = self.state
            msg = self.get_update_success_msg(prev, new, include_up_to_date)
        except Exception as err:
            msg = self.get_instance_error_msg(f"{update_fields}, {err}")
        return msg

    class Meta:
        abstract = True


class SemaBrand(SemaApiModel):
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

    @classmethod
    def get_pk_list_from_api_data(cls, data):
        try:
            return [item['AAIABrandId'] for item in data]
        except Exception:
            raise

    @staticmethod
    def get_api_data():
        try:
            data = sema_api.retrieve_brand_datasets()
            for item in data:
                del item['DatasetId']
                del item['DatasetName']
            return data
        except Exception:
            raise

    @classmethod
    def parse_api_data(cls, data):
        pk = data['AAIABrandId']
        update_fields = {
            'name': data['BrandName']
        }
        return pk, update_fields

    objects = SemaBrandManager()

    class Meta:
        ordering = ['name']
        verbose_name = 'SEMA brand'

    @property
    def dataset_count(self):
        return self.sema_datasets.count()

    def __str__(self):
        return str(self.name)


class SemaDataset(SemaApiModel):
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

    @classmethod
    def get_pk_list_from_api_data(cls, data):
        try:
            return [item['DatasetId'] for item in data]
        except Exception:
            raise

    @staticmethod
    def get_api_data(brand_id=None):
        try:
            data = sema_api.retrieve_brand_datasets()
            if brand_id:
                data = [
                    item for item in data
                    if item['AAIABrandId'] == brand_id
                ]
            return data
        except Exception:
            raise

    @classmethod
    def parse_api_data(cls, data):
        pk = data['DatasetId']
        update_fields = {
            'name': data['DatasetName'],
            'brand': SemaBrand.objects.get(brand_id=data['AAIABrandId'])
        }
        return pk, update_fields

    objects = SemaDatasetManager()

    class Meta:
        ordering = ['name']
        verbose_name = 'SEMA dataset'

    def __str__(self):
        return f'{self.brand} :: {self.name}'


class SemaYear(SemaApiModel):
    year = PositiveSmallIntegerField(
        primary_key=True,
        unique=True
    )

    @property
    def state(self):
        return super().state

    @classmethod
    def get_pk_list_from_api_data(cls, data):
        return data

    @staticmethod
    def get_api_data(brand_id=None, dataset_id=None):
        try:
            return sema_api.retrieve_years(
                brand_id=brand_id,
                dataset_id=dataset_id
            )
        except Exception:
            raise

    @classmethod
    def parse_api_data(cls, data):
        pk = data
        update_fields = {}
        return pk, update_fields

    objects = SemaYearManager()

    class Meta:
        ordering = ['year']
        verbose_name = 'SEMA year'

    def __str__(self):
        return str(self.year)


class SemaMake(SemaApiModel):
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

    @classmethod
    def get_pk_list_from_api_data(cls, data):
        try:
            return [item['MakeID'] for item in data]
        except Exception:
            raise

    @staticmethod
    def get_api_data(brand_id=None, dataset_id=None, year=None):
        try:
            return sema_api.retrieve_makes(
                brand_id=brand_id,
                dataset_id=dataset_id,
                year=year
            )
        except Exception:
            raise

    @classmethod
    def parse_api_data(cls, data):
        try:
            pk = data['MakeID']
            update_fields = {
                'name': data['MakeName']
            }
            return pk, update_fields
        except Exception:
            raise

    objects = SemaMakeManager()

    class Meta:
        ordering = ['name']
        verbose_name = 'SEMA make'

    def __str__(self):
        return str(self.name)


class SemaModel(SemaApiModel):
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

    @classmethod
    def get_pk_list_from_api_data(cls, data):
        try:
            return [item['ModelID'] for item in data]
        except Exception:
            raise

    @staticmethod
    def get_api_data(brand_id=None, dataset_id=None, year=None, make_id=None):
        try:
            data = sema_api.retrieve_models(
                brand_id=brand_id,
                dataset_id=dataset_id,
                year=year,
                make_id=make_id
            )
            for item in data:
                del item['BaseVehicleID']
            return [dict(t) for t in {tuple(item.items()) for item in data}]
        except Exception:
            raise

    @classmethod
    def parse_api_data(cls, data):
        try:
            pk = data['ModelID']
            update_fields = {
                'name': data['ModelName']
            }
            return pk, update_fields
        except Exception:
            raise

    objects = SemaModelManager()

    class Meta:
        ordering = ['name']
        verbose_name = 'SEMA model'

    def __str__(self):
        return str(self.name)


class SemaSubmodel(SemaApiModel):
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

    @classmethod
    def get_pk_list_from_api_data(cls, data):
        try:
            return [item['SubmodelID'] for item in data]
        except Exception:
            raise

    @staticmethod
    def get_api_data(brand_id=None, dataset_id=None,
                     year=None, make_id=None, model_id=None):
        try:
            data = sema_api.retrieve_submodels(
                brand_id=brand_id,
                dataset_id=dataset_id,
                year=year,
                make_id=make_id,
                model_id=model_id
            )
            for item in data:
                del item['VehicleID']
            return [dict(t) for t in {tuple(item.items()) for item in data}]
        except Exception:
            raise

    @classmethod
    def parse_api_data(cls, data):
        try:
            pk = data['SubmodelID']
            update_fields = {
                'name': data['SubmodelName']
            }
            return pk, update_fields
        except Exception:
            raise

    objects = SemaSubmodelManager()

    class Meta:
        ordering = ['name']
        verbose_name = 'SEMA submodel'

    def __str__(self):
        return str(self.name)


class SemaMakeYear(SemaApiModel):
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

    @classmethod
    def get_pk_list_from_api_data(cls, data):
        try:
            pk_list = []
            for item in data:
                try:
                    year_make = cls.objects.get(
                        year__year=item['year'],
                        make__make_id=item['MakeID']
                    )
                    pk_list.append(year_make.pk)
                except cls.DoesNotExist:
                    pass
            return pk_list
        except Exception:
            raise

    @staticmethod
    def get_api_data(year, brand_id=None, dataset_id=None):
        try:
            data = sema_api.retrieve_makes(
                brand_id=brand_id,
                dataset_id=dataset_id,
                year=year
            )
            for item in data:
                item['year_'] = year
            return data
        except Exception:
            raise

    @classmethod
    def parse_api_data(cls, data):
        try:
            pk = None
            update_fields = {
                'year': SemaYear.objects.get(year=data['year_']),
                'make': SemaMake.objects.get(make_id=data['MakeID']),
            }
            return pk, update_fields
        except Exception:
            raise

    @classmethod
    def get_object_from_api_data(cls, pk, **update_fields):
        try:
            return cls.objects.get(
                year=update_fields['year'],
                make=update_fields['make']
            )
        except Exception:
            raise

    objects = SemaMakeYearManager()

    class Meta:
        ordering = ['make', 'year']
        unique_together = ['make', 'year']
        verbose_name = 'SEMA make year'

    def __str__(self):
        return f'{self.year} :: {self.make}'


class SemaBaseVehicle(SemaApiModel):
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

    @classmethod
    def get_pk_list_from_api_data(cls, data):
        try:
            return [item['BaseVehicleID'] for item in data]
        except Exception:
            raise

    @staticmethod
    def get_api_data(year, make_id, brand_id=None, dataset_id=None):
        try:
            data = sema_api.retrieve_models(
                brand_id=brand_id,
                dataset_id=dataset_id,
                year=year,
                make_id=make_id
            )
            for item in data:
                item['year_'] = year
                item['make_id_'] = make_id
            return data
        except Exception:
            raise

    @classmethod
    def parse_api_data(cls, data):
        try:
            pk = data['BaseVehicleID']
            update_fields = {
                'make_year': SemaMakeYear.objects.get(
                    year__year=data['year_'],
                    make__make_id=data['make_id_']
                ),
                'model': SemaModel.objects.get(model_id=data['ModelID'])
            }
            return pk, update_fields
        except Exception:
            raise

    objects = SemaBaseVehicleManager()

    class Meta:
        ordering = ['make_year', 'model']
        verbose_name = 'SEMA base vehicle'

    def __str__(self):
        return f'{self.make_year} :: {self.model}'


class SemaVehicle(SemaApiModel):
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

    # year, make_id, model_id
    # brand_id=None, dataset_id=None

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

    @classmethod
    def get_pk_list_from_api_data(cls, data):
        try:
            return [item['VehicleID'] for item in data]
        except Exception:
            raise

    @staticmethod
    def get_api_data(year, make_id, model_id, brand_id=None, dataset_id=None):
        try:
            data = sema_api.retrieve_submodels(
                brand_id=brand_id,
                dataset_id=dataset_id,
                year=year,
                make_id=make_id,
                model_id=model_id
            )
            for item in data:
                item['year_'] = year
                item['make_id_'] = make_id
                item['model_id_'] = model_id
            return data
        except Exception:
            raise

    @classmethod
    def parse_api_data(cls, data):
        try:
            pk = data['VehicleID']
            update_fields = {
                'base_vehicle': SemaBaseVehicle.objects.get(
                    make_year__year__year=data['year_'],
                    make_year__make__make_id=data['make_id_'],
                    model__model_id=data['model_id_']
                ),
                'submodel': SemaSubmodel.objects.get(
                    submodel_id=data['SubmodelID']
                )
            }
            return pk, update_fields
        except Exception:
            raise

    objects = SemaVehicleManager()

    class Meta:
        ordering = ['base_vehicle', 'submodel']
        verbose_name = 'SEMA vehicle'

    def __str__(self):
        return f'{self.base_vehicle} :: {self.submodel}'


class SemaCategory(SemaApiModel):
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

    @property
    def state(self):
        state = dict(super().state)
        state.update(
            {
                'Name': self.name,
                'Parent': str(self.parent_category)
            }
        )
        return state

    @classmethod
    def get_pk_list_from_api_data(cls, data):
        try:
            return [item['CategoryId'] for item in data]
        except Exception:
            raise

    @staticmethod
    def get_api_data(brand_id, dataset_id=None,
                     year=None, make_name=None,
                     model_name=None, submodel_name=None,
                     base_vehicle_id=None, vehicle_id=None):
        try:
            return sema_api.retrieve_categories(
                brand_id=brand_id,
                dataset_id=dataset_id,
                year=year,
                make_name=make_name,
                model_name=model_name,
                submodel_name=submodel_name,
                base_vehicle_id=base_vehicle_id,
                vehicle_id=vehicle_id
            )
        except Exception:
            raise

    @classmethod
    def parse_api_data(cls, data):
        try:
            pk = data['CategoryId']
            update_fields = {
                'name': data['Name']
            }
            if data.get('ParentId'):
                update_fields['parent_category'] = (
                    cls.objects.get(category_id=data['ParentId'])
                )
            return pk, update_fields
        except Exception:
            raise

    @staticmethod
    def get_nested_data_from_api_data(data):
        return data['Categories']

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


class SemaProduct(SemaApiModel):
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

    @classmethod
    def get_pk_list_from_api_data(cls, data):
        try:
            return [item['ProductId'] for item in data]
        except Exception:
            raise

    @staticmethod
    def get_api_data(brand_id, dataset_id=None,
                     year=None, make_name=None,
                     model_name=None, submodel_name=None,
                     base_vehicle_id=None, vehicle_id=None,
                     part_number=None, pies_segments=None):

        try:
            data = sema_api.retrieve_products_by_brand(
                brand_id=brand_id,
                dataset_id=dataset_id,
                year=year,
                make_name=make_name,
                model_name=model_name,
                submodel_name=submodel_name,
                base_vehicle_id=base_vehicle_id,
                vehicle_id=vehicle_id,
                part_number=part_number,
                pies_segments=part_number
            )
            for item in data:
                item['dataset_id_'] = dataset_id
            return data
        except Exception:
            raise

    @classmethod
    def parse_api_data(cls, data):
        try:
            pk = data['ProductId']
            update_fields = {
                'part_number': data['PartNumber'],
                'dataset': SemaDataset.objects.get(
                    dataset_id=data['dataset_id_']
                )
            }
            return pk, update_fields
        except Exception:
            raise

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
