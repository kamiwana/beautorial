# Generated by Django 2.1.2 on 2018-11-08 01:56

import django.core.validators
from django.db import migrations, models
import re


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0026_auto_20181108_1055'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='icon',
            field=models.CharField(blank=True, choices=[(1, '밝은'), (2, '중간'), (3, '어두운'), (4, '웜톤'), (5, '쿨톤'), (6, '모름')], max_length=100, validators=[django.core.validators.RegexValidator(re.compile('^\\d+(?:\\,\\d+)*\\Z'), code='invalid', message='Enter only digits separated by commas.')]),
        ),
    ]
