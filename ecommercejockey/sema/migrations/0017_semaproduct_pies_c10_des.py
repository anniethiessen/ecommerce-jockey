# Generated by Django 2.2.5 on 2019-10-27 06:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sema', '0016_semaproduct_pies_c10_ext'),
    ]

    operations = [
        migrations.RenameField(
            model_name='semaproduct',
            old_name='pies_c10_tle',
            new_name='pies_c10_des',
        ),
    ]
