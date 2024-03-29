# Generated by Django 2.2.5 on 2019-11-26 00:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0014_remove_categorypath_shopify_collections'),
    ]

    operations = [
        migrations.AddField(
            model_name='categorypath',
            name='relevancy_exceptions',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='item',
            name='relevancy_exceptions',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='vendor',
            name='relevancy_exceptions',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='item',
            name='premier_product',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='item', to='premier.PremierProduct'),
        ),
        migrations.AlterField(
            model_name='item',
            name='sema_product',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='item', to='sema.SemaProduct', verbose_name='SEMA product'),
        ),
    ]
