from django.db import models
from django.urls import reverse
from django.conf import settings
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill
from .choices import *
import re
from cosmetic import models as cosmetic_models

def post_path(instance, filename):
    from random import choice
    import string
    arr = [choice(string.ascii_letters) for _ in range(8)]
    pid = ''.join(arr)
    extension = filename.split('.')[-1]
    return 'post/{}/{}.{}'.format(instance.user.pk, pid, extension)
from django.utils.text import slugify
import  itertools
# Create your models here.
class Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, verbose_name='TITLE')
    # unique=True: 특정 포스트 검색 시, pk대신에 사용하기 위해 유니크하게..
    # allow_unicode=True: 한글처리 가능
    slug = models.SlugField(unique=True, allow_unicode=True, help_text='one word for title alias')
    contents_text = models.TextField(verbose_name='CONTENT')
    # auto_now_add=True: 데이터가 생성될 때 생성시각 자동 입력
    create_date = models.DateTimeField(auto_now_add=True, verbose_name='등록일')
    # auto_now=True: 데이터가 수정될 때마다 수정시간 변경
    modify_date = models.DateTimeField(auto_now=True, verbose_name='Modify Date')
    share = models.SmallIntegerField(choices=SHARE_CHOICES, blank=True, null=True)
    tag_set = models.ManyToManyField('Tag', blank=True)
    like_user_set = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                           blank=True,
                                           related_name='like_user_set',
                                           through='Like')

    bookmark_user_set = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                           blank=True,
                                           related_name='bookmark_user_set',
                                           through='Bookmark')

    comment_user_set = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                           blank=True,
                                           related_name='comment_user_set',
                                           through='Comment')

    complete_image = ProcessedImageField(upload_to=post_path,
                                  processors=[ResizeToFill(150, 150)],
                                  format='JPEG',
                                  options={'quality': 90},
                                  blank=True,
                                  )


    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.slug = slugify(self.title, allow_unicode=True)

        max_length = Post._meta.get_field('slug').max_length
        self.slug = orig = slugify(self.title, allow_unicode=True)[:max_length]

        for x in itertools.count(1):
            if not Post.objects.filter(slug=self.slug).exists():
                break
            self.slug = "%s-%d" % (orig[:max_length - len(str(x)) - 1], x)

        super().save(force_insert, force_update, using, update_fields)

    # NOTE: content에서 tags를 추출하여, Tag 객체 가져오기, 신규 태그는 Tag instance 생성, 본인의 tag_set에 등록,
    def tag_save(self):
        tags = re.findall(r'#(\w+)\b', self.contents_text)

        if not tags:
            return

        for t in tags:
            tag, tag_created = Tag.objects.get_or_create(name=t)
            self.tag_set.add(tag)  # NOTE: ManyToManyField 에 인스턴스 추가

    class Meta:
        verbose_name = '메이크업카드'
        verbose_name_plural = '메이크업카드'
        db_table = 'my_post'
        ordering = ('-modify_date',)

    def __str__(self):
        return self.title

    def get_num_comments(self):
        cmnt_count = Comment.objects.filter(comment_for=self).count()
        return cmnt_count

    # 정의된 객체를 지칭하는 URL 반환
    def get_absolute_url(self):
        # namespace=blog, name=post_detail인 url을 reverse함수를 통해 생성
        return reverse('post:post_detail', args=(self.id, self.slug))

    # modify_date를 기준으로 이전 포스트 반환
    def get_previous_post(self):
        # get_previous_by_필드명()은 Django의 내장함수
        return self.get_previous_by_modify_date()

    # modify_date를 기준으로 다음 포스트 반환
    def get_next_post(self):
        # get_next_by_필드명()은 Django의 내장함수
        return self.get_next_by_modify_date()

    def like_count(self):
        return self.like_user_set.count()

    def bookmark_count(self):
        return self.bookmark_user_set.count()

    def step_count(self):
        return self.steps.all().count()

    def comment_count(self):
        return self.comment_user_set.count()

    def get_user_id(self):
        return self.user.get_username()

    def get_is_following(self):
        return self.user.is_follower(self.user)


class Step(models.Model):
    post = models.ForeignKey(Post, related_name='steps', on_delete=models.CASCADE)
   # user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, verbose_name='TITLE')
    index = models.SmallIntegerField()
    comment_step_set = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                           blank=True,
                                           related_name='commnet_step_set',
                                           through='Comment')

    step_detail_set = models.ManyToManyField('self',
                                           blank=True,
                                           related_name='step_detail',
                                           through='StepDetail',
                                           symmetrical=False,)

    create_date = models.DateTimeField(auto_now_add=True, verbose_name='등록일')

    class Meta:
        verbose_name = 'step'
        verbose_name_plural = 'steps'
        db_table = 'post_step'
        ordering = ['index']

    def reply_count(self):
        return self.comment_step_set.count()

    def get_step_detail(self):
        return ",".join([str(p) for p in self.step_detail_set.all()])

    def step_detail_count(self):
        return self.step_details.count()

    def __str__(self):
       return  self.post.title + self.title

    def less_comments(self):
        return Comment.objects.all().filter(step=self).order_by("-id")[:100]

def StepDetail_path(instance, filename):
    from random import choice
    import string
    arr = [choice(string.ascii_letters) for _ in range(8)]
    pid = ''.join(arr)
    extension = filename.split('.')[-1]
    return 'post/{}/{}/{}.{}'.format(instance.user.pk, instance.step.pk, pid, extension)

class StepDetail(models.Model):
  #  post = models.ForeignKey(Post, on_delete=models.CASCADE)
  #  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    step = models.ForeignKey(Step, related_name='step_details', on_delete=models.CASCADE)
    product = models.ForeignKey(cosmetic_models.Product, related_name='products', on_delete=models.CASCADE)
    contents_text = models.TextField(verbose_name='CONTENT')
    create_date = models.DateTimeField(auto_now_add=True, verbose_name='등록일')
    image = ProcessedImageField(upload_to=StepDetail_path,
                                  processors=[ResizeToFill(150, 150)],
                                  format='JPEG',
                                  options={'quality': 90},
                                  blank=True,
                                  )
    class Meta:
        verbose_name = 'step_detail'
        verbose_name_plural = 'steps_detail'
        db_table = 'post_step_detail'


    def __str__(self):
       return 'StepDetail: ' + self.step.title

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    step = models.ForeignKey(Step, on_delete=models.CASCADE, verbose_name="step", related_name="comments")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment_content = models.CharField(max_length=200, verbose_name="내용")
    create_date = models.DateTimeField(auto_now_add=True, verbose_name='등록일')

    def __str__(self):
        return self.comment_content

    def comment_user_id(self):
        return self.user.user_id

    class Meta:
        db_table = 'step_comment'
        ordering = ['-create_date']
        verbose_name = '댓글'
        verbose_name_plural = '댓글'
        
class Tag(models.Model):
    name = models.CharField(max_length=140, unique=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = '태그'
        verbose_name_plural = '태그'
        
class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    create_date = models.DateTimeField(auto_now_add=True, verbose_name='등록일')

    class Meta:
        verbose_name = 'like'
        verbose_name_plural = 'likes'
        db_table = 'post_like'

    class Meta:
        unique_together = (
            ('user', 'post')
        )

    class Meta:
        verbose_name = '좋아요'
        verbose_name_plural = '좋아요'
        
class Bookmark(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    create_date = models.DateTimeField(auto_now_add=True, verbose_name='등록일')

    class Meta:
        verbose_name = 'bookmark'
        verbose_name_plural = 'bookmark'
        db_table = 'post_bookmark'

        unique_together = (
            ('user', 'post')
        )
    class Meta:
        verbose_name = '북마크'
        verbose_name_plural = '북마크'

class Banner(models.Model):
    title = models.CharField(max_length=50)
    image = models.ImageField(blank=True, null=True, verbose_name="이미지", upload_to="banner")
    hashtag = models.CharField(max_length=10)
    modify_date = models.DateTimeField(auto_now=True, verbose_name='Modify Date')
    create_date = models.DateTimeField(auto_now_add=True, verbose_name='등록일')

    def __str__(self):
        return self.title

class LikeCount(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    like_count = models.IntegerField(default=0)

    class Meta:
        verbose_name = '배너'
        verbose_name_plural = '배너'