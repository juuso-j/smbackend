# Generated by Django 3.2.6 on 2021-10-04 07:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_view', '0005_auto_20211004_1040'),
    ]

    operations = [
        migrations.AddField(
            model_name='unitgroup',
            name='description',
            field=models.TextField(null=True),
        ),
    ]
