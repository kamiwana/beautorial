from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from .models import *

class UserAdmin(auth_admin.UserAdmin):

    fieldsets = (
        (None, {'fields': ('email', 'password', 'username')}),
        ('개인 정보', {'fields': ('user_type', 'gender', 'birth', 'skin_color', 'face_point', 'favorite_makeup')}),
        ('권한', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
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
            'fields': ('email', 'username', 'password1', 'password2')}
        ),
    )

    list_display = ('email', 'username', 'user_type', 'user_type', 'gender', 'birth', 'is_active',  'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'groups')
    search_fields = ('username', 'email', 'user_type')
    ordering = ('email',)
    readonly_fields = ('last_login', 'date_joined',)

admin.site.register(User, UserAdmin)
