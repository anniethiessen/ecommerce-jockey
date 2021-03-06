from django.db.models import (
    Model,
    BooleanField,
    CharField,
    ForeignKey,
    ManyToManyField,
    PositiveIntegerField,
    PositiveSmallIntegerField,
    TextField,
    CASCADE
)

from core.mixins import MessagesMixin
from premier.models import (
    PremierManufacturer,
    PremierProduct
)
from .apis import sema_api
from .managers import (
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
            msg = self.get_update_success_msg(previous_data=prev, new_data=new)
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
                msg = self.get_update_success_msg(
                    previous_data=previous,
                    new_data=new
                )
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
        return self.datasets.filter(is_authorized=True).count()
    dataset_count.fget.short_description = 'Dataset Count'

    def import_datasets_from_api(self):
        return SemaDataset.objects.import_from_api(brand_ids=[self.brand_id])

    def perform_product_vehicle_update(self, dataset_id=None,
                                       part_numbers=None):
        """
        Retrieves **vehicles by product** data for brand object by brand
        object method and SEMA API object method and retrieves and
        updates product objects' vehicles by product manager and product
        object method and returns a list of messages.

        :type dataset_id: int
        :type part_numbers: list
        :rtype: list

        """

        msgs = []
        try:
            data = self.get_vehicles_by_product_data_from_api(
                dataset_id=dataset_id,
                part_numbers=part_numbers
            )
            msgs += SemaProduct.objects.update_product_vehicles_from_api_data(data)
        except Exception as err:
            msgs.append(self.get_instance_error_msg(str(err)))

        if not msgs:
            msgs.append(self.get_instance_up_to_date_msg())
        return msgs

    def get_vehicles_by_product_data_from_api(self, dataset_id=None,
                                              part_numbers=None):
        """
        Retrieves **vehicles by product** data for object by SEMA API
        object method and adds brand id key to each data item.

        :type dataset_id: int
        :type part_numbers: list
        :rtype: list

        :raises: Exception on SEMA API object method exception

        .. Topic:: Return Format

            [
                {
                    "PartNumber": str,
                    "Vehicles": [
                        {
                            "Year": int,
                            "MakeName": str,
                            "ModelName": str,
                            "SubmodelName": str
                        },
                        {...}
                    ],
                    "brand_id_": str
                },
                {...}
            ]

        """

        try:
            data = sema_api.retrieve_vehicles_by_product(
                brand_id=self.brand_id,
                dataset_id=dataset_id,
                part_numbers=part_numbers
            )
            for item in data:
                item['brand_id_'] = self.brand_id
            return data
        except Exception:
            raise

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
        related_name='datasets'
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

    @property
    def product_count(self):
        return self.products.filter(is_authorized=True).count()
    product_count.fget.short_description = 'Product Count'

    def perform_product_vehicle_update(self, part_numbers=None):
        """
        Retrieves **vehicles by product** data for dataset object by
        dataset object method, brand object method and SEMA API object
        method and retrieves and updates product objects' vehicles by
        product manager and product object method and returns a list of
        messages.

        :type part_numbers: list
        :rtype: list

        """

        msgs = []
        try:
            data = self.get_vehicles_by_product_data_from_api(
                part_numbers=part_numbers
            )
            msgs += SemaProduct.objects.update_product_vehicles_from_api_data(data)
        except Exception as err:
            msgs.append(self.get_instance_error_msg(str(err)))

        if not msgs:
            msgs.append(self.get_instance_up_to_date_msg())
        return msgs

    def get_vehicles_by_product_data_from_api(self, part_numbers=None):
        """
        Retrieves **vehicles by product** data for object by brand
        object method and SEMA API object method, and adds dataset id
        key each data item.

        :type part_numbers: list
        :rtype: list

        :raises: Exception on brand object method exception

        .. Topic:: Return Format

            [
                {
                    "PartNumber": str,
                    "Vehicles": [
                        {
                            "Year": int,
                            "MakeName": str,
                            "ModelName": str,
                            "SubmodelName": str
                        },
                        {...}
                    ],
                    "brand_id_": str,
                    "dataset_id_": int
                },
                {...}
            ]

        """

        try:
            data = self.brand.get_vehicles_by_product_data_from_api(
                dataset_id=self.dataset_id,
                part_numbers=part_numbers
            )
            for item in data:
                item['dataset_id_'] = self.dataset_id
            return data
        except Exception:
            raise

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

    @property
    def make_year_count(self):
        return self.make_years.filter(is_authorized=True).count()
    make_year_count.fget.short_description = 'Make Year Count'

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

    @property
    def make_year_count(self):
        return self.make_years.filter(is_authorized=True).count()
    make_year_count.fget.short_description = 'Make Year Count'

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

    @property
    def base_vehicle_count(self):
        return self.base_vehicles.filter(is_authorized=True).count()
    base_vehicle_count.fget.short_description = 'Base Vehicle Count'

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

    @property
    def vehicle_count(self):
        return self.vehicles.filter(is_authorized=True).count()
    vehicle_count.fget.short_description = 'Vehicle Count'

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

    @property
    def base_vehicle_count(self):
        return self.base_vehicles.filter(is_authorized=True).count()
    base_vehicle_count.fget.short_description = 'Base Vehicle Count'

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

    @property
    def vehicle_count(self):
        return self.vehicles.filter(is_authorized=True).count()
    vehicle_count.fget.short_description = 'Vehicle Count'

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
    is_relevant = BooleanField(
        default=False
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

    @property
    def product_count(self):
        return self.products.filter(is_authorized=True).count()
    product_count.fget.short_description = 'Product Count'

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
    def product_count(self):
        return self.products.filter(is_authorized=True).count()
    product_count.fget.short_description = 'Product Count'

    @property
    def parent_category_count(self):
        return self.parent_categories.filter(is_authorized=True).count()
    parent_category_count.fget.short_description = 'Parent Count'

    @property
    def child_category_count(self):
        return self.child_categories.filter(is_authorized=True).count()
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

    def perform_product_category_update(self, brand_ids=None, dataset_ids=None,
                                        base_vehicle_ids=None,
                                        vehicle_ids=None, part_numbers=None,
                                        year=None, make_name=None,
                                        model_name=None, submodel_name=None,
                                        pies_segments=None):
        """
        Retrieves **products by category** data for category object by
        category object method and SEMA API object method and retrieves
        and updates product objects' categories by product manager and
        product object method, and returns a list of messages.

        :type brand_ids: list
        :type dataset_ids: list
        :type base_vehicle_ids: list
        :type vehicle_ids: list
        :type part_numbers: list
        :type year: int
        :type make_name: str
        :type model_name: str
        :type submodel_name: str
        :type pies_segments: list
        :rtype: list

        """

        msgs = []
        try:
            data = self.get_products_by_category_data_from_api(
                brand_ids=brand_ids,
                dataset_ids=dataset_ids,
                base_vehicle_ids=base_vehicle_ids,
                vehicle_ids=vehicle_ids,
                part_numbers=part_numbers,
                year=year,
                make_name=make_name,
                model_name=model_name,
                submodel_name=submodel_name,
                pies_segments=pies_segments
            )
            msgs += SemaProduct.objects.update_product_categories_from_api_data(
                data
            )
        except Exception as err:
            msgs.append(self.get_instance_error_msg(str(err)))
            return msgs

        if not msgs:
            msgs.append(self.get_instance_up_to_date_msg())
        return msgs

    def get_products_by_category_data_from_api(self,
                                               brand_ids=None,
                                               dataset_ids=None,
                                               base_vehicle_ids=None,
                                               vehicle_ids=None,
                                               part_numbers=None,
                                               year=None, make_name=None,
                                               model_name=None,
                                               submodel_name=None,
                                               pies_segments=None):
        """
        Retrieves **products by category** data for object by SEMA API
        object method and adds category id key to each data item.

        :type brand_ids: list
        :type dataset_ids: list
        :type base_vehicle_ids: list
        :type vehicle_ids: list
        :type part_numbers: list
        :type year: int
        :type make_name: str
        :type model_name: str
        :type submodel_name: str
        :type pies_segments: list
        :rtype: list

        :raises: Exception on SEMA API object method exception

        .. warnings also:: Filtering by year, make, model, or submodel
        requires all four

        .. Topic:: Return Format

            [
                {
                    "ProductId": int,
                    "PartNumber": str,
                    "PiesAttributes": [],
                    "category_id_" int
                },
                {...}
            ]

        """

        try:
            data = sema_api.retrieve_products_by_category(
                category_id=self.category_id,
                brand_ids=brand_ids,
                dataset_ids=dataset_ids,
                base_vehicle_ids=base_vehicle_ids,
                vehicle_ids=vehicle_ids,
                year=year,
                make_name=make_name,
                model_name=model_name,
                submodel_name=submodel_name,
                part_numbers=part_numbers,
                pies_segments=pies_segments
            )
            for item in data:
                item['category_id_'] = self.category_id
            return data
        except Exception:
            raise

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
        related_name='products',
    )
    html = TextField(
        blank=True,
        verbose_name='HTML'
    )
    categories = ManyToManyField(
        SemaCategory,
        blank=True,
        related_name='products'
    )
    vehicles = ManyToManyField(
        SemaVehicle,
        blank=True,
        related_name='products'
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

    def perform_product_html_update(self):
        try:
            html = self.get_product_html_data_from_api()
            self.html = html
            self.save()
            self.refresh_from_db()
            return self.get_update_success_msg()
        except Exception as err:
            return self.get_instance_error_msg(str(err))

    def perform_product_vehicle_update(self):
        """
        Retrieves **vehicles by product** data for product object by
        product object method, dataset object method, brand object
        method and SEMA API object method and retrieves and updates
        product objects' vehicles by product manager and product object
        method and returns a list of messages.

        :rtype: list

        """

        msgs = []
        try:
            data = self.get_vehicles_by_product_data_from_api()
            msgs += SemaProduct.objects.update_product_vehicles_from_api_data(data)
        except Exception as err:
            msgs.append(self.get_instance_error_msg(str(err)))

        if not msgs:
            msgs.append(self.get_instance_up_to_date_msg())
        return msgs

    def get_product_html_data_from_api(self):
        """
        Retrieves **product html** data for object by SEMA API object
        method.

        :rtype: str

        :raises: Exception on SEMA API object method exception

        """

        try:
            return sema_api.retrieve_product_html(self.product_id)
        except Exception:
            raise

    def get_vehicles_by_product_data_from_api(self):
        """
        Retrieves **vehicles by product** data for object by dataset
        object method, brand object method, and SEMA API object method,
        and adds product id key each data item.

        :rtype: list

        :raises: Exception on dataset object method exception

        .. Topic:: Return Format

            [
                {
                    "PartNumber": str,
                    "Vehicles": [
                        {
                            "Year": int,
                            "MakeName": str,
                            "ModelName": str,
                            "SubmodelName": str
                        },
                        {...}
                    ],
                    "brand_id_": str,
                    "dataset_id_": int,
                    "product_id_": int
                },
                {...}
            ]

        """

        try:
            data = self.dataset.get_vehicles_by_product_data_from_api(
                part_numbers=[self.part_number]
            )
            for item in data:
                item['product_id_'] = self.product_id
            return data
        except Exception:
            raise

    def update_product_vehicles_from_api_data(self, data):
        """
        Adds vehicles from data to product object and returns a list of
        messages.

        :type data: list
        :rtype: list

        .. warnings also:: Does not remove vehicles not in data

        .. Topic:: Expected Data Format

            [
                {
                    "Year": int,
                    "MakeName": str,
                    "ModelName": str,
                    "SubmodelName": str
                },
                {...}
            ]

        """

        msgs = []
        for item in data:
            try:
                vehicle = SemaVehicle.objects.get_by_names(
                    year=item['Year'],
                    make_name=item['MakeName'],
                    model_name=item['ModelName'],
                    submodel_name=item['SubmodelName'],
                )
            except SemaVehicle.DoesNotExist:
                # FIXME
                from random import randint
                from django.core.exceptions import MultipleObjectsReturned
                try:
                    year, created = SemaYear.objects.get_or_create(
                        year=item['Year'],
                        defaults={'is_authorized': False}
                    )
                    if created:
                        print(f'Created year {year}')

                    try:
                        make = SemaMake.objects.get(name=item['MakeName'])
                    except SemaMake.DoesNotExist:
                        pk = randint(1000000, 9999999)
                        while SemaMake.objects.filter(pk=pk).exists():
                            pk = randint(1000000, 9999999)
                        make = SemaMake.objects.create(
                            make_id=pk,
                            name=item['MakeName'],
                            is_authorized=False
                        )
                        print(f'Created make {make}')

                    make_year, created = SemaMakeYear.objects.get_or_create(
                        year=year,
                        make=make,
                        defaults={'is_authorized': False}
                    )
                    if created:
                        print(f'Created make year {make_year}')

                    try:
                        model = SemaModel.objects.get(
                            name=item['ModelName']
                        )
                    except SemaModel.DoesNotExist:
                        pk = randint(1000000, 9999999)
                        while SemaModel.objects.filter(pk=pk).exists():
                            pk = randint(1000000, 9999999)
                        model = SemaModel.objects.create(
                            model_id=pk,
                            name=item['ModelName'],
                            is_authorized=False
                        )
                        print(f'Created model {model}')

                    try:
                        base_vehicle = SemaBaseVehicle.objects.get(
                            make_year=make_year,
                            model=model
                        )
                    except SemaBaseVehicle.DoesNotExist:
                        pk = randint(1000000, 9999999)
                        while SemaBaseVehicle.objects.filter(pk=pk).exists():
                            pk = randint(1000000, 9999999)
                        base_vehicle = SemaBaseVehicle.objects.create(
                            base_vehicle_id=pk,
                            make_year=make_year,
                            model=model
                        )
                        print(f'Created base vehicle {base_vehicle}')

                    try:
                        submodel = SemaSubmodel.objects.get(
                            name=item['SubmodelName']
                        )
                    except SemaSubmodel.DoesNotExist:
                        pk = randint(1000000, 9999999)
                        while SemaSubmodel.objects.filter(pk=pk).exists():
                            pk = randint(1000000, 9999999)
                        submodel = SemaSubmodel.objects.create(
                            submodel_id=pk,
                            name=item['SubmodelName'],
                            is_authorized=False
                        )
                        print(f'Created submodel {submodel}')

                    pk = randint(1000000, 9999999)
                    while SemaVehicle.objects.filter(pk=pk).exists():
                        pk = randint(1000000, 9999999)
                    vehicle = SemaVehicle.objects.create(
                        vehicle_id=pk,
                        base_vehicle=base_vehicle,
                        submodel=submodel,
                        is_authorized=False
                    )
                    print(f'Created vehicle {vehicle}')
                except Exception as err:
                    msgs.append(
                        self.get_instance_error_msg(f"{item}, {err}")
                    )
                    continue
            except Exception as err:
                msgs.append(self.get_instance_error_msg(f"{item}, {err}"))
                continue

            try:
                if vehicle in self.vehicles.all():
                    msgs.append(
                        self.get_instance_up_to_date_msg(
                            message=f"{vehicle} already added"
                        )
                    )
                else:
                    self.vehicles.add(vehicle)
                    self.save()
                    msgs.append(
                        self.get_update_success_msg(message=f"{vehicle} added")
                    )
            except Exception as err:
                msgs.append(self.get_instance_error_msg(f"{item}, {err}"))
                continue
        return msgs

    def update_product_categories_from_api_data(self, data):
        """
        Adds categories from data to product object and returns a list
        of messages.

        :type data: list
        :rtype: list

        .. warnings also:: Does not remove categories not in data

        .. Topic:: Expected Data Format

            [5, 845, 3453]

        """

        msgs = []
        for item in data:
            try:
                category = SemaCategory.objects.get(
                    category_id=item
                )
                if category in self.categories.all():
                    msgs.append(
                        self.get_instance_up_to_date_msg(
                            message=f"{category} already added"
                        )
                    )
                else:
                    self.categories.add(category)
                    self.save()
                    msgs.append(
                        self.get_update_success_msg(
                            message=f"{category} added"
                        )
                    )
            except Exception as err:
                msgs.append(self.get_instance_error_msg(f"{item, err}"))
                continue
        return msgs

    objects = SemaProductManager()

    class Meta:
        ordering = ['dataset', 'part_number']
        verbose_name = 'SEMA product'

    def __str__(self):
        return f'{self.product_id} :: {self.dataset}'
