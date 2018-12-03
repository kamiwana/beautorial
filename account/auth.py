# -*- coding: utf-8 -*-

from django.db.models import Q
from .models import *
from rest_framework import HTTP_HEADER_ENCODING


class user_idOrEmailBackend(object):
    def authenticate(self, user_id=None, password=None, **kwargs):
        try:
           # Try to fetch the user by searching the user_id or email field
            user = User.objects.get(Q(user_id=user_id)|Q(email=user_id))
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a non-existing user (#20760).
            User().set_password(password)

from rest_framework import exceptions
from django.contrib.auth import get_user_model
import jwt
import time

User = get_user_model()
JWT_SECRET = 'beautorial'


def get_authorization_header(request):

    auth = request.META.get('HTTP_AUTHORIZATION', b'')

    if isinstance(auth, type('')):
        auth = auth.encode(HTTP_HEADER_ENCODING)
    return auth


class MyTokenAuthentication():

    def authenticate(self, request):
        token = get_authorization_header(request)

        if not token:
            return None
        # token 디코딩
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])

        # token 만료 확인
        expire = payload.get('expire')

        if int(time.time()) > expire:
            return None

        # user 객체

        login_user = payload.get('user')

        if not login_user:
            return None

        try:
            user = User.objects.get(pk=login_user)

        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('No such user')

        return (user, token)