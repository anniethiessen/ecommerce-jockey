# Generated by Django 2.2.5 on 2019-10-28 05:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sema', '0031_semadescriptionpiesattribute'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='semadescriptionpiesattribute',
            unique_together={('product', 'segment')},
        ),
    ]
