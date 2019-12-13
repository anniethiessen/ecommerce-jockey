# Generated by Django 2.2.5 on 2019-12-13 02:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopify', '0033_shopifycollectioncalculator'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shopifycollectioncalculator',
            name='metafield_value_collection_family_choice',
            field=models.CharField(choices=[('shopify_collection_collection_family_value', 'Shopify Collection Family'), ('custom_collection_family_metafield_value_value', 'Custom Collection Family Metafield Value')], default='shopify_collection_collection_family_value', max_length=50),
        ),
    ]
