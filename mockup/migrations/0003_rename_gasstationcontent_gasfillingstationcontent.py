# Generated by Django 3.2.6 on 2021-09-24 09:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mockup', '0002_alter_geometry_unit'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='GasStationContent',
            new_name='GasFillingStationContent',
        ),
    ]