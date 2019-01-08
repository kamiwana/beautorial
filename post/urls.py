from django.conf.urls import url
from .views import *

app_name = "posts"

urlpatterns = [
  url(r'^step/$', StepViewSet.as_view({'get': 'list'})),
  url(r'^like/$', LikeSet.as_view()),
  url(r'^bookmark/$', BookmarkSet.as_view()),
  url(r'^follow-post-list/$', FollowPostList.as_view()),
  url(r'^like-post-list/$', LikePostList.as_view()),
  url(r'^bookmark-post-list/$', BookmarkPostList.as_view()),
  url(r'^explore/tags/(?P<tag>\w+)/$', PostViewSet.as_view({'get': 'list'}), name="tag_list"),
  url(r'^latest-list/(?P<cnt>\w+)/$', PostViewSet.as_view({'get': 'list'}), name="latest_list"),
  url(r'^my-beauty-card/(?P<beauty>\w+)/$', PostViewSet.as_view({'get': 'list'}), name="beauty_list"),
  url(r'^$', PostViewSet.as_view({'get': 'list'}), name='post_list'),
  url(r'^(?P<pk>\w+)/$', PostViewSet.as_view({'get': 'retrieve'}), name='post_detail'),
  url(r'^update/(?P<pk>\w+)/$', PostViewSet.as_view({'post': 'update'}), name='post_update'),
  url(r'^delete/(?P<pk>\w+)/$', PostViewSet.as_view({'get': 'delete'}), name='post_delete'),
  url(r'^my-makeupcard-list/$', PostMyList.as_view()),
  url(r'^step/$', StepViewSet.as_view({'get': 'list'}), name='step_list'),
  url(r'^step/update/(?P<pk>\w+)/$', StepViewSet.as_view({'post': 'update'}), name='step_update'),
  url(r'^step/delete/(?P<pk>\w+)/$', StepViewSet.as_view({'get': 'delete'}), name='step_delete'),
  url(r'^comments/create/$', CommentCreateAPIView.as_view(), name='create'),
  url(r'^comments/delete/(?P<pk>\d+)/$', CommentViewSet.as_view({'get': 'delete'}), name='comment_delete'),
  url(r'^comments/update/(?P<pk>\d+)/$', CommentViewSet.as_view({'post': 'update'}), name='comment_update'),
  url(r'^comments/list/$', CommentViewSet.as_view({'get': 'list'}), name='comments_list'),
  url(r'^banners/list/$', BannerListAPIView.as_view(), name='banner_list'),
  url(r'^make-tag/list/$', MakeTagListAPIView.as_view(), name='make_tag_list')
]