# Generated by Django 2.2.5 on 2019-11-11 20:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0011_category_group_unique'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='premier_product',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='item', to='premier.PremierProduct'),
        ),
    ]