# Generated by Django 2.2.5 on 2019-10-28 07:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sema', '0033_semadescriptionpiesattribute_meta'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='semaproduct',
            name='pies_c10_des',
        ),
    ]
