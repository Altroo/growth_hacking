# Generated by Django 3.2.9 on 2021-11-16 00:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mubawab', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mubawab',
            name='phone_1',
        ),
        migrations.RemoveField(
            model_name='mubawab',
            name='phone_2',
        ),
        migrations.RemoveField(
            model_name='mubawab',
            name='phone_3',
        ),
        migrations.AddField(
            model_name='mubawab',
            name='phone',
            field=models.CharField(blank=True, max_length=20, null=True, unique=True, verbose_name='Téléphone'),
        ),
        migrations.AddField(
            model_name='mubawabproduit',
            name='type_annonce',
            field=models.CharField(default=None, max_length=255, verbose_name="Type d'annonce"),
        ),
    ]
