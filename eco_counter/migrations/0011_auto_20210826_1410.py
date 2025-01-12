# Generated by Django 3.2.5 on 2021-08-26 11:10

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eco_counter', '0010_weekdata_location'),
    ]

    operations = [
        migrations.AddField(
            model_name='importstate',
            name='month_number',
            field=models.PositiveSmallIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(12)]),
        ),
        migrations.AddField(
            model_name='importstate',
            name='week_number',
            field=models.PositiveSmallIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(53)]),
        ),
        migrations.AddField(
            model_name='importstate',
            name='year',
            field=models.PositiveSmallIntegerField(choices=[(2019, 2019), (2020, 2020), (2021, 2021)], default=2021),
        ),
    ]
