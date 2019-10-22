from import_export.fields import Field
from import_export.resources import ModelResource
from import_export.widgets import ForeignKeyWidget

from core.admin.widgets import RoundedDecimalWidget
from ..models import PremierManufacturer, PremierProduct


class PremierProductResource(ModelResource):
    premier_part_number = Field(
        attribute='premier_part_number',
        column_name='PremierPartNumber'
    )
    vendor_part_number = Field(
        attribute='vendor_part_number',
        column_name='VendorPartNumber'
    )
    description = Field(
        attribute='description',
        column_name='Description'
    )
    manufacturer = Field(
        attribute='manufacturer',
        column_name='Manufacturer',
        widget=ForeignKeyWidget(
            PremierManufacturer,
            'name'
        )
    )
    msrp = Field(
        attribute='msrp',
        column_name='MSRP',
        widget=RoundedDecimalWidget()
    )
    map = Field(
        attribute='map',
        column_name='MAP',
        widget=RoundedDecimalWidget()
    )
    jobber = Field(
        attribute='jobber',
        column_name='Jobber',
        widget=RoundedDecimalWidget()
    )
    cost = Field(
        attribute='cost',
        column_name='Your Cost',
        widget=RoundedDecimalWidget()
    )
    part_status = Field(
        attribute='part_status',
        column_name='Status'
    )
    weight = Field(
        attribute='weight',
        column_name='Weight (lbs)',
        widget=RoundedDecimalWidget()
    )
    length = Field(
        attribute='length',
        column_name='Length (in)',
        widget=RoundedDecimalWidget()
    )
    width = Field(
        attribute='width',
        column_name='Width (in)',
        widget=RoundedDecimalWidget()
    )
    height = Field(
        attribute='height',
        column_name='Height (in)',
        widget=RoundedDecimalWidget()
    )
    upc = Field(
        attribute='upc',
        column_name='UPC'
    )

    class Meta:
        model = PremierProduct
        import_id_fields = ('premier_part_number',)
        fields = (
            'premier_part_number',
            'vendor_part_number',
            'description',
            'manufacturer',
            'msrp',
            'map',
            'jobber',
            'cost',
            'part_status',
            'weight',
            'length',
            'width',
            'height',
            'upc'
        )
        skip_unchanged = True
        report_skipped = False
