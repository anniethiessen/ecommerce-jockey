# Generated by Django 2.2.5 on 2019-10-08 04:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0025_semaproduct_html'),
    ]

    operations = [
        migrations.AlterField(
            model_name='semamodel',
            name='make',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='models', to='product.SemaMake'),
        ),
        migrations.AlterField(
            model_name='semasubmodel',
            name='model',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submodels', to='product.SemaModel'),
        ),
    ]
