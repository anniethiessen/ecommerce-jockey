# Generated by Django 2.2.5 on 2019-12-03 17:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sema', '0051_sema_pies'),
    ]

    operations = [
        migrations.AlterField(
            model_name='semadigitalassetspiesattribute',
            name='value',
            field=models.URLField(max_length=500),
        ),
    ]
