# Generated by Django 3.2.6 on 2021-09-28 09:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mockup', '0011_auto_20210928_1220'),
    ]

    operations = [
        migrations.AlterField(
            model_name='unit',
            name='contet_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='units', to='mockup.contenttype'),
        ),
    ]