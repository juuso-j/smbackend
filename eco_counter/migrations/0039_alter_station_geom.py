# Generated by Django 3.2.6 on 2021-09-24 11:21

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('eco_counter', '0038_alter_station_geom'),
    ]

    operations = [
        migrations.AlterField(
            model_name='station',
            name='geom',
            field=django.contrib.gis.db.models.fields.PointField(srid=4326),
        ),
    ]
