# Generated by Django 2.2.5 on 2019-10-24 21:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('premier', '0003_premierproduct_vendor_part_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='premiermanufacturer',
            name='is_relevant',
            field=models.BooleanField(default=False),
        ),
    ]