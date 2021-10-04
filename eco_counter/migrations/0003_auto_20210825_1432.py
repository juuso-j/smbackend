# Generated by Django 3.2.5 on 2021-08-25 11:32

import django.contrib.postgres.fields
import django.core.validators
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('eco_counter', '0002_auto_20210825_1225'),
    ]

    operations = [
        migrations.AddField(
            model_name='weekday',
            name='date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='weekday',
            name='values_ak',
            field=models.PositiveSmallIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='weekday',
            name='values_ap',
            field=models.PositiveSmallIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='weekday',
            name='values_at',
            field=models.PositiveSmallIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='weekday',
            name='values_jk',
            field=models.PositiveSmallIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='weekday',
            name='values_jp',
            field=models.PositiveSmallIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='weekday',
            name='values_jt',
            field=models.PositiveSmallIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='weekday',
            name='values_pk',
            field=models.PositiveSmallIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='weekday',
            name='values_pp',
            field=models.PositiveSmallIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='weekday',
            name='values_pt',
            field=models.PositiveSmallIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='day',
            name='date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='day',
            name='values_ak',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.PositiveSmallIntegerField(), default=list, size=None),
        ),
        migrations.AlterField(
            model_name='day',
            name='values_ap',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.PositiveSmallIntegerField(), default=list, size=None),
        ),
        migrations.AlterField(
            model_name='day',
            name='values_at',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.PositiveSmallIntegerField(), default=list, size=None),
        ),
        migrations.AlterField(
            model_name='day',
            name='values_jk',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.PositiveSmallIntegerField(), default=list, size=None),
        ),
        migrations.AlterField(
            model_name='day',
            name='values_jp',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.PositiveSmallIntegerField(), default=list, size=None),
        ),
        migrations.AlterField(
            model_name='day',
            name='values_jt',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.PositiveSmallIntegerField(), default=list, size=None),
        ),
        migrations.AlterField(
            model_name='day',
            name='values_pk',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.PositiveSmallIntegerField(), default=list, size=None),
        ),
        migrations.AlterField(
            model_name='day',
            name='values_pp',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.PositiveSmallIntegerField(), default=list, size=None),
        ),
        migrations.AlterField(
            model_name='day',
            name='values_pt',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.PositiveSmallIntegerField(), default=list, size=None),
        ),
        migrations.AlterField(
            model_name='importstate',
            name='rows_imported',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='month',
            name='month_number',
            field=models.PositiveSmallIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(12)]),
        ),
        migrations.AlterField(
            model_name='month',
            name='year',
            field=models.PositiveSmallIntegerField(choices=[(2019, 2019), (2020, 2020), (2021, 2021)], default=2021),
        ),
        migrations.AlterField(
            model_name='week',
            name='week_number',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(53)]),
        ),
        migrations.AlterField(
            model_name='week',
            name='year',
            field=models.PositiveSmallIntegerField(choices=[(2019, 2019), (2020, 2020), (2021, 2021)], default=2021),
        ),
        migrations.AlterField(
            model_name='year',
            name='year',
            field=models.PositiveSmallIntegerField(choices=[(2019, 2019), (2020, 2020), (2021, 2021)], default=2021),
        ),
    ]