# Generated by Django 2.2.5 on 2019-11-07 01:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopify', '0010_shopify_integer_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shopifycollection',
            name='collection_id',
            field=models.BigIntegerField(blank=True, help_text='Populated by Shopify', null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='shopifymetafield',
            name='metafield_id',
            field=models.BigIntegerField(blank=True, help_text='Populated by Shopify', null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='shopifyoption',
            name='option_id',
            field=models.BigIntegerField(blank=True, help_text='Populated by Shopify', null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='shopifyproduct',
            name='product_id',
            field=models.BigIntegerField(blank=True, help_text='Populated by Shopify', null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='shopifyvariant',
            name='variant_id',
            field=models.BigIntegerField(blank=True, help_text='Populated by Shopify', null=True, unique=True),
        ),
    ]
