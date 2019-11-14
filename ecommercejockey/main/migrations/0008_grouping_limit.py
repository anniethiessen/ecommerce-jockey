# Generated by Django 2.2.5 on 2019-11-11 06:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_grouping'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grouping',
            name='content_type',
            field=models.ForeignKey(limit_choices_to=models.Q(models.Q(('app_label', 'sema'), ('model', 'semabasevehicle')), models.Q(('app_label', 'sema'), ('model', 'semavehicle')), models.Q(('app_label', 'sema'), ('model', 'semacategory')), _connector='OR'), on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType', verbose_name='content type'),
        ),
    ]