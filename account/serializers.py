from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
import django.contrib.auth.password_validation as validators
from .models import *
from post import models as post_models

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('user', 'picture',)


class PushSerializer(serializers.ModelSerializer):
    class Meta:
        model = Push
        fields = ('follow_push', 'comment_push')


class AccountSerializer(serializers.HyperlinkedModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    profile = ProfileSerializer(source='userprofile', required=False)
    push = PushSerializer(source='userpush', required=False)

    class Meta:
        model = get_user_model()
        fields = (
            'id', 'email', 'password', 'email', 'user_id', 'gender', 'birth', 'skin_color', 'face_point', 'favorite_makeup',
                            'user_type', 'date_joined', 'follower_count', 'following_count', 'profile', 'push', 'like_count')
        extra_kwargs = {'password': {'write_only': True, 'min_length': 8}}
        read_only_fields = ['profile', 'push', 'like_count']

    def validate_password(self, value):
        try:
            validators.validate_password(value)
        except ValidationError as exc:
            raise serializers.ValidationError(str(exc))
        return value

    def create(self, validated_data):

        user = super().create(validated_data)
        user.set_password(validated_data['password'])

        # create push
        push = Push.objects.create(
            user=user,
            follow_push=0,
            comment_push=0
        )
        # create likecount
        like_count = post_models.LikeCount.objects.create(
            user=user
        )

        like_count.save()
        push.save()
        user.save()
        return user

class AccountViewSerializer(serializers.HyperlinkedModelSerializer):
    profile_images = serializers.SerializerMethodField(read_only=True)
    is_following = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = get_user_model()
        fields = ('id', 'user_id',  'profile_images', 'like_count', 'follower_count', 'following_count', 'is_following',
                   'skin_color', 'face_point', 'favorite_makeup', )

    def get_profile_images(self, obj):
        try:
            return obj.userprofile.picture.url
        except:
            return None

    def get_is_following(self, obj):
      #  user = self.context['request'].user
      #
      #  if user is None:
      #      return 0
      #  else:
      #   return user.is_following(obj)
        return 0

class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value

class FollowSerializer(serializers.Serializer):

    class Meta:
        model = Follow
        fields = ('follower', 'following', 'follow_time')
        read_only_fields = ['follow_time']

class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
