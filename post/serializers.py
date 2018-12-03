from rest_framework import serializers
import json
from .models import *
from account.serializers import *
from cosmetic.models import *

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
    is_following = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = get_user_model()
        fields = ('id', 'user_id', 'is_following', 'profile_images', )

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

class CommentSerializer(serializers.HyperlinkedModelSerializer):

    def get_queryset(self):
        user = self.context['request'].user
        queryset = Comment.objects.filter(user=user)
        return queryset

    class Meta:
        model = Comment
        fields = [
            'comment_content',
            'comment_user_id'
        ]

class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ('kor_name',)

class StepDetailSerializer(serializers.ModelSerializer):
     #products = ProductSerializer(many=True, required=False)
     product_kor_name = serializers.SerializerMethodField()

     class Meta:
        model = StepDetail
        fields = ('id', 'contents_text', 'image', 'product', 'product_kor_name')

     def get_product_kor_name(self, obj):
        return obj.product.kor_name

class StepSerializer(serializers.HyperlinkedModelSerializer):
    step_details = StepDetailSerializer(many=True, required=False)
    comments = CommentSerializer(many=True, required=False)

    class Meta:
        model = Step
        fields = ('index', 'title', 'step_detail_count', 'step_details', 'comments')

class PostGetSerializer(serializers.ModelSerializer):

  #  steps = StepSerializer(many=True, required=False)
    user = AccountSerializer()

    class Meta:
        model = Post
        fields = ('pk', 'user',  'step_count', 'like_count', 'bookmark_count', 'comment_count',
                                   'contents_text', 'complete_image', 'create_date', 'modify_date', 'share')

from rest_framework.validators import UniqueValidator
from django.db.models.fields import SlugField
class PostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = ('pk', 'user', 'complete_image', 'step_count', 'like_count', 'bookmark_count', 'comment_count',
                  'title', 'contents_text', 'create_date', 'modify_date', 'share', 'slug')
        read_only_fields = ('pk', 'create_date', 'modify_date', 'step_count', 'slug')

    def create(self, validated_data):

        try:
            tmp_step_data = validated_data.pop('step')
            steps_data = json.loads(tmp_step_data)
            post = Post.objects.create( **validated_data)

            for step_data in steps_data:
                if step_data["stepdetail"]:

                    step = Step.objects.create(post=post,
                                               title=step_data["title"],
                                               index=step_data["index"])
                    steps_detail = step_data["stepdetail"]

                    for step_detail in steps_detail:

                        product_detail = cosmetic_models.Product.objects.get(pk=step_detail["product"])
                        StepDetail.objects.create(step=step,
                                                  product=product_detail,
                                                  contents_text=step_detail["contents_text"]
                                                  )
        except:
            post = Post.objects.create(**validated_data)

        post.tag_save()
        return post

    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            setattr(instance, field, value)
        return instance