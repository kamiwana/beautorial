from django.db import models
from django.core.validators import int_list_validator
from colorfield.fields import ColorField
from .choices import *
from django.core.files.storage import FileSystemStorage

class OverwriteStorage(FileSystemStorage):
    def _save(self, name, content):
        if self.exists(name):
            self.delete(name)
        return super(OverwriteStorage, self)._save(name, content)

    def get_available_name(self, name, max_length=None):
        return name

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

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='카테고리 명')
    create_date = models.DateTimeField(auto_now_add=True, verbose_name='Create Date')

    def __str__(self):
       return self.name

    class Meta:
       verbose_name = '1. 카테고리'
       verbose_name_plural = '1. 카테고리'

class Brand(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='브랜드 명')
    short_name = models.CharField(max_length=10, unique=True, verbose_name='약자')
    logo_image = models.ImageField(upload_to=brand_path, blank=True, verbose_name='로고', storage=OverwriteStorage())
    is_view = models.BooleanField(verbose_name='노출여부')
    create_date = models.DateTimeField(auto_now_add=True, verbose_name='Create Date')

    def __str__(self):
       return self.name

    class Meta:
        verbose_name = '2. 메이크업 브랜드'
        verbose_name_plural = '2. 메이크업 브랜드'

class Product(models.Model):
    image = models.ImageField(upload_to=cosmetic_path, blank=True, verbose_name='대표이미지', storage=OverwriteStorage())
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, verbose_name='브랜드명')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='카테고리')
    kor_name = models.CharField(max_length=100, verbose_name='한글 제품 명')
    eng_name = models.CharField(max_length=100, verbose_name='영문 제품 명')
    url = models.URLField(max_length=250)

    color_code = ColorField(default='#FF0000', verbose_name='컬러값')
    texture = models.CharField(validators=[int_list_validator], max_length=30, blank=True, default=1, verbose_name='질감')
    key = models.CharField(max_length=100, verbose_name='제품키', help_text='제품회사-제품명-카테고리-얼굴위치-컬러값')
    is_view = models.BooleanField(verbose_name='노출여부')
    create_date = models.DateTimeField(auto_now_add=True, verbose_name='Create Date')

    def __str__(self):
       return self.kor_name

    class Meta:
        verbose_name = '3. 메이크업 제품'
        verbose_name_plural = '3. 메이크업 제품'
