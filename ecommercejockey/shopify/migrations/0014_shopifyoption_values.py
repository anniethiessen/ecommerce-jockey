# Generated by Django 2.2.5 on 2019-11-07 14:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopify', '0013_shopifyoption'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shopifyoption',
            name='values',
            field=models.CharField(default="['Default Title']", max_length=255),
        ),
    ]
