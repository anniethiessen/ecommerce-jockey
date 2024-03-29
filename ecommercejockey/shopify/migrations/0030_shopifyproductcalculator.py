# Generated by Django 2.2.5 on 2019-12-08 05:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopify', '0029_shopifyproductcalculator'),
    ]

    operations = [
        migrations.RenameField(
            model_name='shopifyproductcalculator',
            old_name='variant_price_markup_option',
            new_name='variant_price_markup_choice',
        ),
        migrations.RenameField(
            model_name='shopifyproductcalculator',
            old_name='variant_weight_unit_option',
            new_name='variant_weight_unit_choice',
        ),
        migrations.RemoveField(
            model_name='shopifyproductcalculator',
            name='body_html_option',
        ),
        migrations.RemoveField(
            model_name='shopifyproductcalculator',
            name='images_option',
        ),
        migrations.RemoveField(
            model_name='shopifyproductcalculator',
            name='metafields_fitments_option',
        ),
        migrations.RemoveField(
            model_name='shopifyproductcalculator',
            name='metafields_packaging_option',
        ),
        migrations.RemoveField(
            model_name='shopifyproductcalculator',
            name='tags_categories_option',
        ),
        migrations.RemoveField(
            model_name='shopifyproductcalculator',
            name='tags_vendor_option',
        ),
        migrations.RemoveField(
            model_name='shopifyproductcalculator',
            name='title_option',
        ),
        migrations.RemoveField(
            model_name='shopifyproductcalculator',
            name='variant_barcode_option',
        ),
        migrations.RemoveField(
            model_name='shopifyproductcalculator',
            name='variant_cost_option',
        ),
        migrations.RemoveField(
            model_name='shopifyproductcalculator',
            name='variant_price_base_option',
        ),
        migrations.RemoveField(
            model_name='shopifyproductcalculator',
            name='variant_sku_option',
        ),
        migrations.RemoveField(
            model_name='shopifyproductcalculator',
            name='variant_weight_option',
        ),
        migrations.AddField(
            model_name='shopifyproductcalculator',
            name='body_html_choice',
            field=models.CharField(choices=[('sema_description_def_value', 'SEMA DEF Description'), ('sema_description_des_value', 'SEMA DES Description'), ('sema_description_inv_value', 'SEMA INV Description'), ('sema_description_ext_value', 'SEMA EXT Description'), ('sema_description_tle_value', 'SEMA TLE Description'), ('sema_description_sho_value', 'SEMA SHO Description'), ('sema_description_mkt_value', 'SEMA MKT Description'), ('sema_description_key_value', 'SEMA KEY Description'), ('sema_description_asc_value', 'SEMA ASC Description'), ('sema_description_asm_value', 'SEMA ASM Description'), ('sema_description_fab_value', 'SEMA FAB Description'), ('sema_description_lab_value', 'SEMA LAB Description'), ('sema_description_shp_value', 'SEMA SHP Description'), ('sema_description_oth_value', 'SEMA OTH Description'), ('premier_description_value', 'Premier Description'), ('custom_body_html_value', 'Custom Body HTML')], default='sema_description_ext_value', max_length=50),
        ),
        migrations.AddField(
            model_name='shopifyproductcalculator',
            name='body_html_custom_value',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='shopifyproductcalculator',
            name='image_urls_premier_choice',
            field=models.CharField(choices=[('premier_primary_image_urls_value', 'Premier Primary Image URLs'), ('custom_premier_image_urls_value', 'Custom Premier Image URLs')], default='premier_primary_image_urls_value', max_length=50),
        ),
        migrations.AddField(
            model_name='shopifyproductcalculator',
            name='image_urls_premier_custom_value',
            field=models.TextField(blank=True, help_text='format: [""]'),
        ),
        migrations.AddField(
            model_name='shopifyproductcalculator',
            name='image_urls_sema_choice',
            field=models.CharField(choices=[('sema_filtered_image_urls_value', 'SEMA Filtered Image URLs'), ('custom_sema_image_urls_value', 'Custom SEMA Image URLs')], default='sema_filtered_image_urls_value', max_length=50),
        ),
        migrations.AddField(
            model_name='shopifyproductcalculator',
            name='image_urls_sema_custom_value',
            field=models.TextField(blank=True, help_text='format: [""]'),
        ),
        migrations.AddField(
            model_name='shopifyproductcalculator',
            name='images_choice',
            field=models.CharField(choices=[('images_dict_all_value', 'All Images'), ('images_dict_sema_value', 'SEMA Images'), ('images_dict_premier_value', 'Premier Images'), ('images_dict_custom_value', 'Custom Images')], default='images_dict_sema_value', max_length=50),
        ),
        migrations.AddField(
            model_name='shopifyproductcalculator',
            name='images_custom_value',
            field=models.TextField(blank=True, help_text='[{"link"}]'),
        ),
        migrations.AddField(
            model_name='shopifyproductcalculator',
            name='metafield_value_fitments_choice',
            field=models.CharField(choices=[('sema_vehicles_value', 'SEMA Vehicles'), ('custom_fitments_metafield_value_value', 'Custom Fitments Metafield Value')], default='sema_vehicles_value', max_length=50),
        ),
        migrations.AddField(
            model_name='shopifyproductcalculator',
            name='metafield_value_fitments_custom_value',
            field=models.TextField(blank=True, help_text='format: [{"year", "make", "model", "submodel"}]', verbose_name='Custom Fitments Metafields'),
        ),
        migrations.AddField(
            model_name='shopifyproductcalculator',
            name='metafield_value_packaging_choice',
            field=models.CharField(choices=[('sema_html_value', 'SEMA HTML'), ('custom_packaging_metafield_value_value', 'Custom Packaging Metafield Value')], default='sema_html_value', max_length=50),
        ),
        migrations.AddField(
            model_name='shopifyproductcalculator',
            name='metafield_value_packaging_custom_value',
            field=models.TextField(blank=True, help_text='format: <html>...</html>'),
        ),
        migrations.AddField(
            model_name='shopifyproductcalculator',
            name='metafields_choice',
            field=models.CharField(choices=[('metafields_dict_all_value', 'All Metafields'), ('metafields_dict_packaging_value', 'Packaging Metafields'), ('metafields_dict_fitments_value', 'Fitments Metafields'), ('metafields_dict_custom_value', 'Custom Metafields')], default='metafields_dict_all_value', max_length=50),
        ),
        migrations.AddField(
            model_name='shopifyproductcalculator',
            name='metafields_custom_value',
            field=models.TextField(blank=True, help_text='format: [{"namespace", "key": "owner_resource", "value", "value_type"}]'),
        ),
        migrations.AddField(
            model_name='shopifyproductcalculator',
            name='tag_names_collection_choice',
            field=models.CharField(choices=[('sema_category_tag_names_value', 'SEMA Category Tag Names'), ('custom_collection_tag_names_value', 'Custom Collection Tag Names')], default='sema_category_tag_names_value', max_length=50),
        ),
        migrations.AddField(
            model_name='shopifyproductcalculator',
            name='tag_names_collection_custom_value',
            field=models.TextField(blank=True, help_text='format: [""]'),
        ),
        migrations.AddField(
            model_name='shopifyproductcalculator',
            name='tag_names_vendor_choice',
            field=models.CharField(choices=[('sema_brand_tag_names_value', 'SEMA Brand Tag Names'), ('custom_vendor_tag_names_value', 'Custom Vendor Tag Names')], default='sema_brand_tag_names_value', max_length=50),
        ),
        migrations.AddField(
            model_name='shopifyproductcalculator',
            name='tag_names_vendor_custom_value',
            field=models.TextField(blank=True, help_text='format: [""]'),
        ),
        migrations.AddField(
            model_name='shopifyproductcalculator',
            name='tags_choice',
            field=models.CharField(choices=[('tags_dict_all_value', 'All Tags'), ('tags_dict_vendor_value', 'Vendor Tags'), ('tags_dict_collection_value', 'Collection Tags'), ('tags_dict_custom_value', 'Custom Tags')], default='tags_dict_all_value', max_length=50),
        ),
        migrations.AddField(
            model_name='shopifyproductcalculator',
            name='tags_custom_value',
            field=models.TextField(blank=True, help_text='format: [{"name"}]'),
        ),
        migrations.AddField(
            model_name='shopifyproductcalculator',
            name='title_choice',
            field=models.CharField(choices=[('sema_description_def_value', 'SEMA PIES Description'), ('sema_description_des_value', 'SEMA DES Description'), ('sema_description_inv_value', 'SEMA INV Description'), ('sema_description_ext_value', 'SEMA EXT Description'), ('sema_description_tle_value', 'SEMA TLE Description'), ('sema_description_sho_value', 'SEMA SHO Description'), ('sema_description_mkt_value', 'SEMA MKT Description'), ('sema_description_key_value', 'SEMA KEY Description'), ('sema_description_asc_value', 'SEMA ASC Description'), ('sema_description_asm_value', 'SEMA ASM Description'), ('sema_description_fab_value', 'SEMA FAB Description'), ('sema_description_lab_value', 'SEMA LAB Description'), ('sema_description_shp_value', 'SEMA SHP Description'), ('sema_description_oth_value', 'SEMA OTH Description'), ('premier_description_value', 'Premier Description'), ('custom_title_value', 'Custom Title')], default='sema_description_sho_value', max_length=50),
        ),
        migrations.AddField(
            model_name='shopifyproductcalculator',
            name='title_custom_value',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='shopifyproductcalculator',
            name='variant_barcode_choice',
            field=models.CharField(choices=[('premier_upc_value', 'Premier UPC'), ('custom_variant_barcode_value', 'Custom Barcode')], default='premier_upc_value', max_length=50),
        ),
        migrations.AddField(
            model_name='shopifyproductcalculator',
            name='variant_barcode_custom_value',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='shopifyproductcalculator',
            name='variant_cost_choice',
            field=models.CharField(choices=[('premier_cost_cad_value', 'Premier Cost CAD'), ('premier_cost_usd_value', 'Premier Cost USD'), ('custom_variant_cost_value', 'Custom Cost')], default='premier_cost_cad_value', max_length=50),
        ),
        migrations.AddField(
            model_name='shopifyproductcalculator',
            name='variant_cost_custom_value',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='shopifyproductcalculator',
            name='variant_price_base_choice',
            field=models.CharField(choices=[('premier_cost_cad_value', 'Premier Cost CAD'), ('premier_cost_usd_value', 'Premier Cost USD'), ('custom_variant_price_base_value', 'Custom Price Base')], default='premier_cost_cad_value', max_length=50),
        ),
        migrations.AddField(
            model_name='shopifyproductcalculator',
            name='variant_price_base_custom_value',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='shopifyproductcalculator',
            name='variant_sku_choice',
            field=models.CharField(choices=[('premier_premier_part_number_value', 'Premier Part Number'), ('custom_variant_sku_value', 'Custom SKU')], default='premier_premier_part_number_value', max_length=50),
        ),
        migrations.AddField(
            model_name='shopifyproductcalculator',
            name='variant_sku_custom_value',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='shopifyproductcalculator',
            name='variant_weight_choice',
            field=models.CharField(choices=[('premier_weight_value', 'Premier Weight'), ('custom_variant_weight_value', 'Custom Weight')], default='premier_weight_value', max_length=50),
        ),
        migrations.AddField(
            model_name='shopifyproductcalculator',
            name='variant_weight_custom_value',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='shopifyvariant',
            name='sku',
            field=models.CharField(blank=True, max_length=50, verbose_name='SKU'),
        ),
    ]
