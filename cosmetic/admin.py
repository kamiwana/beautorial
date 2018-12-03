from django.contrib import admin
from .models import *
from .forms import *

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    form = BrandForm
    # Post 객체를 보여줄 때 출력할 필드 설정
    list_display = ('name', 'get_category_display', 'is_view')
    # 필터링 항목 설정
    # list_filter = ('company_name',)
    # 객체 검색 필드 설정
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # Post 객체를 보여줄 때 출력할 필드 설정
    list_display = ('brand_short_name', 'brand_category', 'url', 'color_code', 'is_view')
    # 필터링 항목 설정
    # 객체 검색 필드 설정
    search_fields = ('kor_name',)
    form = ProductForm