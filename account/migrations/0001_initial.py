# Generated by Django 2.1.2 on 2018-11-01 13:52

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0009_alter_user_last_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='email address')),
                ('user_id', models.CharField(max_length=255, unique=True, verbose_name='user name')),
                ('gender', models.SmallIntegerField(choices=[(0, '남자'), (1, '여자')], verbose_name='성별')),
                ('birth', models.IntegerField(verbose_name='생년월일6자리')),
                ('skin_color', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(blank=True, null=True), blank=True, null=True, size=None, verbose_name='피부톤')),
                ('face_point', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(blank=True, null=True), blank=True, null=True, size=None, verbose_name='특징')),
                ('favorite_makeup', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(blank=True, null=True), blank=True, null=True, size=None, verbose_name='관심있는 메이크업')),
                ('is_staff', models.BooleanField(default=False, verbose_name='스태프 권한')),
                ('is_active', models.BooleanField(default=True, help_text='이 사용자가 활성화되어 있는지를 나타냅니다. 계정을 삭제하는 대신 이것을 선택 해제하세요.', verbose_name='활성')),
                ('date_joined', models.DateTimeField(auto_now_add=True, verbose_name='가입일')),
                ('user_type', models.IntegerField(choices=[(0, 'standard'), (1, 'kakao'), (2, 'facebook')], default=0, verbose_name='사용자 타입')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': '사용자 정보',
                'verbose_name_plural': '사용자 정보',
                'ordering': ('id',),
            },
        ),
    ]
