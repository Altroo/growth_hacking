# Generated by Django 3.2.9 on 2021-11-01 23:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jiji', '0002_jiji_country'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jiji',
            name='country',
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name='Country'),
        ),
    ]