# Generated by Django 2.2.5 on 2019-10-25 06:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='vendor',
            name='is_relevant',
            field=models.BooleanField(default=False),
        ),
    ]