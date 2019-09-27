# Generated by Django 2.2.5 on 2019-09-26 22:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0005_update_product_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='premierproduct',
            name='inventory_ab',
            field=models.IntegerField(blank=True, null=True, verbose_name='Alberta inventory'),
        ),
        migrations.AddField(
            model_name='premierproduct',
            name='inventory_ca',
            field=models.IntegerField(blank=True, null=True, verbose_name='California inventory'),
        ),
        migrations.AddField(
            model_name='premierproduct',
            name='inventory_co',
            field=models.IntegerField(blank=True, null=True, verbose_name='Colorado inventory'),
        ),
        migrations.AddField(
            model_name='premierproduct',
            name='inventory_ky',
            field=models.IntegerField(blank=True, null=True, verbose_name='Kentucky inventory'),
        ),
        migrations.AddField(
            model_name='premierproduct',
            name='inventory_po',
            field=models.IntegerField(blank=True, null=True, verbose_name='PO inventory'),
        ),
        migrations.AddField(
            model_name='premierproduct',
            name='inventory_tx',
            field=models.IntegerField(blank=True, null=True, verbose_name='Texas inventory'),
        ),
        migrations.AddField(
            model_name='premierproduct',
            name='inventory_ut',
            field=models.IntegerField(blank=True, null=True, verbose_name='Utah inventory'),
        ),
        migrations.AddField(
            model_name='premierproduct',
            name='inventory_wa',
            field=models.IntegerField(blank=True, null=True, verbose_name='Washington inventory'),
        ),
    ]
