# Generated by Django 2.2.5 on 2019-11-08 19:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sema', '0045_semaengine'),
    ]

    operations = [
        migrations.AlterField(
            model_name='semaengine',
            name='aspiration',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='semaengine',
            name='ignition_system_type',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='semaengine',
            name='manufacturer',
            field=models.CharField(max_length=20),
        ),
    ]
