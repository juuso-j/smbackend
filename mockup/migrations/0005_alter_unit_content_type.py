# Generated by Django 3.2.6 on 2021-09-21 11:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('mockup', '0004_alter_unit_content_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='unit',
            name='content_type',
            field=models.ForeignKey(blank=True, limit_choices_to=models.Q(('model', 'charginstationcontent'), ('model', 'gasstationcontent'), ('model', 'routecontent'), ('model', 'parkingareacontent'), _connector='OR'), null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype'),
        ),
    ]
