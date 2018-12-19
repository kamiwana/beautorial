from rest_framework import serializers
import json
from .models import *
from account.serializers import *
from django.db.models import Q

User = get_user_model()


class LikeCountSerializer(serializers.ModelSerializer):
    class Meta:
        model = LikeCount
        fields = ('like_count')


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('picture',)

class FollowSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Follow
        fields = '__all__'

class AccountSerializer(serializers.ModelSerializer):
    profile_images = serializers.SerializerMethodField(read_only=True)


    class Meta:
        model = User
        fields = ('id', 'user_id',  'profile_images', )

    def get_profile_images(self, obj):
        try:
            return obj.userprofile.picture.url
        except:
            return None

class SubcommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ('id', 'comment_content', 'parent')


class CommentChildSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = [
            'id',
            'comment_user_id',
            'parent',
            'comment_content',

        ]

class RecursiveSerializer(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class CommentSerializer(serializers.ModelSerializer):
    #replies = SubcommentSerializer(many=True, read_only=True)

    replies = RecursiveSerializer(many=True, read_only=True)

    def get_queryset(self):
        user = self.context['request'].user
        queryset = Comment.objects.filter(parent=None)
        return queryset

    class Meta:
        model = Comment
        fields = [
            'id',
            'comment_user_id',
            'parent',
            'comment_content',
            'replies',
        ]

        read_only_fields = [
            'replies',
        ]

class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = cosmetic_model.Product
        fields = ('kor_name',)


class StepSerializer(serializers.HyperlinkedModelSerializer):
    products = ProductSerializer(many=True, required=False)
    comments = serializers.SerializerMethodField()
    product_kor_name = serializers.SerializerMethodField()
    product_eng_name = serializers.SerializerMethodField()
    company_name = serializers.SerializerMethodField()
    product_image = serializers.SerializerMethodField()
    color_code = serializers.SerializerMethodField()
    texture = serializers.SerializerMethodField()
    product_url = serializers.SerializerMethodField()

    class Meta:
        model = Step
        fields = ('id','index', 'title', 'contents_text', 'products','company_name', 'product_kor_name', 'product_eng_name',
                  'product_image','color_code','texture','product_url', 'comments')

    def get_comments(self, obj):
       comments = Comment.objects.filter(Q(step=obj.id) & Q(parent=None))
       return CommentSerializer(comments, many=True).data

    def get_product_kor_name(self, obj):
        return obj.product.kor_name

    def get_product_eng_name(self, obj):
        return obj.product.eng_name

    def get_company_name(self, obj):
        return obj.product.brand.name

    def get_product_image(self, obj):

         try:
             request = self.context['request']
             return request.build_absolute_uri(obj.product.image.url)
         except:
             return None

    def get_color_code(self, obj):
        return obj.product.color_code

    def get_texture(self, obj):
        return obj.product.texture

    def get_product_url(self, obj):
        return obj.product.url

class PostGetSerializer(serializers.HyperlinkedModelSerializer):
    is_following = serializers.SerializerMethodField()
    profile_images = serializers.SerializerMethodField()


    class Meta:
        model = Post
        fields = ('pk', 'get_user_pk', 'get_user_id', 'profile_images', 'is_following', 'step_count', 'like_count', 'bookmark_count', 'comment_count',
                                   'contents_text', 'complete_image', 'create_date', 'modify_date', 'share')

    def get_is_following(self, obj):
        user = self.context['request'].user
        if user is None or user == obj.user:
            return 0
        else:
            if user.is_following(obj.user):
                return 1
            else:
                return 0

    def get_profile_images(self, obj):
            request = self.context['request']
            try:
                return request.build_absolute_uri(obj.user.userprofile.picture.url)
            except:
                return None

class PostSerializer(serializers.ModelSerializer):
    steps = StepSerializer(many=True, required=False)

    class Meta:
        model = Post
        fields = ('pk', 'user', 'complete_image', 'step_count', 'like_count', 'bookmark_count', 'comment_count',
                  'title', 'contents_text', 'create_date', 'modify_date', 'share', 'slug', 'steps')
        read_only_fields = ('pk', 'create_date', 'modify_date', 'step_count', 'slug', 'steps')

    def create(self, validated_data):

        snapshot_texture = self.context.get('view').request.FILES.getlist('snapshot_texture')
        tmp_step_data = validated_data.pop('step',None)

        if len(snapshot_texture) == 0:
            data = {"result": 0, "message": "snapshot_texture가 없습니다."}
            raise serializers.ValidationError(data)

        if tmp_step_data is None:
            data = {"result": 0, "message": "step이 없습니다."}
            raise serializers.ValidationError(data)

        try:
            steps_data = json.loads(tmp_step_data)
        except Exception as e:
            data = {
                "result": 0,
                "message": str(e)
            }
            raise serializers.ValidationError(data)

        if len(snapshot_texture) != len(steps_data):
            data = {"result": 0, "message": "스냅샷 이미지 갯수와 step 갯수가 맞지 않습니다."}
            raise serializers.ValidationError(data)

        post = Post.objects.create(**validated_data)

        try:
            for index, step_data in enumerate(steps_data, start=0):
                product = cosmetic_model.Product.objects.get(pk=step_data["product"])
                Step.objects.create(post=post,
                                       title=step_data["title"],
                                       index=step_data["index"],
                                       object_index=step_data["object_index"],
                                       contents_text=step_data["contents_text"],
                                       product=product,
                                       snapshot_texture=snapshot_texture[index]
                                       )
            post.tag_save()
            return post
        except Exception as e:
            data = {
                "result": 0,
                "message": str(e)
            }
            raise serializers.ValidationError(data)

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.contents_text = validated_data.get('contents_text', instance.contents_text)
        instance.share = validated_data.get('share', instance.share)
        instance.save()
        instance.tag_set.clear()
        instance.tag_save()

        try:
            tmp_step_data = validated_data.get('step')
            steps_data = json.loads(tmp_step_data)
            for step_data in steps_data:
                product = cosmetic_model.Product.objects.get(pk=step_data["product"])
                Step.objects.filter(pk=step_data["pk"]).update(
                    title=step_data["title"],
                    index=step_data["index"],
                    object_index=step_data["object_index"],
                    contents_text=step_data["contents_text"],
                    product=product
                )
        except:
            return instance
        return instance
def create_comment_serializer(parent_id=None, user=None):
    class CommentCreateSerializer(serializers.ModelSerializer):
        class Meta:
            model = Comment
            fields = [
                'id',
                'post',
                'step',
                'parent',
                'comment_content',
                'create_date',

            ]
        def __init__(self, *args, **kwargs):
            self.parent_obj = None
            if parent_id:
                parent_qs = Comment.objects.filter(id=parent_id)
                if parent_qs.exists() and parent_qs.count() == 1:
                    self.parent_obj = parent_qs.first()
            return super(CommentCreateSerializer, self).__init__(*args, **kwargs)

        def create(self, validated_data):
            content = validated_data.get("comment_content")
            post = validated_data.get("post")
            step = validated_data.get("step")
            parent_obj = self.parent_obj
            comment = Comment.objects.create(
                post=post,
                user=user,
                step=step,
                comment_content=content,
                parent=parent_obj,
                    )

            comment_count, comment_count_created = CommentCount.objects.get_or_create(post=post)

            if not comment_count_created:
                comment_count = comment_count.count + 1
                CommentCount.objects.filter(post=post).update(
                    count=comment_count
                )

            return comment

    return CommentCreateSerializer

from rest_framework.serializers import (
    HyperlinkedIdentityField,
    SerializerMethodField,
    )

class CommentListSerializer(serializers.ModelSerializer):
    url = HyperlinkedIdentityField(
        view_name='comments-api:thread')

    class Meta:
        model = Comment
        fields = [
            'url',
            'id',
            # 'content_type',
            # 'object_id',
            # 'parent',
            'comment_content',
            'create_date',
        ]

class BannerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Banner
        fields = ('title', 'image', 'hashtag', 'modify_date')
