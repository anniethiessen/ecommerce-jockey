# Generated by Django 2.2.5 on 2019-10-27 16:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sema', '0018_semaproduct_pies_c10_ext'),
    ]

    operations = [
        migrations.AddField(
            model_name='semaproduct',
            name='primary_image_url',
            field=models.URLField(blank=True),
        ),
    ]
