from django.contrib import admin
from .forms import *
from django.utils.safestring import mark_safe
from django.forms import TextInput

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',)
    list_display_links = ['name']

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    form = BrandForm
    # Post 객체를 보여줄 때 출력할 필드 설정
    #list_display = ('name', 'get_category_display', 'is_view')
    list_display = ('thumnail', 'name',  'is_view')
    # 필터링 항목 설정
    # list_filter = ('company_name',)
    # 객체 검색 필드 설정
    search_fields = ('name',)
    list_display_links = ['name']

    readonly_fields = ('thumnail',)

    def thumnail(self, obj):
        if obj.logo_image:
            return mark_safe('<img src="{url}" width="{width}" height={height} />'.format(
                url=obj.logo_image.url,
                width=50,
                height=50,
            )
            )

    thumnail.short_description = '로고'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # Post 객체를 보여줄 때 출력할 필드 설정
    list_display = ('thumnail', 'brand_short_name', 'category', 'kor_name', 'eng_name', 'get_url', 'get_color_code', 'is_view')
    # 필터링 항목 설정
    # 객체 검색 필드 설정
    search_fields = ('kor_name',)
    readonly_fields = ('thumnail',)
    list_filter = ('category', 'brand',)
    form = ProductForm
    list_per_page = 20
    def get_color_code(self, obj):
        return mark_safe('<b style="background:{};">{}</b>'.format(obj.color_code, obj.color_code))

    def get_url(self, obj):
        return mark_safe('<a href="{}"  target="_blank">{}</a>'.format(obj.url, '바로가기'))

    def thumnail(self, obj):
        if obj.image:
            return mark_safe('<img src="{url}" width="{width}" height={height} />'.format(
                url=obj.image.url,
                width=50,
                height=50,
            )
            )

    def brand_short_name(self, obj):
        return obj.brand.short_name

    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '80'})},
        models.URLField:{'widget': TextInput(attrs={'size': '150'})}
    }

    thumnail.short_description = '대표이미지'
    get_color_code.short_description = '컬러'
    get_url.short_description = 'URL'
    brand_short_name.short_description = '브랜드명'


