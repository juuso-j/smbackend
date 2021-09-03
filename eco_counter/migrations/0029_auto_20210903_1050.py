# Generated by Django 3.2.5 on 2021-09-03 07:50

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('eco_counter', '0028_auto_20210903_1020'),
    ]

    operations = [
        migrations.CreateModel(
            name='Day',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value_ak', models.PositiveIntegerField(default=0)),
                ('value_ap', models.PositiveIntegerField(default=0)),
                ('value_at', models.PositiveIntegerField(default=0)),
                ('value_pk', models.PositiveIntegerField(default=0)),
                ('value_pp', models.PositiveIntegerField(default=0)),
                ('value_pt', models.PositiveIntegerField(default=0)),
                ('value_jk', models.PositiveIntegerField(default=0)),
                ('value_jp', models.PositiveIntegerField(default=0)),
                ('value_jt', models.PositiveIntegerField(default=0)),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('day_number', models.PositiveSmallIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(7)])),
                ('month', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='days', to='eco_counter.month')),
                ('station', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='days', to='eco_counter.station')),
                ('week', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='days', to='eco_counter.week')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.DeleteModel(
            name='WeekDay',
        ),
    ]
