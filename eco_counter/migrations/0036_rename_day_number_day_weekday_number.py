# Generated by Django 3.2.6 on 2021-09-09 09:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('eco_counter', '0035_auto_20210908_0910'),
    ]

    operations = [
        migrations.RenameField(
            model_name='day',
            old_name='day_number',
            new_name='weekday_number',
        ),
    ]
