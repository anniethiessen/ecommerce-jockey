# Generated by Django 2.2.5 on 2019-10-08 22:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0028_remove_semamodel_make'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='semasubmodel',
            name='model',
        ),
        migrations.RemoveField(
            model_name='semasubmodel',
            name='vehicle_id',
        ),
    ]
