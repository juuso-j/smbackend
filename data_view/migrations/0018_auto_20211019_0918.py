# Generated by Django 3.2.6 on 2021-10-19 06:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data_view', '0017_auto_20211015_1252'),
    ]

    operations = [
        migrations.RenameField(
            model_name='chargingstationcontent',
            old_name='unit',
            new_name='mobile_unit',
        ),
        migrations.RenameField(
            model_name='gasfillingstationcontent',
            old_name='unit',
            new_name='mobile_unit',
        ),
        migrations.RenameField(
            model_name='statuecontent',
            old_name='unit',
            new_name='mobile_unit',
        ),
        migrations.RenameField(
            model_name='walkingroutecontent',
            old_name='unit',
            new_name='mobile_unit',
        ),
    ]