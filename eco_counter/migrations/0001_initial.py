# Generated by Django 3.2.5 on 2021-08-25 07:01

import datetime
import django.contrib.gis.db.models.fields
import django.contrib.postgres.fields
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Day',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=datetime.date(2021, 8, 25))),
                ('values_ak', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), default=list, size=24)),
                ('values_ap', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), default=list, size=24)),
                ('values_at', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), default=list, size=24)),
                ('values_pk', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), default=list, size=24)),
                ('values_pp', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), default=list, size=24)),
                ('values_pt', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), default=list, size=24)),
                ('values_jk', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), default=list, size=24)),
                ('values_jp', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), default=list, size=24)),
                ('values_jt', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), default=list, size=24)),
            ],
        ),
        migrations.CreateModel(
            name='ImportState',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rows_imported', models.IntegerField(default=0)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('geom', django.contrib.gis.db.models.fields.PointField(srid=4326)),
            ],
        ),
        migrations.CreateModel(
            name='Month',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='WeekDay',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Year',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Week',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('week', models.IntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(53)])),
                ('days', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='week', to='eco_counter.day')),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='weeks', to='eco_counter.location')),
            ],
        ),
        migrations.AddField(
            model_name='day',
            name='location',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='days', to='eco_counter.location'),
        ),
    ]
