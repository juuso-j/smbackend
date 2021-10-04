# Generated by Django 3.2.5 on 2021-09-01 06:26

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eco_counter', '0024_auto_20210830_1325'),
    ]

    operations = [
        migrations.AddField(
            model_name='importstate',
            name='current_week_number',
            field=models.PositiveSmallIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(53)]),
        ),
    ]