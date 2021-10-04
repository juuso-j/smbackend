# Generated by Django 3.2.5 on 2021-08-30 04:43

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eco_counter', '0020_auto_20210827_1342'),
    ]

    operations = [
        migrations.AddField(
            model_name='day',
            name='day_number',
            field=models.PositiveSmallIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(7)]),
        ),
        migrations.AddField(
            model_name='weekday',
            name='day_number',
            field=models.PositiveSmallIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(7)]),
        ),
    ]