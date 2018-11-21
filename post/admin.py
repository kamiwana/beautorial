from django.contrib import admin
from django.contrib.admin.views.main import ChangeList
from .models import *
# from .forms import *

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name']

class CosmeticChangeList(ChangeList):
    def __init__(self, request, model, list_display,
                 list_display_links, list_filter, date_hierarchy,
                 search_fields, list_select_related, list_per_page,
                 list_max_show_all, list_editable, model_admin):
        super(CosmeticChangeList, self).__init__(request, model,
                                              list_display, list_display_links, list_filter,
                                              date_hierarchy, search_fields, list_select_related,
                                              list_per_page, list_max_show_all, list_editable,
                                              model_admin)

        # these need to be defined here, and not in CosmeticAdmin
        self.list_display = ['company_name', 'product_name']
        self.list_display_links = ['product_name']
        self.list_editable = ['product_name']

class StepInline(admin.TabularInline):
    model = Step

class StepInline(admin.TabularInline):
    model = Step


class LikeInline(admin.TabularInline):
    model = Like

class PostAdmin(admin.ModelAdmin):
    # Post 객체를 보여줄 때 출력할 필드 설정
    list_display = ('id', 'title', 'step_count', 'modify_date')
    # 필터링 항목 설정
    list_filter = ('modify_date',)
    # 객체 검색 필드 설정
    search_fields = ('title', 'content')
    # slug는 title로 자동입력되도록 설정
    prepopulated_fields = {'slug': ('title',)}

    inlines = [LikeInline, StepInline]

class CosmeticAdmin(admin.ModelAdmin):
    # Post 객체를 보여줄 때 출력할 필드 설정
    list_display = ('company_name', 'product_name', 'color_code', 'create_date')
    # 필터링 항목 설정
    list_filter = ('company_name',)
    # 객체 검색 필드 설정
    search_fields = ('product_name', 'product_name')

class CommentInline(admin.TabularInline):
    model = Comment

class Stepdmin(admin.ModelAdmin):
    # inlines = [CosmeticInline]
    # Post 객체를 보여줄 때 출력할 필드 설정
    list_display = ('post', 'title', 'create_date')
    # 필터링 항목 설정
    list_filter = ('title',)
    # 객체 검색 필드 설정
    search_fields = ('title',)

    inlines = [CommentInline]

#class CosmeticInline(admin.TabularInline):
    #    model = StepDetail.cosmetic_set.through
    #fields = ['product_name']
    #readonly_fields = ['product_name']

    #def product_name(self, instance):
    #    return instance.cosmetic.product_name
    #product_name.short_description = 'product name'

class StepDetailadmin(admin.ModelAdmin):
  list_display = ('step', 'create_date')

 # inlines = (
      #      CosmeticInline,
  # )
  exclude = ('cosmetic_set',)
  #  def get_changelist(self, request, **kwargs):
  #      return CosmeticChangeList
  #form = CosmeticChangeListForm
  # def get_changelist_form(self, request, **kwargs):
#     return CosmeticChangeListForm

admin.site.register(Post, PostAdmin)
admin.site.register(Step, Stepdmin)
admin.site.register(StepDetail, StepDetailadmin)
admin.site.register(Cosmetic, CosmeticAdmin)
