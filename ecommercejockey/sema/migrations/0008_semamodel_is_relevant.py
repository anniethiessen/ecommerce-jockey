# Generated by Django 2.2.5 on 2019-10-25 16:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sema', '0007_semamake_is_relevant'),
    ]

    operations = [
        migrations.AddField(
            model_name='semamodel',
            name='is_relevant',
            field=models.BooleanField(default=False),
        ),
    ]
