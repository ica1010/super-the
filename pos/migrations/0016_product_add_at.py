# Generated by Django 5.0 on 2024-10-22 13:15

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pos', '0015_remove_product_date_avaries'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='add_at',
            field=models.DateField(auto_created=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
