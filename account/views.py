from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework import generics
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.shortcuts import get_object_or_404
from .serializers import *
from .models import *
from rest_framework import status
from rest_framework.response import Response

@api_view(["POST"])
def login(request):
    """

        파라미터
        user_id : email or user_id
        password
        user_type

    METHOD : POST, form-data

    """
    user_id = request.data.get("user_id")
    password = request.data.get("password")

    try:
       # Try to fetch the user by searching the user_id or email field
        user = User.objects.get(Q(user_id=user_id)|Q(email=user_id), is_active=True)
        # user = authenticate(username=user_id, password=password)
        #if user.is_block:
        #    data = {
        #        "result": -3,
        #        "message": '차단된 사용자입니다.',
        #    }
        #    return Response(data, status=status.HTTP_400_BAD_REQUEST)

        if user.check_password(password):

            # token 생성
            token, created = user.get_user_token(user.pk)

            serializer = AccountSerializer(user)

            data = {"result": 1, "token": token.key, "data": serializer.data}
            return Response(data, status=status.HTTP_200_OK)
        else:
            data = {
                "result": -2,
                "message": '비밀번호를 다시 확인해주세요.',
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
    except User.DoesNotExist:
        # Run the default password hasher once to reduce the timing
        # difference between an existing and a non-existing user (#20760).
        data = {
            "result": 0,
            "message": '존재하지 않는 ID 입니다.',
        }
        return Response(data, status=status.HTTP_400_BAD_REQUEST)

class UserCreate(generics.ListCreateAPIView):

    """
    사용자를 등록합니다.

    METHOD : POST, form-data

    회원 가입
    {
        "user_type":"0(standard),1(kakao), 2(facebook)",
        "user_id":"test,
        "email":"a@gmail.com",
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
                # token 생성
                token, created = user.get_user_token(user.pk)

                data = {"result": 1, "token": token.key, "data": serializer.data}
                return Response(data, status=status.HTTP_201_CREATED)
        else:
            dict = serializer.errors

            if 'email' in dict:
                if dict['email'][0] == "유효한 이메일 주소를 입력하십시오.":
                    data = {"result": -1, "message": '유효한 이메일 주소를 입력하십시오.'}
                elif dict['email'][0] == "사용자 정보의 이메일 주소은/는 이미 존재합니다.":
                    data = {"result": -1, "message": '사용자 정보의 이메일 주소는 이미 존재합니다.'}
                else:
                    data = {"result": -3, "message": serializer.errors}
            elif 'user_id' in dict:
                if dict['user_id'][0] == "영문/숫자만 입력해주세요.":
                    data = {"result": 0, "message": '영문/숫자만 입력해주세요.'}
                elif dict['user_id'][0] == "사용자 정보의 사용자 이름은/는 이미 존재합니다..":
                    data = {"result": 0, "message": '사용자 정보의 사용자 이름은 이미 존재합니다.'}
                else:
                    data = {"result": -3, "message": serializer.errors}
            elif 'password' in dict:
                if '비밀번호가 너무 짧습니다.' in dict['password'][0]:
                    data = {"result": -3, "message": '비밀번호가 너무 짧습니다. 최소 8 문자를 포함해야 합니다.'}
                elif '비밀번호가 너무 일상적인 단어입니다.' in dict['password'][0]:
                    data = {"result": -3, "message": '비밀번호가 너무 일상적인 단어입니다.'}
                elif '비밀번호는 적어도  하나의 숫자를 포함해야합니다.' in dict['password'][0]:
                    data = {"result": -3, "message": '비밀번호는 적어도  하나의 숫자를 포함해야합니다.'}
                elif '비밀번호가 너무 일상적인 단어입니다.' in dict['password'][0]:
                    data = {"result": -3, "message": '비밀번호가 너무 일상적인 단어입니다.'}
                else:
                    data = {"result": -3, "message": serializer.errors}
            else:
                data = {
                    "result": 0,
                    "message": serializer.errors
                }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
def myuser_get(request, pk):
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        data = {"result": -1, "message": '등록된 아이디가 없습니다.'}
        raise serializers.ValidationError(data)

    serializer = AccountSerializer(user)
    return Response(serializer.data)

#@permission_classes((IsAuthenticated,))
@api_view(['GET'])
def user_get(request, pk):

    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        data = {"result": -1, "message": '등록된 아이디가 없습니다.'}
        raise serializers.ValidationError(data)

    serializer = AccountViewSerializer(user)
    return Response(serializer.data)

@api_view(['POST'])
def user_update(request):
    user_pk = request.data.get('user', None)
    queryset = get_object_or_404(User, pk=user_pk)

    serializer = AccountSerializer(queryset, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        data = {
            "result": 1,
            "data": serializer.data
        }
    else:
        data = {
            "result": 0,
            "message": serializer.errors
        }

    return Response(data, status=status.HTTP_200_OK)

class ChangePassword(APIView):
    """
        파라미터
        user : 로그인시 전달 받은 사용자  id
        old_password
        new_password

    METHOD : POST
    """
    def get_object(self):

        try:
            user = User.objects.get(pk=self.request.data.get("user"))
            return user
        except User.DoesNotExist:
            data = {"result": -1, "message": '등록된 아이디가 없습니다.'}
            raise serializers.ValidationError(data)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            old_password = serializer.data.get("old_password")
            if not self.object.check_password(old_password):
                data = {"result": -1, "message": '기존 비밀번호가 다릅니다.'}
                return Response(data,status=status.HTTP_400_BAD_REQUEST)
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            data = {"result": 1, "message": '비밀번호가 변경되었습니다.'}
            return Response(data, status=status.HTTP_200_OK)
        else:
            dict = serializer.errors

            if 'new_password' in dict:
                data = {"result": -2, "message": "비밀번호는 8자 이상 영문/숫자가 필요합니다."}
            else:
                data = serializer.errors
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

from smtplib import SMTPException
class ResetPassword(APIView):
    """
        파라미터
        email

    METHOD : POST
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
            data = {"result": -1, "message": '사용자정보가 존재하지 않습니다.'}
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
                return Response({'result': 1, "message": '이메일 발송이 완료되었습니다.'})
            except SMTPException as e:
                data = {"result": 0, "message": e.smtp_error}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)

from rest_framework.parsers import MultiPartParser, FormParser
class ProfileView(APIView):
    """
    프로필 사진 변경
    
        파라미터
        user : 로그인시 전달받은 id
        picture : 프로필 이미지

    METHOD : POST
    """

    parser_classes = (MultiPartParser,)
    serializer_class = ProfileSerializer

    def post(self, request, *args, **kwargs):

        picture = request.data.get('picture')
        user = request.data.get('user')

        if picture is None:
            return Response({
                "result": -1,
                "message": '이미지 데이터가 없습니다.'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            profile = Profile.objects.get(user=user)

            profile_serializer = self.serializer_class(profile, data=request.data)
            if profile_serializer.is_valid():
                profile_serializer.save()
                return Response({
                    "result": 1,
                    "message": 'success',
                    "data": profile_serializer.data
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    "result": 0,
                    "message":  profile_serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except Profile.DoesNotExist:
            profile_serializer = self.serializer_class(data=request.data)
            if profile_serializer.is_valid():
                profile_serializer.save()
                return Response({
                    "result": 1,
                    "message": 'success',
                    "data": profile_serializer.data
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    "result": 0,
                    "message":  profile_serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

class FollowSet(APIView):
    """
        METHOD : POST,form-data
        파라미터
        user : 로그인시 전달받은 id
        picture : 프로파일 이미지

    METHOD : POST
    """
    def post(self, request, *args, **kwargs):
        try:
            following = User.objects.get(pk=self.request.data.get("following"))
        except User.DoesNotExist:
            data = {"result": 0, "message": 'following 등록된 아이디가 없습니다.'}
            return Response(data, status=status.HTTP_404_NOT_FOUND)

        try:
            follower = User.objects.get(pk=self.request.data.get("follower"))
        except User.DoesNotExist:
            data = {"result": 0, "message": 'follower 등록된 아이디가 없습니다.'}
            return Response(data, status=status.HTTP_404_NOT_FOUND)

        follow, created = Follow.objects.get_or_create(following=following, follower=follower)

        if created:
            data = {'result': 1, 'message': '팔로우 시작'}
        else:
            follow.delete()
            data = {'result': 0, 'message': '팔로우 취소'}
        return Response(data, status=status.HTTP_200_OK)

@api_view(['POST'])
def push_update(request):
    user = request.data.get('user')
    follow_push = request.data.get('follow_push')
    comment_push = request.data.get('comment_push')

    try:
        user = User.objects.get(pk=user)
    except User.DoesNotExist:
        data = {"result": 0, "message": '등록된 아이디가 없습니다.'}
        return Response(data, status=status.HTTP_404_NOT_FOUND)

    push, created = Push.objects.update_or_create(user=user,
                                                  defaults={
                                                      'follow_push': follow_push,
                                                      'comment_push': comment_push
                                                  })

    serializer = PushSerializer(push, data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        data = {"result": 1, "message": 'success', "data": serializer.data}
        if created:
            return Response(data, status.HTTP_201_CREATED)
        else:
            return Response(data, status.HTTP_200_OK)
    else:
        data = {"result": 1, "message": 'fail', "data": serializer.errors}
        return Response(data, status=status.HTTP_400_BAD_REQUEST)

from django.core.exceptions import ObjectDoesNotExist
class UserLogoutView(APIView):
    """
    로그인한 사용자가 로그아웃 버튼을 누르면 토큰을 삭제하고
    사용자를 로그아웃시킨다.
    """

    def logout(self, request):
        """인스턴스 메서드로 토큰을 지우는 logout 메서드 정의"""
        try:
            request.user.auth_token.delete()
        except (ObjectDoesNotExist, AttributeError):
            content = {
                "detail": "토큰이 존재하지 않습니다."
            }
           # django_logout(request)
            return Response(content, status=status.HTTP_200_OK)
            # django_logout(request)
        content = {
            "detail": "성공적으로 로그아웃되었습니다.",
        }
        return Response(content, status=status.HTTP_200_OK)

    def get(self, request):
        """
        get요청으로 logout 인스턴스 메서드를 실행.
        """
        return self.logout(request)