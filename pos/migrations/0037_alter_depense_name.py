# Generated by Django 5.0 on 2025-04-05 13:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pos", "0036_depense"),
    ]

    operations = [
        migrations.AlterField(
            model_name="depense",
            name="name",
            field=models.CharField(max_length=150, verbose_name="nom de la depense"),
        ),
    ]
