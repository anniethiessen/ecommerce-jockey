# Generated by Django 2.2.5 on 2019-09-28 03:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0015_semabasevehicle_semamake_semamodel_semasubmodel_semavehicle_semayear'),
    ]

    operations = [
        migrations.AddField(
            model_name='semadataset',
            name='years',
            field=models.ManyToManyField(blank=True, null=True, related_name='sema_datasets', to='product.SemaYear'),
        ),
    ]