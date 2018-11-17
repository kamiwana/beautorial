# Generated by Django 2.1.2 on 2018-11-03 03:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0016_auto_20181102_1836'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='skin_color',
            field=models.CharField(blank=True, choices=[(1, '밝은'), (2, '중간'), (3, '어두운'), (4, '웜톤'), (5, '쿨톤'), (6, '모름')], max_length=100, null=True, verbose_name='피부톤'),
        ),
    ]
