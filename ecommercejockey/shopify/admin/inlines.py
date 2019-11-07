from django.contrib.admin import (
    StackedInline,
    TabularInline
)

from core.admin.forms import LimitedInlineFormSet
from core.admin.utils import (
    get_change_view_link,
    get_changelist_view_link,
    # get_image_preview
)
from ..models import (
    ShopifyCollection,
    ShopifyImage,
    ShopifyMetafield,
    ShopifyOption,
    ShopifyProduct,
    ShopifyVariant
)


class ShopifyVendorProductsTabularInline(TabularInline):
    model = ShopifyProduct
    fk_name = 'vendor'
    formset = LimitedInlineFormSet
    verbose_name_plural = 'products (top 10)'
    all_link_query = 'vendor__id__exact'
    extra = 0
    ordering = (
        'title',
    )
    classes = (
        'collapse',
    )

    fields = (
        'all_link',
        'details_link',
        'id',
        'product_id',
        'title',
        'vendor',
        'is_published'
    )

    readonly_fields = (
        'id',
        'details_link',
        'all_link'
    )

    def get_rel_obj(self, obj):
        return getattr(obj, self.fk_name)

    def all_link(self, obj):
        if not obj:
            return None
        query = f'{self.all_link_query}={getattr(self.get_rel_obj(obj), "pk")}'
        return get_changelist_view_link(obj, 'See All', query)
    all_link.short_description = ''

    def details_link(self, obj):
        if not obj:
            return None
        return get_change_view_link(obj, 'Details')
    details_link.short_description = ''

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'vendor':
            formfield.choices = formfield.choices
        return formfield

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if not request.user.is_superuser:
            readonly_fields += (
                'product_id',
            )
        return readonly_fields


class ShopifyProductImagesTabularInline(TabularInline):
    model = ShopifyImage
    fk_name = 'product'
    verbose_name_plural = 'images'
    all_link_query = 'product__id__exact'
    extra = 0
    classes = (
        'collapse',
    )

    fields = (
        'all_link',
        'details_link',
        'id',
        'product',
        'src'
    )

    readonly_fields = (
        'id',
        'details_link',
        'all_link'
    )

    def get_rel_obj(self, obj):
        return getattr(obj, self.fk_name)

    def all_link(self, obj):
        query = f'{self.all_link_query}={getattr(self.get_rel_obj(obj), "pk")}'
        return get_changelist_view_link(obj, 'See All', query)
    all_link.short_description = ''

    def details_link(self, obj):
        if not obj.pk:
            return None
        return get_change_view_link(obj, 'Details')
    details_link.short_description = ''

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'product':
            formfield.choices = formfield.choices
        return formfield


class ShopifyProductOptionsTabularInline(TabularInline):
    model = ShopifyOption
    fk_name = 'product'
    verbose_name_plural = 'options'
    all_link_query = 'product__id__exact'
    extra = 0
    classes = (
        'collapse',
    )

    fields = (
        'all_link',
        'details_link',
        'id',
        'option_id',
        'product',
        'name',
        'values'
    )

    readonly_fields = (
        'id',
        'details_link',
        'all_link'
    )

    def get_rel_obj(self, obj):
        return getattr(obj, self.fk_name)

    def all_link(self, obj):
        query = f'{self.all_link_query}={getattr(self.get_rel_obj(obj), "pk")}'
        return get_changelist_view_link(obj, 'See All', query)
    all_link.short_description = ''

    def details_link(self, obj):
        if not obj.pk:
            return None
        return get_change_view_link(obj, 'Details')
    details_link.short_description = ''

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'product':
            formfield.choices = formfield.choices
        return formfield

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if not request.user.is_superuser:
            readonly_fields += (
                'option_id',
            )
        return readonly_fields


class ShopifyProductVariantsStackedInline(StackedInline):
    model = ShopifyVariant
    verbose_name_plural = 'variants'
    extra = 0

    fieldsets = (
        (
            'Variant', {
                'fields': (
                    'variant_id',
                    'title',
                    ('sku', 'sku_match__', 'sku__'),
                    ('barcode', 'barcode_match__', 'barcode__')
                )
            }
        ),
        (
            'Weight', {
                'fields': (
                    'grams',
                    ('weight', 'weight_match__', 'weight__'),
                    ('weight_unit', 'weight_unit_match__', 'weight_unit__')
                )
            }
        ),
        (
            'Pricing', {
                'fields': (
                    ('price', 'price_match__', 'price__'),
                    'compare_at_price',
                    ('cost', 'cost_match__', 'cost__')
                )
            }
        ),
        (
            'Taxes', {
                'fields': (
                    'is_taxable',
                    'tax_code'
                )
            }
        ),
        (
            'Inventory & Fulfillment', {
                'fields': (
                    'inventory_management',
                    'inventory_policy',
                    'fulfillment_service'
                )
            }
        )
    )

    readonly_fields = (
        'sku__',
        'sku_match__',
        'barcode__',
        'barcode_match__',
        'weight__',
        'weight_match__',
        'weight_unit__',
        'weight_unit_match__',
        'price__',
        'price_match__',
        'cost__',
        'cost_match__'
    )

    def sku_match__(self, obj):
        return bool(obj.sku == obj.product.calculator.sku_)
    sku_match__.boolean = True
    sku_match__.short_description = ''

    def sku__(self, obj):
        if self.sku_match__(obj):
            return ''
        return obj.product.calculator.sku_
    sku__.short_description = ''

    def barcode_match__(self, obj):
        return bool(obj.barcode == obj.product.calculator.barcode_)
    barcode_match__.boolean = True
    barcode_match__.short_description = ''

    def barcode__(self, obj):
        if self.barcode_match__(obj):
            return ''
        return obj.product.calculator.barcode_
    barcode__.short_description = ''

    def weight_match__(self, obj):
        return bool(obj.weight == obj.product.calculator.weight_)
    weight_match__.boolean = True
    weight_match__.short_description = ''

    def weight__(self, obj):
        if self.weight_match__(obj):
            return ''
        return obj.product.calculator.weight_
    weight__.short_description = ''

    def weight_unit_match__(self, obj):
        return bool(obj.weight_unit == obj.product.calculator.weight_unit_)
    weight_unit_match__.boolean = True
    weight_unit_match__.short_description = ''

    def weight_unit__(self, obj):
        if self.weight_unit_match__(obj):
            return ''
        return obj.product.calculator.weight_unit_
    weight_unit__.short_description = ''

    def price_match__(self, obj):
        return bool(obj.price == obj.product.calculator.price_)
    price_match__.boolean = True
    price_match__.short_description = ''

    def price__(self, obj):
        if self.price_match__(obj):
            return ''
        return obj.product.calculator.price_
    price__.short_description = ''

    def cost_match__(self, obj):
        return bool(obj.cost == obj.product.calculator.cost_)
    cost_match__.boolean = True
    cost_match__.short_description = ''

    def cost__(self, obj):
        if self.cost_match__(obj):
            return ''
        return obj.product.calculator.cost_
    cost__.short_description = ''

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if not request.user.is_superuser:
            readonly_fields += (
                'variant_id',
            )
        return readonly_fields


class ShopifyProductMetafieldsTabularInline(TabularInline):
    model = ShopifyMetafield
    fk_name = 'product'
    verbose_name_plural = 'metafields'
    all_link_query = 'product__id__exact'
    extra = 0
    classes = (
        'collapse',
    )

    fields = (
        'all_link',
        'details_link',
        'id',
        'metafield_id',
        'product',
        'owner_resource',
        'namespace',
        'value_type',
        'key'
    )

    readonly_fields = (
        'id',
        'details_link',
        'all_link'
    )

    def get_rel_obj(self, obj):
        return getattr(obj, self.fk_name)

    def all_link(self, obj):
        query = f'{self.all_link_query}={getattr(self.get_rel_obj(obj), "pk")}'
        return get_changelist_view_link(obj, 'See All', query)
    all_link.short_description = ''

    def details_link(self, obj):
        if not obj.pk:
            return None
        return get_change_view_link(obj, 'Details')
    details_link.short_description = ''

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'product':
            formfield.choices = formfield.choices
        return formfield

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if not request.user.is_superuser:
            readonly_fields += (
                'metafield_id',
            )
        return readonly_fields


class ShopifyTagProductsManyToManyTabularInline(TabularInline):
    model = ShopifyProduct.tags.through
    fk_name = 'shopifytag'
    extra = 0


class ShopifyProductTagsManyToManyTabularInline(TabularInline):
    verbose_name_plural = 'Tags'
    model = ShopifyProduct.tags.through
    fk_name = 'shopifyproduct'
    extra = 0
    classes = (
        'collapse',
    )


class ShopifyCollectionTagsManyToManyTabularInline(TabularInline):
    model = ShopifyCollection.tags.through
    fk_name = 'shopifycollection'
    extra = 0


class ShopifyCollectionRulesManyToManyTabularInline(TabularInline):
    model = ShopifyCollection.rules.through
    fk_name = 'shopifycollection'
    extra = 0


class ShopifyTagCollectionsManyToManyTabularInline(TabularInline):
    model = ShopifyCollection.tags.through
    fk_name = 'shopifytag'
    extra = 0


class ShopifyRuleCollectionsManyToManyTabularInline(TabularInline):
    model = ShopifyCollection.rules.through
    fk_name = 'shopifycollectionrule'
    extra = 0
