# Generated by Django 2.2.5 on 2019-11-26 00:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sema', '0048_semaengine_max_length'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='semabasevehicle',
            name='notes',
        ),
        migrations.RemoveField(
            model_name='semabrand',
            name='notes',
        ),
        migrations.RemoveField(
            model_name='semacategory',
            name='notes',
        ),
        migrations.RemoveField(
            model_name='semadataset',
            name='notes',
        ),
        migrations.RemoveField(
            model_name='semaengine',
            name='notes',
        ),
        migrations.RemoveField(
            model_name='semamake',
            name='notes',
        ),
        migrations.RemoveField(
            model_name='semamakeyear',
            name='notes',
        ),
        migrations.RemoveField(
            model_name='semamodel',
            name='notes',
        ),
        migrations.RemoveField(
            model_name='semaproduct',
            name='notes',
        ),
        migrations.RemoveField(
            model_name='semasubmodel',
            name='notes',
        ),
        migrations.RemoveField(
            model_name='semavehicle',
            name='notes',
        ),
        migrations.RemoveField(
            model_name='semayear',
            name='notes',
        ),
    ]
