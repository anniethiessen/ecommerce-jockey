from django.contrib.admin import (
    StackedInline,
    TabularInline
)
from django.contrib.contenttypes.admin import GenericTabularInline

from core.admin.forms import LimitedInlineFormSet
from core.admin.utils import (
    get_change_view_link,
    get_changelist_view_link,
    # get_image_preview
)
from ..models import (
    ShopifyCollection,
    ShopifyCollectionCalculator,
    ShopifyImage,
    ShopifyMetafield,
    ShopifyOption,
    ShopifyProduct,
    ShopifyProductCalculator,
    ShopifyVariant
)


class ShopifyMetafieldBaseTabularInline(GenericTabularInline):  # TODO
    model = ShopifyMetafield
    verbose_name_plural = 'metafields'
    extra = 0
    classes = (
        'collapse',
    )

    fields = (
        'all_link',
        'details_link',
        'id',
        'metafield_id',
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

    def all_link(self, obj):
        query = (
            f'object_id__exact={obj.object_id}'
            f'&content_type_id__exact={obj.content_type.pk}'
        )
        return get_changelist_view_link(obj, 'See All', query)
    all_link.short_description = ''

    def details_link(self, obj):
        if not obj.pk:
            return None
        return get_change_view_link(obj, 'Details')
    details_link.short_description = ''

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'content_type':
            formfield.choices = formfield.choices
        return formfield

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if not request.user.is_superuser:
            readonly_fields += (
                'metafield_id',
            )
        return readonly_fields


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
                    'sku',
                    'barcode'
                )
            }
        ),
        (
            'Weight', {
                'fields': (
                    'grams',
                    'weight',
                    'weight_unit'
                )
            }
        ),
        (
            'Pricing', {
                'fields': (
                    'price',
                    'compare_at_price',
                    'cost',
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

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if not request.user.is_superuser:
            readonly_fields += (
                'variant_id',
            )
        return readonly_fields


class ShopifyProductCalculatorStackedInline(StackedInline):
    model = ShopifyProductCalculator
    verbose_name_plural = 'calculator'
    extra = 0
    classes = (
        'collapse',
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    'details_link',
                    ('title_match', 'title_difference'),
                    'title_option',
                    ('body_html_match', 'body_html_difference'),
                    'body_html_option',
                    ('variant_weight_match', 'variant_weight_difference'),
                    'variant_weight_option',
                    ('variant_weight_unit_match', 'variant_weight_unit_difference'),
                    'variant_weight_unit_option',
                    ('variant_cost_match', 'variant_cost_difference'),
                    'variant_cost_option',
                    ('variant_price_match', 'variant_price_difference'),
                    'variant_price_base_option',
                    'variant_price_markup_option',
                    ('variant_sku_match', 'variant_sku_difference'),
                    'variant_sku_option',
                    ('variant_barcode_match', 'variant_barcode_difference'),
                    'variant_barcode_option',
                    ('metafields_match', 'metafields_difference'),
                    'metafields_packaging_option',
                    'metafields_fitments_option',
                    ('tags_match', 'tags_difference'),
                    'tags_vendor_option',
                    'tags_categories_option',
                    ('images_match', 'images_difference'),
                    'images_option'
                )
            }
        ),
    )

    readonly_fields = (
        'details_link',
        'title_match',
        'body_html_match',
        'variant_weight_match',
        'variant_weight_unit_match',
        'variant_cost_match',
        'variant_price_match',
        'variant_sku_match',
        'variant_barcode_match',
        'metafields_match',
        'tags_match',
        'images_match',
        'title_difference',
        'body_html_difference',
        'variant_weight_difference',
        'variant_weight_unit_difference',
        'variant_cost_difference',
        'variant_price_difference',
        'variant_sku_difference',
        'variant_barcode_difference',
        'metafields_difference',
        'tags_difference',
        'images_difference'
    )

    def details_link(self, obj):
        if not obj:
            return None
        return get_change_view_link(obj, 'See Full Calculator')
    details_link.short_description = ''


class ShopifyProductMetafieldsTabularInline(ShopifyMetafieldBaseTabularInline):
    pass


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


class ShopifyCollectionCalculatorStackedInline(StackedInline):
    model = ShopifyCollectionCalculator
    verbose_name_plural = 'calculator'
    extra = 0
    classes = (
        'collapse',
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    'details_link',
                    ('title_match', 'title_difference'),
                    'title_option',
                    ('metafields_match', 'metafields_difference'),
                    'metafields_display_name_option',
                    'metafields_subcollections_option',
                    ('tags_match', 'tags_difference'),
                    'tags_categories_option'
                )
            }
        ),
    )

    readonly_fields = (
        'details_link',
        'title_match',
        'metafields_match',
        'tags_match',
        'title_difference',
        'metafields_difference',
        'tags_difference'
    )

    def details_link(self, obj):
        if not obj:
            return None
        return get_change_view_link(obj, 'See Full Calculator')
    details_link.short_description = ''


class ShopifyCollectionChildCollectionsTabularInline(TabularInline):
    model = ShopifyCollection
    fk_name = 'parent_collection'
    verbose_name_plural = 'child collections'
    all_link_query = 'parent_collection__id__exact'
    extra = 0
    classes = (
        'collapse',
    )

    fields = (
        'all_link',
        'details_link',
        'id',
        'collection_id',
        'title',
        'body_html',
        'handle'
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

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if not request.user.is_superuser:
            readonly_fields += (
                'collection_id',
                'handle'
            )
        return readonly_fields


class ShopifyCollectionTagsManyToManyTabularInline(TabularInline):
    model = ShopifyCollection.tags.through
    fk_name = 'shopifycollection'
    extra = 0


class ShopifyCollectionRulesManyToManyTabularInline(TabularInline):
    model = ShopifyCollection.rules.through
    fk_name = 'shopifycollection'
    extra = 0


class ShopifyCollectionMetafieldsTabularInline(ShopifyMetafieldBaseTabularInline):
    pass


class ShopifyTagCollectionsManyToManyTabularInline(TabularInline):
    model = ShopifyCollection.tags.through
    fk_name = 'shopifytag'
    extra = 0


class ShopifyRuleCollectionsManyToManyTabularInline(TabularInline):
    model = ShopifyCollection.rules.through
    fk_name = 'shopifycollectionrule'
    extra = 0
