# Generated by Django 3.2.6 on 2021-09-21 11:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mockup', '0009_rename_object_id_unit_content_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='unit',
            old_name='content_id',
            new_name='object_id',
        ),
    ]
