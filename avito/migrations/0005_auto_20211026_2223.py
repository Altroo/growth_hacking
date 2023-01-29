# Generated by Django 3.2.8 on 2021-10-26 22:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('avito', '0004_auto_20211026_0002'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='boutique',
            options={'ordering': ('added_date',), 'verbose_name': '1 - Boutique', 'verbose_name_plural': '1 - Boutiques'},
        ),
        migrations.AlterModelOptions(
            name='particulier',
            options={'ordering': ('added_date',), 'verbose_name': '0 - Particulier', 'verbose_name_plural': '0 - Particuliers'},
        ),
        migrations.AlterModelOptions(
            name='particulierproduit',
            options={'ordering': ('date_published',), 'verbose_name': '0 - Annonce Particulier', 'verbose_name_plural': '0 - Annonces Particulier'},
        ),
        migrations.AlterModelOptions(
            name='produit',
            options={'ordering': ('date_published',), 'verbose_name': '1 - Produit', 'verbose_name_plural': '1 - Produits'},
        ),
    ]