# Generated by Django 3.2.5 on 2021-09-01 07:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('eco_counter', '0026_auto_20210901_1001'),
    ]

    operations = [
        migrations.AddField(
            model_name='weekday',
            name='month',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='week_days', to='eco_counter.month'),
        ),
    ]
