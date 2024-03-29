# Generated by Django 2.2.5 on 2019-11-14 19:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('shopify', '0016_shopifymetafield'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shopifymetafield',
            name='content_type',
            field=models.ForeignKey(limit_choices_to=models.Q(models.Q(('app_label', 'shopify'), ('model', 'shopifyproduct')), models.Q(('app_label', 'shopify'), ('model', 'shopifycollection')), _connector='OR'), on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType'),
        ),
        migrations.AlterField(
            model_name='shopifymetafield',
            name='object_id',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterUniqueTogether(
            name='shopifymetafield',
            unique_together={('content_type', 'object_id', 'owner_resource', 'namespace', 'key')},
        ),
        migrations.RemoveField(
            model_name='shopifymetafield',
            name='product',
        ),
    ]
