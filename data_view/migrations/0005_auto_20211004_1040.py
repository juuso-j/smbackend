# Generated by Django 3.2.6 on 2021-10-04 07:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data_view', '0004_auto_20211004_1039'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chargingstationcontent',
            name='name',
        ),
        migrations.RemoveField(
            model_name='gasfillingstationcontent',
            name='name',
        ),
        migrations.RemoveField(
            model_name='statuecontent',
            name='name',
        ),
        migrations.RemoveField(
            model_name='walkingroutecontent',
            name='name',
        ),
    ]
