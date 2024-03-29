import os
from shutil import move

from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

from django.conf import settings
from django.db.models import (
    Model,
    CharField,
    DecimalField,
    ForeignKey,
    ImageField,
    IntegerField,
    CASCADE
)

from core.mixins import MessagesMixin
from core.models import RelevancyBaseModel
from .managers import (
    PremierManufacturerManager,
    PremierProductManager
)
from .utils import (
    premier_manufacturer_image_path,
    premier_product_image_path
)


class PremierManufacturer(RelevancyBaseModel):
    name = CharField(
        max_length=50,
        unique=True
    )
    primary_image = ImageField(
        blank=True,
        null=True,
        upload_to=premier_manufacturer_image_path
    )
    primary_image_thumbnail = ImageSpecField(
        [
            ResizeToFill(100, 100)
        ],
        source='primary_image',
        format='JPEG',
        options={'quality': 50}
    )
    slug = CharField(
        max_length=20,
        unique=True
    )

    # <editor-fold desc="relevancy properties ...">
    @property
    def relevancy_errors(self):
        msgs = []
        if self.is_relevant:
            if not self.primary_image or self.primary_image == '':
                error = "no primary image"
                msgs.append(error)
        return ', '.join(msgs)
    relevancy_errors.fget.short_description = 'Errors'
    # </editor-fold>

    # <editor-fold desc="count properties ...">
    @property
    def product_count(self):
        return self.products.count()

    @property
    def product_relevant_count(self):
        return self.products.filter(is_relevant=True).count()
    product_relevant_count.fget.short_description = 'Relevant Product Count'
    # </editor-fold>

    objects = PremierManufacturerManager()

    def __str__(self):
        return self.name


class PremierProductInventoryBaseModel(Model, MessagesMixin):
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

    # <editor-fold desc="update properties ...">
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
        
    def perform_inventory_update_from_api_data(self, **update_fields):
        try:
            prev = self.inventory_state
            self.clear_inventory_fields()
            for attr, value in update_fields.items():
                if not getattr(self, attr) == value:
                    setattr(self, attr, value)
                    self.save()
            self.refresh_from_db()
            new = self.inventory_state
            msg = self.get_update_success_msg(previous_data=prev, new_data=new)
        except Exception as err:
            msg = self.get_instance_error_msg(f"{update_fields}, {err}")
        return msg
    # </editor-fold>

    # <editor-fold desc="perform properties ...">
    def perform_inventory_update_from_api(self):
        try:
            part_numbers = [self.premier_part_number]
            data = self._meta.model.objects.retrieve_inventory_data_from_api(
                part_numbers
            )
            data = data[0]['inventory']
            update_fields = self._meta.model.objects.parse_api_inventory_data(
                data
            )
            return self.perform_inventory_update_from_api_data(**update_fields)
        except Exception as err:
            return self.get_instance_error_msg(str(err))
    # </editor-fold>

    class Meta:
        abstract = True


class PremierProductPricingBaseModel(Model, MessagesMixin):
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

    # <editor-fold desc="update properties ...">
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
        
    def perform_pricing_update_from_api_data(self, **update_fields):
        try:
            prev = self.pricing_state
            self.clear_pricing_fields()
            for attr, value in update_fields.items():
                if not getattr(self, attr) == value:
                    setattr(self, attr, value)
                    self.save()
            self.refresh_from_db()
            new = self.pricing_state
            msg = self.get_update_success_msg(previous_data=prev, new_data=new)
        except Exception as err:
            msg = self.get_instance_error_msg(f"{update_fields}, {err}")
        return msg
    # </editor-fold>

    # <editor-fold desc="perform properties ...">
    def perform_pricing_update_from_api(self):
        try:
            part_numbers = [self.premier_part_number]
            data = self._meta.model.objects.retrieve_pricing_data_from_api(part_numbers)
            data = data[0]['pricing']
            update_fields = self._meta.model.objects.parse_api_pricing_data(
                data
            )
            return self.perform_pricing_update_from_api_data(**update_fields)
        except Exception as err:
            return self.get_instance_error_msg(str(err))
    # </editor-fold>

    class Meta:
        abstract = True


class PremierProduct(PremierProductInventoryBaseModel,
                     PremierProductPricingBaseModel, RelevancyBaseModel):
    premier_part_number = CharField(
        max_length=30,
        unique=True,
        primary_key=True
    )
    vendor_part_number = CharField(
        max_length=30,
    )
    description = CharField(
        max_length=500
    )
    manufacturer = ForeignKey(
        PremierManufacturer,
        on_delete=CASCADE,
        related_name='products'
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
    primary_image = ImageField(
        blank=True,
        max_length=200,
        null=True,
        upload_to=premier_product_image_path
    )
    primary_image_thumbnail = ImageSpecField(
        [
            ResizeToFill(100, 100)
        ],
        source='primary_image',
        format='JPEG',
        options={'quality': 50}
    )

    # <editor-fold desc="relevancy properties ...">
    @property
    def may_be_relevant(self):
        return bool(
            self.manufacturer.is_relevant and self.inventory_ab
        )

    @property
    def relevancy_errors(self):
        msgs = []
        if self.is_relevant:
            if not self.manufacturer.is_relevant:
                error = "manufacturer not relevant"
                msgs.append(error)
            if not self.inventory_ab or self.inventory_ab <= 0:
                error = "no AB inventory"
                msgs.append(error)
            if not self.cost_cad or self.cost_cad <= 0:
                error = "no CAD cost"
                msgs.append(error)
            if not self.primary_image or self.primary_image == '':
                error = "no primary image"
                msgs.append(error)
        return ', '.join(msgs)
    relevancy_errors.fget.short_description = 'Errors'
    # </editor-fold>

    # <editor-fold desc="perform properties ...">
    def perform_primary_image_update_from_media_root(self):
        try:
            bucket_path = os.path.join(
                settings.MEDIA_ROOT,
                'premier',
                self.manufacturer.slug,
                'bucket',
                self.vendor_part_number + '.jpg'
            )
            image_path = os.path.join(
                settings.MEDIA_ROOT,
                premier_product_image_path(
                    self,
                    self.vendor_part_number
                ) + '.jpg'
            )
            save_path = premier_product_image_path(
                self,
                self.vendor_part_number + '.jpg'
            )
            if os.path.exists(bucket_path):
                move(bucket_path, image_path)
                self.primary_image = save_path
                self.save()
                msg = self.get_update_success_msg('Image updated from bucket')
            elif os.path.exists(image_path):
                self.primary_image = save_path
                self.save()
                msg = self.get_update_success_msg('Image updated')
            else:
                msg = self.get_instance_error_msg('Image does not exist')
        except Exception as err:
            msg = self.get_instance_error_msg(str(err))
        return msg
    # </editor-fold>

    objects = PremierProductManager()

    def __str__(self):
        return f'{self.vendor_part_number} :: {self.manufacturer.name}'
