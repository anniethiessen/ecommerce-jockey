# Generated by Django 2.2.5 on 2019-10-12 07:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0033_semacategory'),
    ]

    operations = [
        migrations.AddField(
            model_name='semayear',
            name='is_authorized',
            field=models.BooleanField(default=False, help_text='brand has given access to dataset'),
        ),
    ]
