# Generated by Django 5.0 on 2025-03-31 09:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("pos", "0034_orderitem_size"),
    ]

    operations = [
        migrations.RenameField(
            model_name="order",
            old_name="montant_paye",
            new_name="montant_remise",
        ),
        migrations.RenameField(
            model_name="order",
            old_name="montant_restant",
            new_name="relicat",
        ),
    ]
