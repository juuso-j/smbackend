# Generated by Django 3.2.6 on 2021-09-27 07:33

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mockup', '0008_alter_geometry_geometry'),
    ]

    operations = [
        migrations.AlterField(
            model_name='geometry',
            name='geometry',
            field=django.contrib.gis.db.models.fields.GeometryField(null=True, srid=3067),
        ),
    ]
