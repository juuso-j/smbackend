# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-01-26 14:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0040_translate_unitontologyworddetails'),
    ]

    operations = [
        migrations.AlterField(
            model_name='unit',
            name='provider_type',
            field=models.PositiveSmallIntegerField(choices=[(1, 'SELF_PRODUCED'), (2, 'MUNICIPALITY'), (3, 'ASSOCIATION'), (4, 'PRIVATE_COMPANY'), (5, 'OTHER_PRODUCTION_METHOD'), (6, 'PURCHASED_SERVICE'), (7, 'UNKNOWN_PRODUCTION_METHOD'), (8, 'CONTRACT_SCHOOL'), (9, 'SUPPORTED_OPERATIONS'), (10, 'PAYMENT_COMMITMENT'), (11, 'VOUCHER_SERVICE')], null=True),
        ),
        migrations.AlterUniqueTogether(
            name='unitontologyworddetails',
            unique_together=set([('period_begin_year', 'unit', 'ontologyword', 'clarification_fi')]),
        ),
    ]