# Generated by Django 3.2.6 on 2021-09-28 10:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('mockup', '0014_rename_contet_type_unit_content_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='unit',
            name='content_id',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='unit',
            name='content_type_short_name',
            field=models.CharField(choices=[('CGS', 'ChargingStation'), ('GFS', 'GasFillingStation')], max_length=3, null=True),
        ),
        migrations.AlterField(
            model_name='unit',
            name='content_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype'),
        ),
        migrations.DeleteModel(
            name='ContentType',
        ),
    ]
