# Generated by Django 2.2.5 on 2019-10-22 21:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0058_delete_manufacturer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='sema_product',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='products', to='product.SemaProduct', verbose_name='SEMA product'),
        ),
    ]