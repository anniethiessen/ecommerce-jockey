# Generated by Django 2.2.5 on 2019-10-28 06:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sema', '0032_semadescriptionpiesattribute_unique'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='semadescriptionpiesattribute',
            options={'verbose_name': 'SEMA description PIES'},
        ),
        migrations.AlterUniqueTogether(
            name='semadescriptionpiesattribute',
            unique_together=set(),
        ),
    ]