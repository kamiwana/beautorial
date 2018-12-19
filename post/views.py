from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework import mixins
from .serializers import *
from django.http import Http404
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView
from django.core.exceptions import PermissionDenied
class PostViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    """
        METHOD : POST
        파라미터
    """
    parser_classes = (MultiPartParser,)
    serializer_class = PostSerializer
    queryset = Post.objects.all()

    serializer = serializer_class(queryset, many=True)

    def list(self, request, tag=None):

        self.filter_backends = (filters.SearchFilter,)
        self.search_fields = ('context',)
        self.filter_backends = (DjangoFilterBackend,)
        self.filter_fields = ('user', 'share')

        user = self.request.user
        if tag:
            queryset = Post.objects.filter(tag_set__name__iexact=tag)
        else:
            queryset = self.filter_queryset(Post.objects.filter(share=1))

        page = request.GET.get('page')
        try:
            page = self.paginate_queryset(queryset)
        except Exception as e:
            page = []
            data = page
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": 'No more record.',
                "data": data
            })

        if page:
            serializer = PostGetSerializer(page, many=True)
            data = serializer.data
            return self.get_paginated_response(data)

        serializer = PostGetSerializer(queryset, context={'request': request}, many=True)
        return Response({
            "result": 1,
            "message": 'Post all recods.',
            "data": serializer.data
        })

    def post(self, request, *args, **kwargs):

        if request.data.get('complete_image') is None:
            data = {
                "result": -1,
                "message": 'complete_image 가 없습니다.'
            }
            return Response(data, status=status.HTTP_401_UNAUTHORIZED)

        # Copy parsed content from HTTP request
        user = self.request.user
        if not user.is_authenticated:
            # raise PermissionDenied
            data = {
                "result": -2,
                "message": "메이크업 카드를 만들려면 로그인이 필요합니다.",
            }
            return Response(data, status=status.HTTP_404_NOT_FOUND)

        data = request.data
        data['user'] = user.pk

        Post_serializer = self.get_serializer(data=data)
        if Post_serializer.is_valid():
            step_data = self.request.data.get("step")

            if step_data is None:
                Post_serializer.save()
            else:
                Post_serializer.save(step=step_data)

            data = {
                "result": 1,
                "message": "메이크업 카드 저장 성공 ",
                "data" :  Post_serializer.data
            }
            return Response(data, status=status.HTTP_201_CREATED)
        else:
            data = {
                "result": 0,
                "message": Post_serializer.errors
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self, pk, user):
        try:
            post = Post.objects.get(pk=pk)
            if user == post.user.pk:
                return post
            elif post.share == 1:
                return post
            else:
                data = {
                    "result": 0,
                    "message": "해당 메이크업카드가 없습니다."
                }
                raise serializers.ValidationError(data)
        except Post.DoesNotExist:
            data = {
                "result": 0,
                "message": "헤당 메이크업카드가 없습니다."
            }
            raise serializers.ValidationError(data)

    def retrieve(self, request, pk=None):
        user = self.request.query_params.get('user', None)
        Post = self.get_object(pk, user)
        serializer = self.get_serializer(Post)

        return Response({
            "result": 1,
            "data": serializer.data
        })

        return Response(serializer.data)

    def update(self, request, pk=None):
        user = request.user
        if not user.is_authenticated:
            data = {"result": -1, "message": '등록된 아이디가 없습니다.'}
            raise serializers.ValidationError(data)

        queryset = get_object_or_404(Post, pk=pk)

        if user.pk != queryset.user.pk:
            data = {"result": -2, "message": '작성자만 수정 가능합니다.'}
            raise serializers.ValidationError(data)

        step_data = self.request.data.get("step", None)
        serializer = PostSerializer(queryset, data=request.data, partial=True)
        if serializer.is_valid():
            if step_data is None:
                serializer.save()
            else:
                serializer.save(step=step_data)
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

    def delete(self, request, pk=None):
        user = request.user
        if not user.is_authenticated:
            data = {"result": -1, "message": '등록된 아이디가 없습니다.'}
            raise serializers.ValidationError(data)

        post = get_object_or_404(Post, pk=pk)

        if user.pk != post.user.pk:
            data = {"result": -2, "message": '작성자만 삭제 가능합니다.'}
            raise serializers.ValidationError(data)

        post.delete()
        data = {
            "result": 1,
            "message": "success"
        }
        return Response(data, status=status.HTTP_200_OK)

class PostMyList(ListAPIView):
    """
        METHOD : GET
        파라미터
    """

    def list(self, request, *args, **kwargs):

        user = request.user
        if not user.is_authenticated:
            data = {"result": -1, "message": '등록된 아이디가 없습니다.'}
            raise serializers.ValidationError(data)

        queryset = self.filter_queryset(Post.objects.filter(user=user))
        serializer = PostSerializer(queryset, context={'request': request}, many=True)

        return Response({
            "result": 0,
            "data": serializer.data
        })

class LikeSet(APIView):
    """
        METHOD : POST,form-data
        파라미터
    METHOD : POST
    """
    def post(self, request, *args, **kwargs):

        user = request.user
        if not user.is_authenticated:
            data = {"result": -1, "message": '등록된 아이디가 없습니다.'}
            raise serializers.ValidationError(data)


        post_pk = self.request.data.get('post', None)
        post = get_object_or_404(Post, pk=post_pk)
        post_like, post_like_created = post.like_set.get_or_create(user=user)

        try:
            like_count = LikeCount.objects.get(user=post.user)
        except LikeCount.DoesNotExist:
            new_like_count = LikeCount.objects.create(user=post.user)
            new_like_count.save()
            like_count = LikeCount.objects.get(user=post.user)

        if post_like_created:
            like_count.like_count = like_count.like_count + 1
            like_count.save()
            data = {'message': '좋아요', 'result': 1}
        else:
            post_like.delete()
            like_count.like_count = like_count.like_count - 1
            like_count.save()
            data = {'message': '좋아요 취소', 'result': 0}
        return Response(data, status=status.HTTP_200_OK)

class BookmarkSet(APIView):
    """
        METHOD : POST,form-data
        파라미터
    METHOD : POST
    """
    def post(self, request, *args, **kwargs):

        user = request.user
        if not user.is_authenticated:
            data = {"result": -1, "message": '등록된 아이디가 없습니다.'}
            raise serializers.ValidationError(data)

        post_pk = self.request.data.get('post', None)
        post = get_object_or_404(Post, pk=post_pk)

        post_bookmark, post_bookmark_created = post.bookmark_set.get_or_create(user=user)

        if post_bookmark_created:
            data = {'message': '북마크', 'result': 1}
        else:
            post_bookmark.delete()
            data = {'message': '북마크 취소', 'result': 0}
        return Response(data, status=status.HTTP_200_OK)

class PostDetailList(ListAPIView):

    serializer_class = PostSerializer

    def get_object(self, pk, user):
        try:
            post = Post.objects.get(pk=pk)
            if int(user) == post.user.pk:
                return post
            elif post.share == 1:
                return post
            else:
                raise Http404
        except Post.DoesNotExist:
            raise Http404

    def get_queryset(self):
        user_pk = self.request.query_params.get('user', None)
        user = get_object_or_404(User, pk=user_pk)
        queryset = Post.objects.filter(like__user=user, share=1)

        return queryset

class FollowPostList(ListAPIView):

    serializer_class = PostGetSerializer

    def get_queryset(self):
        user_pk = self.request.query_params.get('user', None)
        user = get_object_or_404(User, pk=user_pk)
        follow_set = user.get_following
        queryset = Post.objects.filter(user__user_id__in=follow_set, share=1)

        return queryset

class LikePostList(ListAPIView):

    serializer_class = PostGetSerializer

    def list(self, request, *args, **kwargs):

        user = self.request.user
        if not user.is_authenticated:
            data = {"result": -1, "message": '등록된 아이디가 없습니다.'}
            raise serializers.ValidationError(data)

        queryset = Post.objects.filter(like__user=user, share=1)

        serializer = self.serializer_class(queryset,  context={'request': request}, many=True)
        return Response({
            "result": 1,
            "message": 'Post like recods.',
            "data": serializer.data
        })


class BookmarkPostList(ListAPIView):

    serializer_class = PostGetSerializer

    def list(self, request, *args, **kwargs):
        user = self.request.user
        if not user.is_authenticated:
            data = {"result": -1, "message": '등록된 아이디가 없습니다.'}
            raise serializers.ValidationError(data)

        queryset = Post.objects.filter(bookmark__user=user, share=1)

        serializer = self.serializer_class(queryset, context={'request': request}, many=True)
        return Response({
            "result": 1,
            "message": 'Post bookmark recods.',
            "data": serializer.data
        })

class StepViewSet(viewsets.GenericViewSet,
                     mixins.ListModelMixin):
    """
        METHOD : POST
        파라미터
    """
    parser_classes = (MultiPartParser,)
    serializer_class = StepSerializer
    queryset = Step.objects.all()
    serializer = serializer_class(queryset, many=True)

    def list(self, request):

        queryset = Step.objects.filter(post=request.GET.get("post"))
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "result": 1,
            "message": 'Post all recods.',
            "data": serializer.data
        })

    def post(self, request, *args, **kwargs):
        Step_serializer = StepSerializer(self.queryset, data=request.data)
        if Step_serializer.is_valid():
            Step_serializer.save()
            return Response(Step_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(Step_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self, pk, user):
        try:
            step = Step.objects.get(pk=pk)
            return step
        except Step.DoesNotExist:
            raise Http404

    def retrieve(self, request, pk=None):
        Step = self.get_object(pk)
        serializer = PostSerializer(Post)
        return Response(serializer.data)

class CommentCreateAPIView(CreateAPIView):

    queryset = Comment.objects.all()
    def get_serializer_class(self):

        user = self.request.user
        if not user.is_authenticated:
            data = {"result": -1, "message": '등록된 아이디가 없습니다.'}
            raise serializers.ValidationError(data)

        parent_id = self.request.GET.get("parent_id", None)

        return create_comment_serializer(
                parent_id=parent_id,
                user=user
                )

class CommentListAPIView(ListAPIView):

    serializer_class = CommentSerializer

    def get_queryset(self, *args, **kwargs):
        step = self.request.GET.get("step")
        queryset = Comment.objects.filter(Q(step=step) & Q(parent=None))
        serializer = self.serializer_class(queryset, many=True)
        return Response({
            "result": 1,
            "data": serializer.data
        })

    def get_object(self, pk, user):
        try:
            comment = Comment.objects.get(pk=pk)
            return comment
        except Comment.DoesNotExist:
            raise Http404

    def retrieve(self, request, pk=None):
        comment = self.get_object(pk)
        serializer = PostSerializer(comment)
        return Response(serializer.data)

    def update(self, request, pk=None):
        queryset = get_object_or_404(Post, pk=pk)
        serializer = PostSerializer(queryset, data=request.data, partial=True)
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


    def delete(self, request, pk=None):
        comment = self.get_object(pk, self.request.user)
        comment.delete()
        data = {
            "result": 1,
            "message": "success"
        }
        return Response(data, status=status.HTTP_200_OK)


class BannerListAPIView(ListAPIView):

    serializer_class = BannerSerializer

    def list(self, *args, **kwargs):
        queryset = Banner.objects.all()
        serializer = self.serializer_class(queryset, many=True)
        return Response({
            "result": 1,
            "data": serializer.data
        })


