# Generated by Django 3.2.6 on 2021-09-17 04:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('eco_counter', '0036_rename_day_number_day_weekday_number'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='station',
            options={'ordering': ['id']},
        ),
        migrations.AlterModelOptions(
            name='week',
            options={'ordering': ['-week_number']},
        ),
        migrations.AlterModelOptions(
            name='weekdata',
            options={'ordering': ['-week__week_number']},
        ),
    ]