# Generated by Django 2.2.5 on 2019-12-05 22:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopify', '0028_shopifycollectionrule_column'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shopifyproductcalculator',
            name='body_html_option',
            field=models.CharField(choices=[('sema_description_def_value', 'SEMA Definition'), ('sema_description_des_value', 'SEMA Description'), ('sema_description_inv_value', 'SEMA Invoice'), ('sema_description_ext_value', 'SEMA Extended'), ('sema_description_tle_value', 'SEMA Title'), ('sema_description_sho_value', 'SEMA Short'), ('sema_description_mkt_value', 'SEMA Marketing'), ('sema_description_key_value', 'SEMA Key Words'), ('sema_description_asc_value', 'SEMA ASC'), ('sema_description_asm_value', 'SEMA ASM'), ('sema_description_fab_value', 'SEMA FAB'), ('sema_description_lab_value', 'SEMA LAB'), ('sema_description_shp_value', 'SEMA SHP'), ('sema_description_oth_value', 'SEMA Other'), ('premier_description_value', 'Premier Description'), ('custom_value', 'Custom')], default='sema_description_ext_value', max_length=50),
        ),
        migrations.AlterField(
            model_name='shopifyproductcalculator',
            name='title_option',
            field=models.CharField(choices=[('sema_description_def_value', 'SEMA Definition'), ('sema_description_des_value', 'SEMA Description'), ('sema_description_inv_value', 'SEMA Invoice'), ('sema_description_ext_value', 'SEMA Extended'), ('sema_description_tle_value', 'SEMA Title'), ('sema_description_sho_value', 'SEMA Short'), ('sema_description_mkt_value', 'SEMA Marketing'), ('sema_description_key_value', 'SEMA Key Words'), ('sema_description_asc_value', 'SEMA ASC'), ('sema_description_asm_value', 'SEMA ASM'), ('sema_description_fab_value', 'SEMA FAB'), ('sema_description_lab_value', 'SEMA LAB'), ('sema_description_shp_value', 'SEMA SHP'), ('sema_description_oth_value', 'SEMA Other'), ('premier_description_value', 'Premier Description'), ('custom_value', 'Custom')], default='sema_description_sho_value', max_length=50),
        ),
    ]