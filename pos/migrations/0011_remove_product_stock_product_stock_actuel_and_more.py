# Generated by Django 5.0 on 2024-10-18 14:52

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pos', '0010_caissegenerale_caissehistorique_delete_caissejournal_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='stock',
        ),
        migrations.AddField(
            model_name='product',
            name='stock_actuel',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='product',
            name='stock_initial',
            field=models.IntegerField(default=0),
        ),
        migrations.CreateModel(
            name='FicheStock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stock_initial', models.IntegerField(default=0)),
                ('stock_actuel', models.IntegerField(default=0)),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
                ('dernier_mouvement', models.DateTimeField(auto_now=True)),
                ('produit', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='pos.product')),
            ],
        ),
        migrations.CreateModel(
            name='Inventaire',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_inventaire', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='InventaireDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stock_physique', models.IntegerField()),
                ('stock_systeme', models.IntegerField()),
                ('inventaire', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pos.inventaire')),
                ('produit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pos.product')),
            ],
        ),
        migrations.AddField(
            model_name='inventaire',
            name='produits_inventories',
            field=models.ManyToManyField(through='pos.InventaireDetail', to='pos.product'),
        ),
        migrations.CreateModel(
            name='MouvementStock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type_mouvement', models.CharField(choices=[('ENTRÉE', 'Entrée'), ('SORTIE', 'Sortie')], max_length=6)),
                ('quantite', models.PositiveIntegerField()),
                ('date_mouvement', models.DateTimeField(auto_now_add=True)),
                ('produit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mouvements', to='pos.product')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
