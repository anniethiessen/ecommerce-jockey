# Generated by Django 2.2.5 on 2019-09-28 22:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0018_remove_dataset_years'),
    ]

    operations = [
        migrations.AlterField(
            model_name='premierproduct',
            name='description',
            field=models.CharField(max_length=500),
        ),
        migrations.AlterField(
            model_name='premierproduct',
            name='manufacturer',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='semabrand',
            name='brand_id',
            field=models.CharField(max_length=10, primary_key=True, serialize=False, unique=True),
        ),
        migrations.AlterField(
            model_name='semadataset',
            name='dataset_id',
            field=models.PositiveIntegerField(primary_key=True, serialize=False, unique=True),
        ),
        migrations.AlterField(
            model_name='semadataset',
            name='name',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='semamake',
            name='make_id',
            field=models.PositiveIntegerField(primary_key=True, serialize=False, unique=True),
        ),
        migrations.AlterField(
            model_name='semamodel',
            name='base_vehicle_id',
            field=models.PositiveIntegerField(unique=True),
        ),
        migrations.AlterField(
            model_name='semamodel',
            name='model_id',
            field=models.PositiveIntegerField(primary_key=True, serialize=False, unique=True),
        ),
        migrations.AlterField(
            model_name='semaproduct',
            name='product_id',
            field=models.PositiveIntegerField(primary_key=True, serialize=False, unique=True),
        ),
        migrations.AlterField(
            model_name='semasubmodel',
            name='submodel_id',
            field=models.PositiveIntegerField(primary_key=True, serialize=False, unique=True),
        ),
        migrations.AlterField(
            model_name='semasubmodel',
            name='vehicle_id',
            field=models.PositiveIntegerField(unique=True),
        ),
    ]