# Generated by Django 3.2.6 on 2021-10-01 07:59

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
                ('name', models.CharField(max_length=64, null=True)),
                ('class_name', models.CharField(max_length=64, null=True)),
                ('description', models.TextField(null=True)),
                ('type_name', models.CharField(choices=[('CGS', 'ChargingStation'), ('GFS', 'GasFillingStation'), ('WGR', 'WalkingRoute'), ('STE', 'Statue')], max_length=3, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='GroupTypes',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=64, null=True)),
                ('class_name', models.CharField(max_length=64, null=True)),
                ('description', models.TextField(null=True)),
                ('type_name', models.CharField(choices=[('CER', 'CultureRoute')], max_length=3, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('is_active', models.BooleanField(default=True)),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('geometry', django.contrib.gis.db.models.fields.GeometryField(null=True, srid=3067)),
                ('content_type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='units', to='data_view.contenttypes')),
            ],
            options={
                'ordering': ['created_time'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='WalkingRouteContent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
                ('unit', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='walking_route_content', to='data_view.unit')),
            ],
        ),
        migrations.CreateModel(
            name='UnitGroup',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('is_active', models.BooleanField(default=True)),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('group_type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='unit_groups', to='data_view.grouptypes')),
            ],
            options={
                'ordering': ['created_time'],
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='unit',
            name='unit_group',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='units', to='data_view.unitgroup'),
        ),
        migrations.CreateModel(
            name='StatueContent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, null=True)),
                ('description', models.TextField(null=True)),
                ('unit', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='statue_content', to='data_view.unit')),
            ],
        ),
        migrations.CreateModel(
            name='GasFillingStationContent',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=64, null=True)),
                ('address', models.CharField(max_length=128, null=True)),
                ('lng_cng', models.CharField(max_length=8, null=True)),
                ('operator', models.CharField(max_length=32, null=True)),
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
                ('name', models.CharField(max_length=64, null=True)),
                ('address', models.CharField(max_length=128, null=True)),
                ('url', models.URLField(null=True)),
                ('charger_type', models.CharField(max_length=32, null=True)),
                ('unit', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='charging_station_content', to='data_view.unit')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
