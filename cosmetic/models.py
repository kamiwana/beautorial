from django.db import models
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill
from django.core.validators import int_list_validator
from colorfield.fields import ColorField
from .choices import *

def brand_path(instance, filename):
    from random import choice
    import string
    arr = [choice(string.ascii_letters) for _ in range(8)]
    pid = ''.join(arr)
    extension = filename.split('.')[-1]
    return 'cosmetic/{}.{}'.format(pid, extension)

def cosmetic_path(instance, filename):
    from random import choice
    import string
    arr = [choice(string.ascii_letters) for _ in range(8)]
    pid = ''.join(arr)
    extension = filename.split('.')[-1]
    return 'cosmetic/{}.{}'.format(pid, extension)

class Brand(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='브랜드 명')
    short_name = models.CharField(max_length=10, unique=True, verbose_name='약자')
    logo_image = ProcessedImageField(upload_to=brand_path,
                                  processors=[ResizeToFill(150, 150)],
                                  format='JPEG',
                                  options={'quality': 90},
                                  blank=True,
                                  verbose_name='로고')
    category = models.CharField(max_length=255, blank=True, default='',choices=CATEGORY_CHOICES, verbose_name='카테고리')
    is_view = models.BooleanField(verbose_name='노출여부')
    create_date = models.DateTimeField(auto_now_add=True, verbose_name='Create Date')

    def __str__(self):
       return self.name

    class Meta:
        verbose_name = '메이크업 브랜드'
        verbose_name_plural = '메이크업 브랜드'

class Product(models.Model):
    image = ProcessedImageField(upload_to=cosmetic_path,
                                  processors=[ResizeToFill(150, 150)],
                                  format='JPEG',
                                  options={'quality': 90},
                                  blank=True,
                                  verbose_name='대표이미지')
    brand = models.ForeignKey(Brand,on_delete=models.CASCADE, verbose_name='브랜드명')
    category = models.SmallIntegerField(verbose_name='카테고리')
    kor_name = models.CharField(max_length=100, verbose_name='한글 제품 명')
    eng_name = models.CharField(max_length=100, verbose_name='영문 제품 명')
    url = models.URLField(max_length=250)

    color_code = ColorField(default='#FF0000', verbose_name='컬러값')
    texture = models.CharField(validators=[int_list_validator], max_length=30, blank=True, default='', verbose_name='질감')
    key = models.CharField(max_length=100, verbose_name='제품키')
    is_view = models.BooleanField(verbose_name='노출여부')
    create_date = models.DateTimeField(auto_now_add=True, verbose_name='Create Date')

    def __str__(self):
       return self.kor_name

    def brand_short_name(self):
        return self.brand.short_name

    def brand_category(self):
        return self.brand.category

    class Meta:
        verbose_name = '메이크업 제품'
        verbose_name_plural = '메이크업 제품'