# Generated by Django 3.2.6 on 2021-09-27 10:24

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('eco_counter', '0039_alter_station_geom'),
    ]

    operations = [
        migrations.AlterField(
            model_name='station',
            name='geom',
            field=django.contrib.gis.db.models.fields.PointField(srid=3067),
        ),
    ]