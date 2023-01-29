# Generated by Django 3.2.8 on 2021-10-28 20:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('opensooq', '0005_alter_opensooqboutiqueproduit_price'),
    ]

    operations = [
        migrations.CreateModel(
            name='OpenSooqParticulier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country', models.CharField(max_length=255, verbose_name='Pays particulier')),
                ('name', models.CharField(max_length=255, verbose_name='Nom utilisateur')),
                ('phone', models.CharField(blank=True, max_length=20, null=True, unique=True, verbose_name='Téléphone')),
                ('city', models.CharField(max_length=150, verbose_name='Ville')),
                ('added_date', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': '1 - OpenSooq Particulier',
                'verbose_name_plural': '1 - OpenSooq Particuliers',
                'ordering': ('added_date',),
            },
        ),
        migrations.AlterField(
            model_name='opensooqboutiqueproduit',
            name='boutique',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='open_sooq_boutique', to='opensooq.opensooqboutique', verbose_name='Boutique'),
        ),
        migrations.CreateModel(
            name='OpenSooqParticulierProduit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField(max_length=2000, verbose_name='Lien produit')),
                ('title', models.CharField(max_length=255, verbose_name='Titre annonce')),
                ('category', models.CharField(max_length=255, verbose_name='Catégorie annonce')),
                ('price', models.PositiveIntegerField(default=0, verbose_name='Prix annonce')),
                ('image_1', models.URLField(blank=True, max_length=2000, null=True, verbose_name='Annonce image 1')),
                ('image_2', models.URLField(blank=True, max_length=2000, null=True, verbose_name='Annonce image 2')),
                ('image_3', models.URLField(blank=True, max_length=2000, null=True, verbose_name='Annonce image 3')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description annonce')),
                ('date_published', models.DateField(verbose_name='Date publication')),
                ('particulier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='open_sooq_particulier', to='opensooq.opensooqparticulier', verbose_name='Particulier')),
            ],
            options={
                'verbose_name': '1 - OpenSooq Particulier ads',
                'verbose_name_plural': '1 - OpenSooq Particulier ads',
                'ordering': ('date_published',),
                'unique_together': {('particulier', 'url')},
            },
        ),
    ]