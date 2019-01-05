from django.contrib import admin
from .models import *

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name']

class StepInline(admin.TabularInline):
    model = Step

class LikeInline(admin.TabularInline):
    model = Like

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'create_date']
    list_display_links = ['post']

@admin.register(Bookmark)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'create_date']
    list_display_links = ['post']

    #search_fields = ('user',)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    # Post 객체를 보여줄 때 출력할 필드 설정
    list_display = ('id','title', 'user', 'step_count', 'modify_date')
    list_display_links = ['title']
    # 필터링 항목 설정
    list_filter = ('modify_date',)
    # 객체 검색 필드 설정
    search_fields = ('title', 'content')
    # slug는 title로 자동입력되도록 설정
    prepopulated_fields = {'slug': ('title',)}

    inlines = [StepInline, LikeInline]

class CommentInline(admin.TabularInline):
    model = Comment

@admin.register(Step)
class Stepdmin(admin.ModelAdmin):
    # inlines = [CosmeticInline]
    # Post 객체를 보여줄 때 출력할 필드 설정
    list_display = ('id', 'post', 'title', 'create_date')
    # 필터링 항목 설정
    list_filter = ('title',)
    # 객체 검색 필드 설정
    search_fields = ('title',)
    inlines = [CommentInline]

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['step', 'comment_content', 'user', 'create_date']
    list_display_links = ['step', 'comment_content', 'user']

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    # Post 객체를 보여줄 때 출력할 필드 설정
    list_display = ('title', 'hashtag', 'create_date', 'modify_date')



