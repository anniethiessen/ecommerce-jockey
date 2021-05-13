# Generated by Django 2.2.5 on 2019-12-09 22:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopify', '0031_shopifyproductcalculator'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shopifyproductcalculator',
            name='image_urls_sema_choice',
            field=models.CharField(choices=[('sema_digital_asset_image_urls_value', 'SEMA Digital Asset Image URLs'), ('custom_sema_image_urls_value', 'Custom SEMA Image URLs')], default='sema_digital_asset_image_urls_value', max_length=50),
        ),
    ]