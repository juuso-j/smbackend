# Generated by Django 3.2.5 on 2021-08-25 12:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('eco_counter', '0003_auto_20210825_1432'),
    ]

    operations = [
        migrations.AddField(
            model_name='weekday',
            name='location',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='weekdays', to='eco_counter.location'),
        ),
    ]
