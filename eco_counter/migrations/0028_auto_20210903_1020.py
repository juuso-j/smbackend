# Generated by Django 3.2.5 on 2021-09-03 07:20

import django.contrib.postgres.fields
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('eco_counter', '0027_weekday_month'),
    ]

    operations = [
        migrations.CreateModel(
            name='HourData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('day_number', models.PositiveSmallIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(7)])),
                ('values_ak', django.contrib.postgres.fields.ArrayField(base_field=models.PositiveSmallIntegerField(), default=list, size=None)),
                ('values_ap', django.contrib.postgres.fields.ArrayField(base_field=models.PositiveSmallIntegerField(), default=list, size=None)),
                ('values_at', django.contrib.postgres.fields.ArrayField(base_field=models.PositiveSmallIntegerField(), default=list, size=None)),
                ('values_pk', django.contrib.postgres.fields.ArrayField(base_field=models.PositiveSmallIntegerField(), default=list, size=None)),
                ('values_pp', django.contrib.postgres.fields.ArrayField(base_field=models.PositiveSmallIntegerField(), default=list, size=None)),
                ('values_pt', django.contrib.postgres.fields.ArrayField(base_field=models.PositiveSmallIntegerField(), default=list, size=None)),
                ('values_jk', django.contrib.postgres.fields.ArrayField(base_field=models.PositiveSmallIntegerField(), default=list, size=None)),
                ('values_jp', django.contrib.postgres.fields.ArrayField(base_field=models.PositiveSmallIntegerField(), default=list, size=None)),
                ('values_jt', django.contrib.postgres.fields.ArrayField(base_field=models.PositiveSmallIntegerField(), default=list, size=None)),
                ('month', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='hour_data', to='eco_counter.month')),
                ('station', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hour_data', to='eco_counter.station')),
                ('week', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='hour_data', to='eco_counter.week')),
            ],
        ),
        migrations.DeleteModel(
            name='Day',
        ),
    ]