# Generated by Django 3.2.6 on 2021-10-04 07:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_view', '0002_unitgroup_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='unitgroup',
            name='description',
            field=models.TimeField(null=True),
        ),
    ]
