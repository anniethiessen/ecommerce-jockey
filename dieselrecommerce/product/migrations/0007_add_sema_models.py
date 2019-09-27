# Generated by Django 2.2.5 on 2019-09-27 02:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0006_add_product_inventory_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='SemaBrand',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('brand_id', models.CharField(blank=True, max_length=10, null=True)),
                ('name', models.CharField(blank=True, max_length=50, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SemaDataset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dataset_id', models.CharField(blank=True, max_length=10, null=True)),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('brand', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sema_datasets', to='product.SemaBrand')),
            ],
        ),
        migrations.CreateModel(
            name='SemaProduct',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dataset', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sema_products', to='product.SemaDataset')),
                ('product', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='sema_product', to='product.Product')),
            ],
        ),
    ]
