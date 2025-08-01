# Generated by Django 5.0 on 2024-10-12 11:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pos', '0004_alter_reapprovisionnement_fournisseur'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reapprovisionnementitem',
            name='prix',
        ),
        migrations.AddField(
            model_name='reapprovisionnementitem',
            name='prix_achat',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='reapprovisionnementitem',
            name='prix_de_vente',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='reapprovisionnementitem',
            name='quantite',
            field=models.PositiveIntegerField(default=1),
        ),
    ]
