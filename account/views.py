from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.views import APIView
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from .serializers import *
from .models import *


@api_view(["POST"])
def login(request):
    """
    로그인
    보낼 데이터는 다음과 같습니다.
    post:
    form-data
    user_id : email or user_id
    password
    """
    user_id = request.data.get("user_id")
    password = request.data.get("password")

    try:
       # Try to fetch the user by searching the user_id or email field
        user = User.objects.get(Q(user_id=user_id)|Q(email=user_id))
        if user.check_password(password):
            serializer = AccountSerializer(user)
            data = {"result": 1, "user": user.pk, "user_id": user.user_id, "email": user.email}
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            data = {
                "result": -2,
                "msg": '비밀번호를 다시 확인해주세요.',
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
    except User.DoesNotExist:
        # Run the default password hasher once to reduce the timing
        # difference between an existing and a non-existing user (#20760).
        data = {
            "result": 0,
            "msg": '존재하지 않는 ID 입니다.',
        }
        return Response(data, status=status.HTTP_400_BAD_REQUEST)

class UserCreate(generics.CreateAPIView):

    """
    사용자를 등록합니다.
    보낼 데이터는 다음과 같습니다.
    post:
    회원 가입
    {
        "user_type":"0(standard),1(kakao), 2(facebook)",
        "user_id":"test,"email":"a@gmail.com",
        "password":"a1234",
        "birth":"020101",
        "skin_color":"1,2,3" (1, '밝은'), (2, '중간'), (3, '어두운'), (4, '웜톤'), (5, '쿨톤'), (6, '모름')
        "face_point":"1,2,3"(1, '무쌍'), (2, '속쌍'), (3, '겉쌍'), (4, '잡티'), (5, '다크서클'), (6, '홍조'), (7, '건조함'), (8, '번들거림'), (9, '칙칙함')
        "favorite_makeup":"1,2,3"(1, '데일리룩'), (2, '스모키'), (3, '무쌍메이크업'), (4, '음영메이크업'), (5, '복숭아메이크업'), (6, '아이라인')
    }
    """
    serializer_class = AccountSerializer

    def post(self, request, format='json'):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            dict = serializer.errors

            if 'email' in dict:
                if dict['email'][0] == "유효한 이메일 주소를 입력하십시오.":
                    data = {"result": -1, "msg": '유효한 이메일 주소를 입력하십시오.'}
                elif dict['email'][0] == "사용자 정보의 이메일 주소은/는 이미 존재합니다.":
                    data = {"result": -1, "msg": '사용자 정보의 이메일 주소는 이미 존재합니다.'}
                else:
                    data = {"result": -3, "msg": serializer.errors}
            elif 'user_id' in dict:
                if dict['user_id'][0] == "영문/숫자만 입력해주세요.":
                    data = {"result": 0, "msg": '영문/숫자만 입력해주세요.'}
                elif dict['user_id'][0] == "사용자 정보의 사용자 이름은/는 이미 존재합니다..":
                    data = {"result": 0, "msg": '사용자 정보의 사용자 이름은 이미 존재합니다.'}
                else:
                    data = {"result": -3, "msg": serializer.errors}
            elif 'password' in dict:
                if '비밀번호가 너무 짧습니다.' in dict['password'][0]:
                    data = {"result": -3, "msg": '비밀번호가 너무 짧습니다. 최소 8 문자를 포함해야 합니다.'}
                elif '비밀번호가 너무 일상적인 단어입니다.' in dict['password'][0]:
                    data = {"result": -3, "msg": '비밀번호가 너무 일상적인 단어입니다.'}
                elif '비밀번호는 적어도  하나의 숫자를 포함해야합니다.' in dict['password'][0]:
                    data = {"result": -3, "msg": '비밀번호는 적어도  하나의 숫자를 포함해야합니다.'}
                elif '비밀번호가 너무 일상적인 단어입니다.' in dict['password'][0]:
                    data = {"result": -3, "msg": '비밀번호가 너무 일상적인 단어입니다.'}
                else:
                    data = {"result": -3, "msg": serializer.errors}
            else:
                data = {
                    "result": 0,
                    "msg": serializer.errors
                }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

class ChangePassword(APIView):
    """
    An endpoint for changing password.
    """
    def get_object(self):

        try:
            user = User.objects.get(pk=self.request.data.get("pk"))
            return user
        except User.DoesNotExist:
            data = {"result": -1, "msg": '등록된 아이디가 없습니다.'}
            raise serializers.ValidationError(data)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            old_password = serializer.data.get("old_password")
            if not self.object.check_password(old_password):
                data = {"result": -1, "msg": '기존 비밀번호가 다릅니다.'}
                return Response(data,status=status.HTTP_400_BAD_REQUEST)
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            data = {"result": 1, "msg": '비밀번호가 변경되었습니다.'}
            return Response(data, status=status.HTTP_200_OK)
        else:
            dict = serializer.errors

            if 'new_password' in dict:
                data = {"result": -2, "msg": "비밀번호는 8자 이상 영문/숫자가 필요합니다."}
            else:
                data = serializer.errors
            return Response(data, status=status.HTTP_400_BAD_REQUEST)


class FollowSet(APIView):

    def post(self, request, *args, **kwargs):
        try:
            following = User.objects.get(user_id=self.request.data.get("following"))
        except User.DoesNotExist:
            data = {"result": -1, "msg": 'following 등록된 아이디가 없습니다.'}
            return Response(data, status=status.HTTP_200_OK)

        try:
            follower = User.objects.get(user_id=self.request.data.get("follower"))
        except User.DoesNotExist:
            data = {"result": -1, "msg": 'follower 등록된 아이디가 없습니다.'}
            return Response(data, status=status.HTTP_200_OK)

        follow, created = Follow.objects.get_or_create(following=following, follower=follower)

        if created:
            data = {'message': '팔로우 시작','result': 1}
        else:
            follow.delete()
            data = {'message': '팔로우 취소', 'result': 0 }
        return Response(data, status=status.HTTP_200_OK)




class ResetPassword(APIView):
    """

    """
    serializer_class = EmailSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        # find a user by email address (case insensitive search)
        users = User.objects.filter(email__iexact=email)

        active_user_found = False

        for user in users:
            if user.is_active and user.has_usable_password():
                active_user_found = True

        if not active_user_found:
            data = {"result": -1, "msg": '사용자정보가 존재하지 않습니다.'}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        if active_user_found :
            # send an e-mail to the user
            random_password = User.objects.make_random_password(length=8,
                                                                allowed_chars="abcdefghjkmnpqrstuvwxyz01234567889")
            user.set_password(random_password)
            user.save()
            context = {
                'user_id': user.user_id,
                'password': random_password
            }

            # render email text
            email_html_message = render_to_string('email/user_reset_password.html', context)
            # Create an e-mail
            email_message = EmailMultiAlternatives(
                subject=_("BeauTOTAL에 문의하신 비밀번호 정보 입니다."),
                body=email_html_message,
                from_email=settings.EMAIL_HOST_USER,
                to=[user.email]
            )

            email_message.attach_alternative(email_html_message, "text/html")

            try:
                email_message.send()
                return Response({'result': 1, "msg": '이메일 발송이 완료되었습니다.'})
            except:
                data = {"result": 0, "msg": '이메일 발송 시 오류가 발생했습니다.'}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)