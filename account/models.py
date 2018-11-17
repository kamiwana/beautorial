from django.contrib.auth.models import User
from django.db import models
from .choices import *
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin,BaseUserManager
from django.utils.translation import ugettext_lazy as _
from django.core.validators import RegexValidator
from django.contrib.auth import models as auth_models
from django.core.validators import validate_comma_separated_integer_list
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill

class UserManager(auth_models.BaseUserManager):

    def create_user(self, user_id, email, password=None):
        if not email:
            raise ValueError('Users must have an email address')
        if not user_id:
            raise ValueError('Users must have a username')
        user = self.model(
            user_id=user_id,
            email=self.normalize_email(email)
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, user_id, email,  password):
        user = self.create_user(user_id, email, password=password)
        user.is_superuser = user.is_staff = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    userid_regex = RegexValidator(regex=r'^[a-zA-Z0-9]+$', message="영문/숫자만 입력해주세요.")
    user_id = models.CharField(_('username'), validators=[userid_regex], unique=True, max_length=50, blank=False)
    gender = models.SmallIntegerField(choices=GENDER_CHOICES,verbose_name='성별', blank=True, null=True)
    birth = models.IntegerField(verbose_name='생년월일6자리', blank=True, null=True)
    skin_color = models.CharField(validators=[validate_comma_separated_integer_list], max_length=30, blank=True, verbose_name='피부톤')
    face_point = models.CharField(validators=[validate_comma_separated_integer_list], max_length=30, blank=True, verbose_name='특징')
    favorite_makeup = models.CharField(validators=[validate_comma_separated_integer_list], max_length=30, blank=True, verbose_name='관심있는 메이크업')
    is_staff = models.BooleanField(default=False, verbose_name='스태프 권한')
    is_active = models.BooleanField(default=True, verbose_name='활성', help_text='이 사용자가 활성화되어 있는지를 나타냅니다. 계정을 삭제하는 대신 이것을 선택 해제하세요.')
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name='가입일')
    user_type = models.IntegerField(choices=USER_CHOICES, default=0, verbose_name='사용자 타입')
    follow_set = models.ManyToManyField('self',
                                        blank=True,
                                        through='Follow',
                                        related_name='followers',
                                        symmetrical=False,)
    objects = UserManager()

    USERNAME_FIELD = 'user_id'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = '사용자 정보'
        verbose_name_plural = '사용자 정보'
        ordering = ('-id', )

    def __unicode__(self):
        return u'{0} ({1})'.format(self.user_id(), self.email)

    def get_user_id(self):
        return self.user_id

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Sends an email to this User.
        """
        #send_mail(subject, message, from_email, [self.email], **kwargs)

    @property
    def get_follower(self):
        return [i.following for i in self.follower_user.all()]

    @property
    def get_following(self):
        return [i.follower for i in self.follow_user.all()]

    @property
    def follower_count(self):
        return len(self.get_follower)

    @property
    def following_count(self):
        return len(self.get_following)

    def is_follower(self, user):
        return user in self.get_follower

    def is_following(self, user):
        return user in self.get_following

def user_path(instance, filename):
    from random import choice
    import string
    arr = [choice(string.ascii_letters) for _ in range(8)]
    pid = ''.join(arr)
    extension = filename.split('.')[-1]
    return 'accounts/{}/{}.{}'.format(instance.user.user_id, pid, extension)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    picture = ProcessedImageField(upload_to=user_path,
                                  processors=[ResizeToFill(150, 150)],
                                  format='JPEG',
                                  options={'quality': 90},
                                  blank=True,
                                  )


class Follow(models.Model):
    following = models.ForeignKey(User, related_name='follow_user', on_delete=models.CASCADE)
    follower = models.ForeignKey(User, related_name='follower_user', on_delete=models.CASCADE)
    follow_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{} -> {}".format(self.follower, self.following)

    class Meta:
        unique_together = (
            ('following', 'follower')
        )

import binascii
import os
from django.db import models
from django.utils.translation import ugettext_lazy as _

class ResetPasswordToken(models.Model):
    class Meta:
        verbose_name = _("Password Reset Token")
        verbose_name_plural = _("Password Reset Tokens")

    @staticmethod
    def generate_key():
        """ generates a pseudo random code using os.urandom and binascii.hexlify """
        return binascii.hexlify(os.urandom(32)).decode()

    id = models.AutoField(
        primary_key=True
    )

    user = models.ForeignKey(
        User,
        related_name='ResetPasswordToken',
        on_delete=models.CASCADE,
        verbose_name=_("The User which is associated to this password reset token")
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("When was this token generated")
    )

    # Key field, though it is not the primary key of the model
    key = models.CharField(
        _("Key"),
        max_length=64,
        db_index=True,
        unique=True
    )

    ip_address = models.GenericIPAddressField(
        _("The IP address of this session"),
        default="127.0.0.1"
    )
    user_agent = models.CharField(
        max_length=256,
        verbose_name=_("HTTP User Agent"),
        default=""
    )

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(ResetPasswordToken, self).save(*args, **kwargs)

    def __str__(self):
        return "Password reset token for user {user}".format(user=self.user)
