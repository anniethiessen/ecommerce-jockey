# Generated by Django 2.2.5 on 2019-11-16 02:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopify', '0021_shopifymetafield'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shopifymetafield',
            name='value_type',
            field=models.CharField(choices=[('string', 'string'), ('integer', 'integer'), ('json_string', 'json')], default='string', max_length=15),
        ),
    ]