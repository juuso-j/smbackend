# Generated by Django 3.2.6 on 2021-09-24 10:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mockup', '0004_alter_unit_content_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gasfillingstationcontent',
            name='unit',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='gas_filling_station_content', to='mockup.unit'),
        ),
    ]
