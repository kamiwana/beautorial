from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from .models import *
from .forms import *

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'profile'

#@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['id',  'user']
    list_display_links = ['user']
#    inlines = [FollowInline, ]

@admin.register(Push)
class PushAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'user',  'follow_push',  'comment_push']
    list_display_links = ['user']
    list_filter = ('follow_push', 'comment_push')
    search_fields = ('user__user_id',)

class FollowInline(admin.TabularInline):
    model = Follow
    fk_name = 'following'

class PushInline(admin.TabularInline):
    model = Push

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ['get_following', 'get_follower', 'follow_time']
    list_display_links = ['get_following', 'get_follower', 'follow_time']

    #search_fields = ('get_from_user_id', 'get_to_user_id')

    def get_following(self, instance):
        return instance.following.user_id

    def get_follower(self, instance):
        return instance.follower.user_id

class UserAdmin(auth_admin.UserAdmin):
    form = UserChangeForm

    fieldsets = (
        (None, {'fields': ('email', 'password', 'user_id')}),
        ('개인 정보', {'fields': ('user_type', 'gender', 'birth', 'skin_color', 'face_point', 'favorite_makeup')}),
        ('권한', {'fields': ('is_active','is_block', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('date_joined', 'last_login')}),
    )
    limited_fieldsets = (
        (None, {'fields': ('email',)}),
        ('Personal info', {'fields': ('user_name','user_type', 'gender', 'birth', 'skin_color', 'face_point', 'favorite_makeup')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'user_id', 'password1', 'password2')}
        ),
    )

    list_display = ('id', 'user_id', 'email', 'user_type', 'gender', 'birth', 'is_active','is_block',  'date_joined')
    list_filter = ('is_block', 'is_active')
    list_display_links = ['user_id']
    search_fields = ('user_id', 'email', 'user_type')
    ordering = ('-date_joined',)
    readonly_fields = ('last_login', 'date_joined',)
    inlines = (ProfileInline, PushInline, FollowInline, )

admin.site.register(User, UserAdmin)

