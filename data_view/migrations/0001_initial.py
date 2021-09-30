# Generated by Django 3.2.6 on 2021-09-30 04:55

import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ContentTypes',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('type_name', models.CharField(choices=[('CGS', 'ChargingStation'), ('GFS', 'GasFillingStation')], max_length=3, null=True)),
                ('name', models.CharField(max_length=32, null=True)),
                ('class_name', models.CharField(max_length=32, null=True)),
                ('description', models.TextField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('is_active', models.BooleanField(default=True)),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('content_type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='units', to='data_view.contenttypes')),
            ],
        ),
        migrations.CreateModel(
            name='Geometry',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('geometry', django.contrib.gis.db.models.fields.GeometryField(null=True, srid=3067)),
                ('unit', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='geometries', to='data_view.unit')),
            ],
        ),
        migrations.CreateModel(
            name='GasFillingStationContent',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, null=True)),
                ('address', models.CharField(max_length=100, null=True)),
                ('lng_cng', models.CharField(max_length=10, null=True)),
                ('operator', models.CharField(max_length=30, null=True)),
                ('unit', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='gas_filling_station_content', to='data_view.unit')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ChargingStationContent',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, null=True)),
                ('address', models.CharField(max_length=100, null=True)),
                ('url', models.URLField(null=True)),
                ('charger_type', models.CharField(max_length=30, null=True)),
                ('unit', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='charging_station_content', to='data_view.unit')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
