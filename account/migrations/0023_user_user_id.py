# Generated by Django 2.1.2 on 2018-11-05 09:52

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0017_auto_20181103_1209'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='user_id',
            field=models.CharField(default=1, max_length=50, validators=[django.core.validators.RegexValidator(message='숫자만 입력해주세요.', regex='^[a-zA-Z0-9]+$')], verbose_name='아이디'),
            preserve_default=False,
        ),
    ]
