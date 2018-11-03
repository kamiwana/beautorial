from django.contrib.auth.models import User
from django.db import models
from .choices import *
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin,BaseUserManager
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import UserManager
from multiselectfield import MultiSelectField

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    username = models.CharField(_('username'), max_length=255, unique=True)
    gender = models.SmallIntegerField(choices=GENDER_CHOICES,verbose_name='성별', blank=True, null=True)
    birth = models.IntegerField(verbose_name='생년월일6자리', blank=True, null=True)
    skin_color = MultiSelectField(choices=SKIN_CHOICES, blank=True, null=True, max_length=30, verbose_name='피부톤')
    face_point = MultiSelectField(choices=FACE_CHOICES, blank=True, null=True, max_length=30, verbose_name='특징')
    favorite_makeup = MultiSelectField(choices=MAKEUP_CHOICES, blank=True, null=True, max_length=30, verbose_name='관심있는 메이크업')
    is_staff = models.BooleanField(default=False, verbose_name='스태프 권한')
    is_active = models.BooleanField(default=True, verbose_name='활성', help_text='이 사용자가 활성화되어 있는지를 나타냅니다. 계정을 삭제하는 대신 이것을 선택 해제하세요.')
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name='가입일')
    user_type = models.IntegerField(choices=USER_CHOICES, default=0, verbose_name='사용자 타입')

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = '사용자 정보'
        verbose_name_plural = '사용자 정보'
        ordering = ('id', )

    def __unicode__(self):
        return u'{0} ({1})'.format(self.username(), self.email)

    def get_username(self):
        return self.username

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Sends an email to this User.
        """
        #send_mail(subject, message, from_email, [self.email], **kwargs)